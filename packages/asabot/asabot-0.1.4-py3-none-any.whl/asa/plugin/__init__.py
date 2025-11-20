from __future__ import annotations

import importlib
import inspect
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Union

from typing import TYPE_CHECKING

from .config import ConfigDiff, PluginConfigManager
from .type import PluginPath, PluginConfig, PluginSpec
from ..core.logging import get_logger

logger = get_logger("asa.plugin")

if TYPE_CHECKING:
    from ..core.bot import Bot


@dataclass
class PluginInfo:
    """单个插件的运行时信息。"""

    plugin_id: str                 # target 字符串（例如 "plugins.weather"）
    target: str                    # 同上，保留字段，方便以后支持 alias
    plugin_type: str               # "module" or "class"
    module_name: str               # 不带类名的部分，例如 "plugins.weather"
    class_name: Optional[str] = None

    config: Optional[Dict[str, Any]] = None  # 有效配置（已去掉 enabled）
    instance: Any = None                    # 模块对象或类实例
    handler_sources: Optional[Set[str]] = None  # 注册到 EventHandler 时用的 source 集
    file_path: Optional[str] = None         # 插件模块文件路径
    mtime: float = 0.0                      # 文件修改时间（为将来代码热重载准备）

    origin: str = "manual"                  # "manual" / "config"
    origin_detail: Optional[Dict[str, Any]] = None  # 比如 {"config_file": "plugins.toml"}
    enabled: bool = True


class PluginManager:
    """插件管理器。

    负责：
        - 统一管理插件的加载 / 卸载 / 重载
        - 维护插件运行时信息（PluginInfo）
        - 通过 EventHandler 的 sources 机制按来源卸载 handler
        - 与 PluginConfigManager 协作，实现基于配置文件的热重载
    """

    def __init__(
        self,
        bot: "Bot",
        config_manager: Optional[PluginConfigManager] = None,
    ) -> None:
        self.bot = bot
        self.config_manager = config_manager
        self.plugins: Dict[str, PluginInfo] = {}
        self.file_to_plugins: Dict[str, Set[str]] = {}

        self.handler = self.bot.handler

        # 基于配置文件的插件加载与热重载
        if self.config_manager is not None:
            self.load_from_config_manager(self.config_manager)
            self.config_manager.add_listener(self.apply_config_diff)

    # ===== 对外统一加载入口 =====

    def load(
        self,
        spec: Union[PluginSpec, PluginPath, Iterable[PluginSpec]],
        config: Optional[PluginConfig] = None,
        *,
        origin: str = "manual",
        origin_detail: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """加载插件的统一入口。

        支持以下调用方式：
         - manager.load("plugins.weather")
         - manager.load("plugins.weather", {"key": "value"})
         - manager.load(("plugins.weather", {"key": "val"}))
         - manager.load(["plugins.weather", "plugins.admin"])
         - manager.load([("plugins.weather", conf), ...])
        """
        from collections.abc import Iterable as IterableABC

        try:
            if isinstance(spec, str):
                return self._load_one(
                    target=spec,
                    config=config,
                    origin=origin,
                    origin_detail=origin_detail,
                )
            if isinstance(spec, tuple) and len(spec) == 2 and isinstance(spec[0], str):
                target, cfg = spec
                return self._load_one(
                    target=target,
                    config=cfg,
                    origin=origin,
                    origin_detail=origin_detail,
                )
            if isinstance(spec, IterableABC):
                loaded: List[Any] = []
                for item in spec:
                    if isinstance(item, str):
                        target, cfg = item, None
                    else:
                        target, cfg = item
                    try:
                        loaded.append(
                            self._load_one(
                                target=target,
                                config=cfg,
                                origin=origin,
                                origin_detail=origin_detail,
                            )
                        )
                    except Exception:
                        logger.exception("插件加载失败: %r", target)
                return loaded

            # 兜底：尝试将 spec 转成字符串 target
            target = str(spec)
            return self._load_one(
                target=target,
                config=config,
                origin=origin,
                origin_detail=origin_detail,
            )
        except Exception as e:
            logger.exception(f"error in loading: {spec} | {e}")

    def _register_handlers_from_object(self, obj: Any, **attrs) -> None:
        """扫描并注册对象（模块或实例）中的所有处理器。"""
        for _, member in inspect.getmembers(obj):
            if (inspect.isfunction(member) or inspect.ismethod(member)) and hasattr(member, "_condition"):
                condition = getattr(member, "_condition")
                self.handler.register_handler(member, condition, **condition.attrs, **attrs)

    # ===== 基于配置文件的加载 / 重载 =====

    def load_from_config_manager(self, cfg_mgr: PluginConfigManager) -> None:
        """根据 PluginConfigManager 当前状态加载所有已启用插件。"""
        for target in cfg_mgr.get_scanned():
            cfg = cfg_mgr.get_plugin_cfg(target)
            self._load_one(
                target=target,
                config=cfg,
                origin="config",
                origin_detail={"config_file": cfg_mgr.fp},
            )

    def reload_all_from_config(self) -> Optional[ConfigDiff]:
        """显式触发一次配置重载，并根据差异调整插件。

        返回 ConfigDiff；当未绑定 config_manager 或重载失败时返回 None。
        """
        if self.config_manager is None:
            return None
        diff = self.config_manager.reload()
        if diff is None:
            return None
        self.apply_config_diff(diff)
        return diff

    def apply_config_diff(self, diff: ConfigDiff) -> None:
        """根据配置差异对插件执行增删改操作。"""
        # 1. 先卸载 removed
        for target in diff.removed.keys():
            self.unload(target)

        # 2. 处理 updated
        for target, (old_cfg, new_cfg) in diff.updated.items():
            old_enabled = old_cfg.get("enabled", True)
            new_enabled = new_cfg.get("enabled", True)
            logger.info(f"DEBUG reload cadif | {target} {old_enabled} {new_enabled}")
            if old_enabled and not new_enabled:
                # 从启用变为禁用
                self.unload(target)
            elif (not old_enabled) and new_enabled:
                # 从禁用变为启用
                cfg = {k: v for k, v in new_cfg.items() if k != "enabled"}
                self._load_one(
                    target=target,
                    config=cfg,
                    origin="config",
                    origin_detail={"config_file": self.config_manager.fp} if self.config_manager else None,
                )
            elif new_enabled:
                # 配置变更但仍启用 → 重载
                cfg = {k: v for k, v in new_cfg.items() if k != "enabled"}
                self.reload(target, override_config=cfg)

        # 3. 最后加载 added
        for target, new_cfg in diff.added.items():
            if not new_cfg.get("enabled", True):
                continue
            cfg = {k: v for k, v in new_cfg.items() if k != "enabled"}
            self._load_one(
                target=target,
                config=cfg,
                origin="config",
                origin_detail={"config_file": self.config_manager.fp} if self.config_manager else None,
            )

    # ===== 卸载 / 重载 =====

    def unload(self, plugin_id: str) -> bool:
        """卸载单个插件，清理 handler 与模块缓存。"""
        info = self.plugins.get(plugin_id)
        if info is None:
            return False

        # 1. 从 EventHandler 卸载 handler
        if info.handler_sources:
            for src in info.handler_sources:
                self.handler.unregister_handler_by_source(src)
        else:
            # 兜底：按模块名卸载
            self.handler.unregister_handler_by_source(info.module_name)

        # 2. 调用插件自定义的清理逻辑（可选）
        try:
            cleanup = None
            if hasattr(info.instance, "__teardown__"):
                cleanup = getattr(info.instance, "__teardown__")
            elif hasattr(info.instance, "__unload__"):
                cleanup = getattr(info.instance, "__unload__")
            if callable(cleanup):
                cleanup()
        except Exception:
            logger.exception("插件卸载清理失败: %s", plugin_id)

        # 3. 清理模块缓存，方便后续热重载
        try:
            if info.module_name in sys.modules:
                sys.modules.pop(info.module_name, None)
        except Exception:
            logger.exception("移除插件模块缓存失败: %s", info.module_name)

        # 4. 更新索引
        if info.file_path and info.file_path in self.file_to_plugins:
            self.file_to_plugins[info.file_path].discard(plugin_id)
            if not self.file_to_plugins[info.file_path]:
                self.file_to_plugins.pop(info.file_path)

        self.plugins.pop(plugin_id, None)
        return True

    def reload(
        self,
        plugin_id: str,
        *,
        override_config: Optional[Dict[str, Any]] = None,
    ) -> Optional[PluginInfo]:
        """重载单个插件。

        优先从 PluginConfigManager 中取最新配置；否则退回到已有 PluginInfo.config。
        可以通过 override_config 强制指定新的配置。
        """
        existing = self.plugins.get(plugin_id)
        logger.info(f"DEBUG reload | {plugin_id} {override_config}")
        origin = "manual"
        origin_detail: Optional[Dict[str, Any]] = None
        cfg: Dict[str, Any] = {}

        # 1. override_config 优先
        if override_config is not None:
            cfg = dict(override_config)
            if existing is not None:
                origin = existing.origin
                origin_detail = existing.origin_detail
        # 2. 其次尝试从配置文件获取
        elif self.config_manager is not None and plugin_id in self.config_manager.cfg:
            cfg = self.config_manager.get_plugin_cfg(plugin_id)
            origin = "config"
            origin_detail = {"config_file": self.config_manager.fp}
        # 3. 最后退回到现有 PluginInfo.config
        elif existing is not None:
            cfg = dict(existing.config or {})
            origin = existing.origin
            origin_detail = existing.origin_detail
        else:
            # 既没有已加载信息，也没有配置 → 视为加载失败
            logger.warning("找不到插件配置，无法重载: %s", plugin_id)
            return None

        self.unload(plugin_id)
        return self._load_one(
            target=plugin_id,
            config=cfg,
            origin=origin,
            origin_detail=origin_detail,
        )

    # ===== 内部实现 =====

    def _load_one(
        self,
        target: str,
        config: Optional[Dict[str, Any]] = None,
        origin: str = "manual",
        origin_detail: Optional[Dict[str, Any]] = None,
    ) -> PluginInfo:
        """加载单个插件 target 并记录状态。"""
        cfg = dict(config or {})
        plugin_id = target

        # 如果已存在同名插件，先卸载再加载
        if plugin_id in self.plugins:
            self.unload(plugin_id)

        if ":" in target:
            module_name, cls_name = target.split(":", 1)
            plugin_type = "class"
        else:
            module_name, cls_name = target, None
            plugin_type = "module"

        module = importlib.import_module(module_name)

        if plugin_type == "module":
            setup = getattr(module, "__setup__", None)
            if callable(setup):
                setup(self.bot, **cfg)
            instance: Any = module
        else:
            cls = getattr(module, cls_name)
            if not callable(cls):
                raise RuntimeError(f"不支持的插件 target: {target!r}")
            instance = cls(**cfg)
            setup = getattr(instance, "__setup__", None)
            if callable(setup):
                setup(self.bot)
        
        self._register_handlers_from_object(instance, sources={module_name, plugin_id})

        file_path = getattr(module, "__file__", None)
        mtime = 0.0
        if file_path is not None:
            try:
                mtime = Path(file_path).stat().st_mtime
            except OSError:
                mtime = 0.0

        info = PluginInfo(
            plugin_id=plugin_id,
            target=target,
            plugin_type=plugin_type,
            module_name=module_name,
            class_name=cls_name,
            config=cfg,
            instance=instance,
            handler_sources={module_name, plugin_id},
            file_path=file_path,
            mtime=mtime,
            origin=origin,
            origin_detail=origin_detail,
            enabled=True,
        )

        self.plugins[plugin_id] = info
        if file_path:
            self.file_to_plugins.setdefault(file_path, set()).add(plugin_id)

        self._tag_handlers_for_plugin(info)

        logger.info(f"插件已加载: {plugin_id} ({plugin_type})")
        return info

    def _tag_handlers_for_plugin(self, info: PluginInfo) -> None:
        """为插件相关 handler 增加插件 ID 作为来源，方便按插件卸载。"""
        module_name = info.module_name
        plugin_source = info.plugin_id

        try:
            handlers = self.handler.get_handlers_by_source(module_name)
        except Exception:
            logger.exception("根据模块名获取处理器失败: %s", module_name)
            handlers = []

        for entry in handlers:
            sources = entry.get("sources")
            if isinstance(sources, set):
                sources.add(plugin_source)
            else:
                new_sources: Set[str] = set()
                if isinstance(sources, (list, tuple, set)):
                    for s in sources:
                        new_sources.add(str(s))
                elif sources is not None:
                    new_sources.add(str(sources))
                new_sources.add(plugin_source)
                entry["sources"] = new_sources

        info.handler_sources = {module_name, plugin_source}
        info.handler_count = len(handlers)


# ===== 顶层函数：保持向后兼容 =====

def load_plugin(bot: "Bot", target: PluginPath, config: Optional[PluginConfig] = None) -> Any:
    """加载单个插件（向后兼容函数）。"""
    if getattr(bot, "plugin_manager", None) is None:
        # 延迟创建一个简单的 PluginManager
        bot.plugin_manager = PluginManager(bot)  # type: ignore[attr-defined]
    return bot.plugin_manager.load(target, config)


def load_plugins(bot: "Bot", specs: Iterable[PluginSpec]) -> List[Any]:
    """批量加载插件（向后兼容函数）。"""
    if getattr(bot, "plugin_manager", None) is None:
        bot.plugin_manager = PluginManager(bot)  # type: ignore[attr-defined]
    result = bot.plugin_manager.load(specs)
    return list(result or [])


__all__ = [
    "load_plugin",
    "load_plugins",
    "PluginSpec",
    "PluginPath",
    "PluginConfig",
    "PluginManager",
    "PluginInfo",
]
