"""装饰器注册表。

核心思想：
    - 所有条件都是 Condition 实例或返回 Condition 的函数
    - 业务代码只关心“写在函数上的条件”，调度由 Bot 负责
"""

from __future__ import annotations

import inspect
from typing import Callable, List, Union, Any, Set, Dict

from .condition import (
    Condition,
    create_condition,
    message_type_is,
    raw_message_contains,
    user_id_in,
    group_id_in,
)


class EventHandler:
    """全局处理器注册表。

    额外维护了一个 `sources` 概念，用于标记 handler 的来源：
        - 默认来源：函数所在模块名（func.__module__）
        - 额外来源：调用方通过 sources 参数显式指定，例如插件 ID

    PluginManager 会利用这一机制按“来源”批量卸载插件相关 handler。
    """

    def __init__(self) -> None:
        self._handlers: List[Dict[str, Any]] = []
        self.dirty: bool = False

    def register_handler(
        self,
        func: Callable,
        condition: Union[Condition, None] = None,
        sources: Union[str, Set[str], None] = None,
        **kwargs: Any,
    ) -> None:
        """注册处理器到适配器。"""
        condition_attrs = condition.attrs if condition is not None else {}
        all_attrs: Dict[str, Any] = {**condition_attrs, **kwargs}

        # 计算来源集合
        source_set: Set[str] = set()
        module_name = getattr(func, "__module__", None)
        if module_name:
            source_set.add(str(module_name))
        if sources:
            if isinstance(sources, str):
                source_set.add(sources)
            else:
                for s in sources:
                    source_set.add(str(s))
        if not source_set:
            source_set.add("unknown")

        entry: Dict[str, Any] = {
            "func": func,
            "condition": condition,
            "priority": all_attrs.get("priority", 0),
            "attrs": all_attrs,
            "sources": source_set,
        }
        self._handlers.append(entry)
        self.dirty = True

    def unregister_handler_by_source(self, sources: Union[str, Set[str]]) -> int:
        """根据任意匹配的来源卸载处理器。"""
        if isinstance(sources, str):
            source_set: Set[str] = {sources}
        else:
            source_set = set(str(s) for s in sources)

        original_count = len(self._handlers)
        self._handlers = [
            h
            for h in self._handlers
            if not any(src in source_set for src in h.get("sources", set()))
        ]
        removed_count = original_count - len(self._handlers)
        if removed_count:
            self.dirty = True
        return removed_count

    def get_handlers_by_source(self, sources: Union[str, Set[str]]) -> List[dict]:
        """获取包含任意指定来源的处理器。"""
        if isinstance(sources, str):
            source_set: Set[str] = {sources}
        else:
            source_set = set(str(s) for s in sources)
        return [
            h
            for h in self._handlers
            if any(src in source_set for src in h.get("sources", set()))
        ]

    def _sort(self) -> None:
        self._handlers.sort(key=lambda x: x.get("priority", 0), reverse=True)

    def get_handlers(self) -> list[dict]:
        if self.dirty:
            self._sort()
            self.dirty = False
        return list(self._handlers)

    def clear(self) -> None:
        """用于测试或重置。"""
        self._handlers.clear()


# ========== 单例条件：可直接 @condition ==========


# 无括号魔法：这些本身就是 Condition 实例
def on_group_message(func = None, **attrs):
    cond = message_type_is("group", **attrs)
    if func is None: # attrs
        def decorator(f):
            return cond(f)
        return decorator
    return cond(func)

def on_private_message(func = None, **attrs):
    cond = message_type_is("private", **attrs)
    if func is None:
        def decorator(f):
            return cond(f)
        return decorator
    return cond(func)

def on_at_me(func = None, **attrs):
    cond = create_condition(
        lambda e: f"[CQ:at,qq={getattr(e, 'self_id', '')}]" in (getattr(e, "raw_message", "") or ""),
        name="is_at_me",
        **attrs
    )
    if func is None:
        def decorator(f):
            return cond(f)
        return decorator
    return cond(func)


# ========== 参数化条件：函数返回 Condition ==========

def on_keyword(*keywords: str, **attrs) -> Condition:
    """有参数，必须括号，但内部统一走工厂。"""
    return raw_message_contains(*keywords, **attrs)


def from_user(user_ids: list[int], **attrs) -> Condition:
    return user_id_in(user_ids, **attrs)


def from_group(group_ids: list[int], **attrs) -> Condition:
    return group_id_in(group_ids, **attrs)


def custom_condition(predicate: Callable, **attrs) -> Condition:
    """用户自定义条件。"""
    return create_condition(predicate, **attrs)


# ========== 组合器 ==========

def any_of(*conditions: Condition) -> Callable[[Callable], Callable]:
    """或组合：any_of(A, B) → A | B | ..."""

    def decorator(func: Callable) -> Callable:
        final = conditions[0]
        for cond in conditions[1:]:
            final = final | cond
        # 复用 Condition.__call__ 的装饰和注册逻辑
        return final(func)  # type: ignore[return-value]

    return decorator


def all_of(*conditions: Condition) -> Callable[[Callable], Callable]:
    """与组合：all_of(A, B) → A & B & ..."""

    def decorator(func: Callable) -> Callable:
        final = conditions[0]
        for cond in conditions[1:]:
            final = final & cond
        return final(func)  # type: ignore[return-value]

    return decorator


__all__ = [
    "on_group_message",
    "on_private_message",
    "on_at_me",
    "on_keyword",
    "from_user",
    "from_group",
    "custom_condition",
    "any_of",
    "all_of",
]
