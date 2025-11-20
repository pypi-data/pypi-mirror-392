"""
NapCat Python Bot Framework
严格配置版：参数 → 环境变量 → .env → 显式报错

对外公开的主入口：
    - Bot / AsaBot: 机器人核心类
    - ConfigError: 严格配置异常，用户可捕获
    - 一些常用装饰器和事件类型（来自 core.deco / core.event）
"""

from .core.bot import Bot, AsaBot
from .core.config import ConfigError
from .core.deco import *  # noqa: F401,F403
from .core.event import *  # noqa: F401,F403
from .core.ctx import ctx

from .core.deco import __all__ as _decorator_all
from .core.event import __all__ as _event_all

# 注意保持与 pyproject.toml 中的 version 一致
__version__ = "0.1.4"

__all__ = [
    "Bot",
    "AsaBot",
    "ConfigError",
    "ctx",
] + _decorator_all + _event_all
