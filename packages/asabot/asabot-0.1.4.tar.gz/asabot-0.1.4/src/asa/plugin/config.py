from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple

import tomllib

from asa.core.logging import get_logger

logger = get_logger("asa.plugin.config")


@dataclass
class ConfigDiff:
    """插件配置差异结构，用于驱动插件热重载。

    - added:   新增的插件 target -> 配置
    - removed: 被删除的插件 target -> 旧配置
    - updated: 内容发生变化的插件 target -> (旧配置, 新配置)
    """

    added: Dict[str, Dict[str, Any]]
    removed: Dict[str, Dict[str, Any]]
    updated: Dict[str, Tuple[Dict[str, Any], Dict[str, Any]]]

    def is_empty(self) -> bool:
        return not (self.added or self.removed or self.updated)


class PluginConfigManager:
    """插件配置管理器。

    负责：
        - 读取 / 解析 plugins.toml
        - 提供当前启用插件列表和单个插件配置
        - 提供 reload() 计算配置差异，用于热重载
        - 可选：基于文件 mtime 的简单 Watch 机制

    TOML 结构约定：

        [plugins]

          [plugins."plugins.weather"]
          enabled = true
          api_key = "your_key"

          [plugins."plugins.admin:AdminPlugin"]
          enabled = true
          admin_users = [123456789]

    其中 key（如 "plugins.weather" / "plugins.admin:AdminPlugin"）
    对应插件 target，与 Bot.load()/PluginManager.load() 的 spec 保持一致。
    """

    def __init__(self, fp: str = "plugins.toml", auto_scan: bool = True) -> None:
        self.fp: str = fp
        self.cfg: Dict[str, Dict[str, Any]] = {}
        self.enabled_plugins: List[str] = []
        self._last_raw_cfg: Dict[str, Dict[str, Any]] = {}
        self._listeners: List[Callable[[ConfigDiff], None]] = []
        self._watch_thread: Optional[threading.Thread] = None
        self._watch_stop_event: Optional[threading.Event] = None
        self._last_mtime: float = 0.0

        self._load(initial=True, auto_scan=auto_scan)

    # ===== 公开属性访问 =====

    def __getitem__(self, item: str) -> Dict[str, Any]:
        return self.cfg[item]

    # ===== 基础加载与状态维护 =====

    def _load(self, *, initial: bool, auto_scan: bool) -> None:
        """读取配置文件并更新内部状态。"""
        try:
            path = Path(self.fp)
            if not path.exists():
                self.cfg = {}
                self._last_raw_cfg = {}
                self.enabled_plugins = []
                if initial:
                    logger.info(f"{self.fp} 不存在，跳过基于配置文件的插件加载")
                return

            self._last_mtime = path.stat().st_mtime

            with path.open("rb") as f:
                data = tomllib.load(f)

            raw_plugins = data.get("plugins", {}) or {}
            # 确保内部结构是普通 dict[str, dict]
            normalized: Dict[str, Dict[str, Any]] = {}
            for name, cfg in raw_plugins.items():
                if isinstance(cfg, Mapping):
                    normalized[name] = dict(cfg)
                else:
                    logger.warning(f"插件配置 {name!r} 不是映射类型，已忽略")

            self.cfg = normalized
            self._last_raw_cfg = dict(normalized)

            if auto_scan:
                self.enabled_plugins = [
                    name for name, cfg in self.cfg.items()
                    if cfg.get("enabled", True)
                ]
            else:
                self.enabled_plugins = []

            if initial and self.cfg:
                logger.info(
                    f"从 {self.fp} 加载插件配置，共 {len(self.cfg)} 个，启用 {len(self.enabled_plugins)} 个"
                )
        except Exception:
            logger.exception("加载插件配置文件失败")
            if initial:
                # 初次失败时，保持空配置
                self.cfg = {}
                self._last_raw_cfg = {}
                self.enabled_plugins = []

    # ===== 查询接口 =====

    def is_enabled(self, plugin_name: str) -> bool:
        cfg = self.cfg.get(plugin_name, {})
        return cfg.get("enabled", True)

    def get_scanned(self) -> List[str]:
        """返回 auto_scan 阶段扫描到的启用插件列表。"""
        return list(self.enabled_plugins)

    def get_plugin_cfg(self, plugin: str) -> Dict[str, Any]:
        """返回某个插件的配置（不含 enabled 字段）。"""
        raw = self.cfg.get(plugin, {}) or {}
        return {k: v for k, v in raw.items() if k != "enabled"}

    # ===== 配置重载与 Diff =====

    def _calc_diff(
        self,
        old: Mapping[str, Dict[str, Any]],
        new: Mapping[str, Dict[str, Any]],
    ) -> ConfigDiff:
        old_keys = set(old.keys())
        new_keys = set(new.keys())

        added_keys = new_keys - old_keys
        removed_keys = old_keys - new_keys
        maybe_updated_keys = old_keys & new_keys

        added: Dict[str, Dict[str, Any]] = {}
        removed: Dict[str, Dict[str, Any]] = {}
        updated: Dict[str, Tuple[Dict[str, Any], Dict[str, Any]]] = {}

        for k in added_keys:
            added[k] = dict(new[k])
        for k in removed_keys:
            removed[k] = dict(old[k])
        for k in maybe_updated_keys:
            old_cfg = old[k]
            new_cfg = new[k]
            if dict(old_cfg) != dict(new_cfg):
                updated[k] = (dict(old_cfg), dict(new_cfg))

        return ConfigDiff(added=added, removed=removed, updated=updated)

    def reload(self) -> Optional[ConfigDiff]:
        """重新加载配置文件，返回与上一次的差异。

        如果文件不存在或加载失败，将返回 None。
        如果没有任何变化，返回 ConfigDiff 且 diff.is_empty() 为 True。
        """
        try:
            path = Path(self.fp)
            if not path.exists():
                if self._last_raw_cfg:
                    # 由有配置变成无配置：认为全部 removed
                    diff = ConfigDiff(
                        added={},
                        removed=dict(self._last_raw_cfg),
                        updated={},
                    )
                    self.cfg = {}
                    self._last_raw_cfg = {}
                    self.enabled_plugins = []
                    self._notify_listeners(diff)
                    return diff
                return None

            with path.open("rb") as f:
                data = tomllib.load(f)

            raw_plugins = data.get("plugins", {}) or {}
            normalized: Dict[str, Dict[str, Any]] = {}
            for name, cfg in raw_plugins.items():
                if isinstance(cfg, Mapping):
                    normalized[name] = dict(cfg)
                else:
                    logger.warning(f"插件配置 {name!r} 不是映射类型，已忽略")

            new_cfg = normalized
            diff = self._calc_diff(self._last_raw_cfg, new_cfg)

            # 更新内部状态
            self.cfg = new_cfg
            self._last_raw_cfg = dict(new_cfg)
            self.enabled_plugins = [
                name for name, cfg in self.cfg.items()
                if cfg.get("enabled", True)
            ]
            self._last_mtime = path.stat().st_mtime

            self._notify_listeners(diff)
            return diff
        except Exception:
            logger.exception("重载插件配置文件失败")
            return None

    # ===== 监听与 Watch =====

    def add_listener(self, callback: Callable[[ConfigDiff], None]) -> None:
        """添加配置变更监听器。

        callback 会在 reload() 成功后被调用，即使 diff 为空。
        """
        self._listeners.append(callback)

    def _notify_listeners(self, diff: ConfigDiff) -> None:
        for cb in list(self._listeners):
            try:
                cb(diff)
            except Exception:
                logger.exception("插件配置监听回调执行失败")

    def start_watch(self, interval: float = 1.0) -> None:
        """启动一个简单的后台线程按 mtime 轮询配置文件，用于开发期热重载。

        生产环境下建议交给应用层控制（例如显式调用 reload()）。
        """
        if self._watch_thread and self._watch_thread.is_alive():
            return

        stop_event = threading.Event()
        self._watch_stop_event = stop_event

        def _loop() -> None:
            path = Path(self.fp)
            while not stop_event.is_set():
                try:
                    if path.exists():
                        mtime = path.stat().st_mtime
                        if mtime > self._last_mtime:
                            self.reload()
                    else:
                        # 文件被删除
                        if self._last_raw_cfg:
                            self.reload()
                except Exception:
                    logger.exception("轮询插件配置文件时出错")
                stop_event.wait(interval)

        t = threading.Thread(target=_loop, name="PluginConfigWatch", daemon=True)
        self._watch_thread = t
        t.start()

    def stop_watch(self) -> None:
        """停止后台 Watch 线程。"""
        if self._watch_stop_event is not None:
            self._watch_stop_event.set()
        if self._watch_thread is not None and self._watch_thread.is_alive():
            self._watch_thread.join(timeout=1.0)


__all__ = ["PluginConfigManager", "ConfigDiff"]

