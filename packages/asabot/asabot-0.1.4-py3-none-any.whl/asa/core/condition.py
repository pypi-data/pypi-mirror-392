"""条件系统。

核心目标：
    - 所有条件都是 `Condition` 实例或返回 `Condition` 的函数
    - `Condition.__call__` 同时支持：
        * `@condition` / `@condition()` 作为装饰器
        * `condition(event)` 作为布尔判断
"""

from __future__ import annotations

import inspect
from .event import Event
from typing import Any, Callable, Iterable, Union, get_type_hints


class Condition:
    """条件对象：可组合、可调用、可直接装饰。"""

    def __init__(self, predicate: Callable[[Any], bool], *, name: str | None = None, **attrs: Any):
        self.predicate = predicate
        self.name = name or predicate.__name__
        self.target_type = Event
        self.attrs = attrs

    def __call__(self, arg: Any = None) -> Union[Callable[..., Any], "Condition", bool]:
        """双重职责：

        - 作为装饰器：
            @condition
            @condition()
        - 作为判断：
            if condition(event): ...
        """
        # @condition() 模式：无参数调用，返回自身
        if arg is None:
            return self

        # 事件判断：arg 不是可调用对象，则视为事件
        if not callable(arg):
            if self.target_type:
                if not isinstance(arg, self.target_type):
                    return False
            return bool(self.predicate(arg))

        # @condition 模式：装饰函数
        func: Callable[..., Any] = arg
        priority = getattr(func, "_priority", 0)
        setattr(func, "_condition", self)

        func_msg_param = inspect_first_parameter_type(func)
        self.target_type = func_msg_param if func_msg_param is not None else Event

        return func

    def __and__(self, other: "Condition") -> "Condition":
        return Condition(
            lambda e: bool(self(e)) and bool(other(e)),
            name=f"({self.name} & {other.name})",
        )

    def __or__(self, other: "Condition") -> "Condition":
        return Condition(
            lambda e: bool(self(e)) or bool(other(e)),
            name=f"({self.name} | {other.name})",
        )

    def __invert__(self) -> "Condition":
        return Condition(
            lambda e: not bool(self(e)),
            name=f"~{self.name}",
        )

    def debug(self, event: Any) -> str:
        """生成调试信息（结果 + 条件名）。"""
        result = bool(self(event))
        status = "[OK]" if result else "[FAIL]"
        return f"{status} {self.name}"

    def __repr__(self) -> str:  # pragma: no cover - 仅调试使用
        return f"<Condition: {self.name}>"

# ========== 工具函数 ==========

def inspect_first_parameter_type(func: Callable[..., Any]) -> type | None:
    try:
        sig = inspect.signature(func)
        params = list(sig.parameters.values())
        if not params:
            return None
        first = params[0]
        annotation = first.annotation
        if annotation is inspect.Parameter.empty:
            return None
        if isinstance(annotation, type):
            return annotation
        try:
            resolved = get_type_hints(func)
            return resolved.get(list(sig.parameters.keys())[0])
        except (NameError, AttributeError):
            return None

    except Exception:
        return None

# ========== 统一工厂 ==========

def create_condition(predicate: Callable[[Any], bool], *, name: str | None = None, **attrs) -> Condition:
    """所有条件的唯一入口。"""
    return Condition(predicate, name=name, **attrs)


# ========== 内置条件生成器 ==========

def message_type_is(type_name: str, **attrs) -> Condition:
    """匹配消息类型：'private' / 'group' 等。"""
    return create_condition(
        lambda e: getattr(e, "message_type", None) == type_name,
        name=f"msg_type='{type_name}'",
        **attrs
    )


def sub_type_is(sub_type: str, **attrs) -> Condition:
    """匹配消息子类型：

    私聊: friend/group/other
    群聊: normal/anonymous/notice
    """
    return create_condition(
        lambda e: getattr(e, "sub_type", None) == sub_type,
        name=f"sub_type='{sub_type}'",
        **attrs
    )


def raw_message_contains(*keywords: Union[str, Iterable[str]], **attrs) -> Condition:
    """消息文案包含任意关键字。

    支持：
        on_keyword("A", "B", ["C", "D"])
    """
    flat_keywords: list[str] = []
    for kw in keywords:
        if isinstance(kw, (list, tuple, set)):
            flat_keywords.extend(str(x) for x in kw)
        else:
            flat_keywords.append(str(kw))

    def _predicate(e: Any) -> bool:
        text = getattr(e, "raw_message", None) or getattr(e, "text", "") or ""
        return any(kw in text for kw in flat_keywords)

    return create_condition(_predicate, name=f"contains{flat_keywords}", **attrs)


def user_id_in(user_ids: list[int], **attrs) -> Condition:
    return create_condition(
        lambda e: getattr(e, "user_id", None) in user_ids,
        name=f"user∈{user_ids}",
        **attrs
    )


def group_id_in(group_ids: list[int], **attrs) -> Condition:
    return create_condition(
        lambda e: getattr(e, "group_id", None) in group_ids,
        name=f"group∈{group_ids}",
        **attrs
    )


def sender_role_in(roles: Iterable[str], **attrs) -> Condition:
    """匹配群成员角色：owner/admin/member 等。"""
    roles_set = {str(r) for r in roles}

    def _predicate(e: Any) -> bool:
        sender = getattr(e, "sender", {}) or {}
        role = str(sender.get("role", ""))
        return role in roles_set

    return create_condition(_predicate, name=f"role∈{sorted(roles_set)}", **attrs)


__all__ = [
    "Condition",
    "create_condition",
    "message_type_is",
    "sub_type_is",
    "raw_message_contains",
    "user_id_in",
    "group_id_in",
    "sender_role_in",
]
