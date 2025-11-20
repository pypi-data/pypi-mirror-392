"""处理器自动发现工具。

默认行为：
    - 扫描并导入 `bot` 包下的所有子模块
    - 导入时触发装饰器执行，从而注册事件处理函数
"""

from __future__ import annotations

import importlib
import pkgutil
import inspect
from types import ModuleType
from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from .bot import Bot


def _import_package(name: str) -> ModuleType | None:
    """安全导入一个包，不存在时返回 None。"""
    try:
        module = importlib.import_module(name)
    except ModuleNotFoundError:
        return None
    return module


def _walk_package(bot: Bot, module: ModuleType) -> None:
    """导入包下所有子模块并注册处理器。"""
    if not hasattr(module, "__path__"):
        return

    prefix = module.__name__ + "."
    for info in pkgutil.walk_packages(module.__path__, prefix):
        sub_module = importlib.import_module(info.name)
        # 扫描模块内所有成员，查找被 @condition 装饰的函数
        for _, member in inspect.getmembers(sub_module):
            if inspect.isfunction(member) and hasattr(member, "_condition"):
                condition = getattr(member, "_condition")
                bot.handler.register_handler(member, condition, **condition.attrs, sources={info.name, "auto_discover"})


def discover_handlers(bot: Bot, packages: Iterable[str]) -> None:
    """导入并扫描给定包列表，然后注册处理器。

    Args:
        bot: Bot 实例
        packages: 包名列表，例如 ["bot", "mybot.handlers"]
    """
    for name in packages:
        module = _import_package(name)
        if module is None:
            continue
        _walk_package(bot, module)


__all__ = ["discover_handlers"]

