"""当前上下文工具。

封装对当前协程内 Bot / Event 的访问，便于在 handler 中使用：

    from asa import ctx

    @on_group_message
    async def handle(event, bot):
        await ctx.reply("hello")  # 等价于 bot.reply(event, "hello")
"""

from __future__ import annotations

import contextvars
from dataclasses import dataclass
from typing import Any, Optional

from .bot import _current_bot, _current_event
from .event import Event


# 每个事件处理协程的扩展数据存储
_event_ext: contextvars.ContextVar[dict] = contextvars.ContextVar("asa_event_ext")


@dataclass
class _CtxProxy:
    """当前事件上下文的轻量代理。"""

    def get_bot(self) -> "Optional[Any]":
        try:
            return _current_bot.get()
        except LookupError:
            return None

    def get_event(self) -> Optional[Event]:
        try:
            return _current_event.get()
        except LookupError:
            return None

    # 便捷属性
    @property
    def bot(self) -> "Optional[Any]":
        return self.get_bot()

    @property
    def event(self) -> Optional[Event]:
        return self.get_event()

    # 扩展数据操作
    def set_ext(self, key: str, value: Any) -> None:
        """设置当前事件的扩展数据。"""
        try:
            store = _event_ext.get()
        except LookupError:
            # 首次访问，创建扩展数据存储
            store = {}
            _event_ext.set(store)

        store[key] = value

    def get_ext(self, key: str, default: Any = None) -> Any:
        """获取当前事件的扩展数据。"""
        try:
            store = _event_ext.get()
            return store.get(key, default)
        except LookupError:
            # 扩展数据未初始化
            return default

    def delete_ext(self, key: str) -> bool:
        """删除当前事件的扩展数据。"""
        try:
            store = _event_ext.get()
            if key in store:
                del store[key]
                return True
            return False
        except LookupError:
            # 扩展数据未初始化
            return False

    def clear_ext(self) -> None:
        """清空当前事件的所有扩展数据。"""
        try:
            store = _event_ext.get()
            store.clear()
        except LookupError:
            # 扩展数据未初始化，无需操作
            pass

    def has_ext(self, key: str) -> bool:
        """检查当前事件扩展数据是否包含指定键。"""
        try:
            store = _event_ext.get()
            return key in store
        except LookupError:
            return False

    # 便捷操作封装
    async def reply(self, message: str, **kwargs: Any) -> Any:
        """基于当前事件快速回复。

        等价于：

            bot = ctx.bot
            event = ctx.event
            await bot.reply(event, message, **kwargs)
        """
        bot = self.get_bot()
        event = self.get_event()
        if bot is None or event is None:
            raise RuntimeError("ctx.reply() 必须在事件处理上下文中调用")
        return await bot.reply(message, event, **kwargs)


ctx = _CtxProxy()


__all__ = ["ctx"]

