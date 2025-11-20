"""基于 Loguru 的全局日志配置模块。

本模块集中管理日志配置，并提供按模块名绑定的 logger：

    from .logging import setup_logging, get_logger

    setup_logging(level="INFO")
    logger = get_logger("core.adapter")

所有日志都会带上 ``module`` 字段，方便区分不同子模块的输出。
"""

from __future__ import annotations

import os
import sys
from typing import Final

from loguru import logger as _logger

# 避免重复配置：如果 setup_logging() 已经成功执行过一次，
# 后续调用将直接返回，不再重复添加 sink。
_LOGGING_CONFIGURED: bool = False

_DEFAULT_LEVEL: Final[str] = "INFO"

# 默认输出格式：时间 | 级别 | 模块 | 源文件:函数:行号 - 日志内容
_LOG_FORMAT: Final[str] = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{extra[module]}</cyan> | "
    "{name}:{function}:{line} - "
    "<level>{message}</level>"
)


def _resolve_level(level: str | None) -> str:
    """根据参数 / 环境变量 / 默认值解析最终日志级别。"""
    if level:
        return level.upper()

    env_level = os.getenv("LOG_LEVEL")
    if env_level:
        return env_level.upper()

    return _DEFAULT_LEVEL


def setup_logging(level: str | None = None) -> None:
    """配置全局 Loguru 日志。

    该函数是幂等的：只会在第一次调用时真正修改日志配置。
    """
    global _LOGGING_CONFIGURED

    if _LOGGING_CONFIGURED:
        return

    # 移除 Loguru 默认输出（否则会有重复输出或不符合期望的格式）。
    _logger.remove()

    resolved_level = _resolve_level(level)

    # 添加一个 stdout sink，项目内统一使用这一套配置。
    # 如果用户有更复杂需求，可以在应用层自行添加其他 sink。
    _logger.add(
        sys.stdout,
        level=resolved_level,
        format=_LOG_FORMAT,
        backtrace=True,
        diagnose=False,
    )

    # 提供一个默认的 module 值，避免用户在未 bind module 时格式化 KeyError。
    _logger.configure(extra={"module": "asa"})

    _LOGGING_CONFIGURED = True


def get_logger(module: str):
    """根据模块名获取绑定了 ``module=xxx`` 的 logger。"""
    return _logger.bind(module=module)


__all__ = ["setup_logging", "get_logger"]
