"""配置中心（严格模式）。

优先级：参数 > 环境变量 > .env 文件 > 显式抛出异常

原则：关键配置无隐式默认值，必须显式指定。
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional, List, Dict, Any


class ConfigError(Exception):
    """配置缺失或格式错误时抛出。"""


@dataclass
class Config:
    """配置加载策略（严格模式）。

    1. 优先使用用户传入的参数
    2. 其次检查环境变量
    3. 尝试加载 .env 文件（如果存在，且安装了 python-dotenv）
    4. 以上都没有 → 抛出 ConfigError
    """

    ws_url: str
    http_url: str
    token: str
    log_level: str
    admin_qq: List[int]

    # 配置键定义（无默认值）
    WS_URL_KEY = "WS_URL"
    HTTP_URL_KEY = "HTTP_URL"
    ADMIN_QQ_KEY = "ADMIN_QQ"
    TOKEN_KEY = "NAPCAT_TOKEN"
    LOG_LEVEL_KEY = "LOG_LEVEL"

    def __init__(
        self,
        ws_url: Optional[str] = None,
        http_url: Optional[str] = None,
        token: Optional[str] = None,
    ):
        # 1. 尝试加载 .env（静默，存在且有 python-dotenv 才生效）
        self._load_dotenv_if_exists()

        # 2. 按优先级加载配置
        resolved_ws_url = self._get_strict(self.WS_URL_KEY, ws_url, "WebSocket 地址")
        resolved_http_url = self._get_strict(self.HTTP_URL_KEY, http_url, "HTTP 地址")
        resolved_token = self._get_strict(self.TOKEN_KEY, token, "NapCat 访问令牌")
        resolved_log_level = self._get_with_default(
            self.LOG_LEVEL_KEY, "INFO", "日志级别"
        )
        resolved_admin_qq = self._parse_admin_qq()

        # dataclass 字段赋值
        object.__setattr__(self, "ws_url", resolved_ws_url)
        object.__setattr__(self, "http_url", resolved_http_url)
        object.__setattr__(self, "token", resolved_token)
        object.__setattr__(self, "log_level", resolved_log_level)
        object.__setattr__(self, "admin_qq", resolved_admin_qq)

    def _load_dotenv_if_exists(self) -> None:
        """静默加载 .env（存在才加载，不报错）。

        优先使用当前工作目录下的 .env；
        如果未安装 python-dotenv，则直接略过。
        """
        try:
            from dotenv import load_dotenv
        except ImportError:
            return

        # 默认行为：从当前工作目录查找 .env
        load_dotenv()

    def _get_strict(self, key: str, param_value: Optional[str], name: str) -> str:
        """严格获取配置：参数 → 环境变量 → 抛错。"""
        if param_value is not None:
            return param_value

        env_value = os.getenv(key)
        if env_value:
            return env_value

        raise ConfigError(
            f"配置缺失: {name} ({key})\n"
            f"请通过以下方式之一指定：\n"
            f"  1) 代码参数: bot = QQBot({key.lower()}='...')\n"
            f"  2) 环境变量: export {key}=...\n"
            f"  3) .env 文件: {key}=...\n"
        )

    def _get_with_default(self, key: str, default: str, name: str) -> str:
        """带默认值的获取（仅用于非关键配置）。"""
        env_value = os.getenv(key)
        if env_value is not None:
            return env_value
        return default

    def _parse_admin_qq(self) -> List[int]:
        """解析 ADMIN_QQ（可选配置）。"""
        admins = os.getenv(self.ADMIN_QQ_KEY, "")
        if not admins:
            return []
        try:
            return [int(q.strip()) for q in admins.split(",") if q.strip()]
        except ValueError as exc:
            raise ConfigError(
                "ADMIN_QQ 格式错误，应为: 123456789,987654321"
            ) from exc

    def diagnose(self) -> Dict[str, Any]:
        """诊断配置（基于已加载的值）。

        当前实现为占位逻辑：仅构造适配器实例，并返回待检测状态。
        真正的连通性检测建议在 QQBot 启动时进行。
        """
        try:
            from .adapter import NapCatAdapter
        except Exception as exc:  # pragma: no cover - 极端情况
            return {"status": "ERROR", "details": f"适配器导入失败: {exc}"}

        try:
            _ = NapCatAdapter(self.ws_url, self.http_url, self.token)
        except Exception as exc:  # pragma: no cover - 具体实现由适配器决定
            return {"status": "ERROR", "details": str(exc)}

        return {"status": "PENDING", "details": "待启动时进行连接检测"}


__all__ = ["Config", "ConfigError"]
