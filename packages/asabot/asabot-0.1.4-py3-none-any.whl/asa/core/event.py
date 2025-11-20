"""OneBot 11 事件系统。

根据 OneBot 11 标准，事件分为以下类型：
- message: 消息事件（私聊消息、群消息）
- notice: 通知事件（群文件上传、群管理员变动等）
- request: 请求事件（加群请求、好友添加请求）
- meta_event: 元事件（生命周期、心跳）
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

class StopPropagation(Exception):
    pass

@dataclass
class Event:
    """OneBot 11 通用事件基类。"""
    raw: Dict[str, Any]
    
    def __new__(cls, raw: Dict[str, Any]):
        """根据 post_type 自动返回适当的事件子类实例。"""
        if cls is Event:  # 如果直接使用 Event 构造函数
            post_type = raw.get("post_type")
            if post_type == "message":
                return MessageEvent(raw)
            elif post_type == "notice":
                return NoticeEvent(raw)
            elif post_type == "request":
                return RequestEvent(raw)
            elif post_type == "meta_event":
                return MetaEvent(raw)
            else:
                # 对于未知类型，返回通用 Event
                instance = super().__new__(Event)
                instance.raw = raw
                return instance
        else:  # 如果直接指定了子类
            return super().__new__(cls)

    # ===== 通用基础字段 =====

    @property
    def time(self) -> Optional[int]:
        """事件发生时间戳。"""
        value = self.raw.get("time")
        try:
            return int(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    @property
    def self_id(self) -> Optional[int]:
        """机器人 QQ 号。"""
        value = self.raw.get("self_id")
        try:
            return int(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    @property
    def post_type(self) -> Optional[str]:
        """请求类型。"""
        return self.raw.get("post_type")

    # ===== 消息相关字段（仅在 post_type=message 时有效）=====
    # 为了向后兼容，这些字段保留在基类中，但在非消息事件中将返回 None

    @property
    def message_type(self) -> Optional[str]:
        """消息类型。"""
        return self.raw.get("message_type")  # "private" / "group"

    @property
    def sub_type(self) -> Optional[str]:
        """消息子类型。"""
        # 私聊: friend/group/other；群聊: normal/anonymous/notice
        return self.raw.get("sub_type")

    @property
    def message_id(self) -> Optional[int]:
        """消息 ID。"""
        value = self.raw.get("message_id")
        try:
            return int(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    @property
    def user_id(self) -> Optional[int]:
        """发送者 QQ 号。"""
        sender = self.raw.get("sender") or {}
        uid = sender.get("user_id") or self.raw.get("user_id")
        try:
            return int(uid) if uid is not None else None
        except (TypeError, ValueError):
            return None

    @property
    def group_id(self) -> Optional[int]:
        """群号，仅群消息有意义。"""
        gid = self.raw.get("group_id")
        try:
            return int(gid) if gid is not None else None
        except (TypeError, ValueError):
            return None

    @property
    def sender(self) -> Dict[str, Any]:
        """原始 sender 对象，可能为空字典。"""
        value = self.raw.get("sender")
        return value if isinstance(value, dict) else {}

    @property
    def anonymous(self) -> Optional[Dict[str, Any]]:
        """匿名信息，仅群消息有意义。"""
        value = self.raw.get("anonymous")
        return value if isinstance(value, dict) else None

    @property
    def message(self) -> Any:
        """OneBot 11 的 message 字段。

        支持两种格式：
        - 字符串格式：CQ 码，如 "[CQ:at,qq=123456]Hello World"
        - 数组格式：消息段数组，如 [{"type": "at", "data": {"qq": "123456"}}, {"type": "text", "data": {"text": "Hello World"}}]
        """
        return self.raw.get("message")

    @property
    def raw_message(self) -> Optional[str]:
        """原始消息内容字符串。通常由实现框架提供，为纯文本格式。"""
        value = self.raw.get("raw_message")
        return value if isinstance(value, str) else None

    @property
    def font(self) -> Optional[int]:
        """字体。"""
        value = self.raw.get("font")
        try:
            return int(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    @property
    def text(self) -> Optional[str]:
        """获取消息的文本表示。

        优先返回 raw_message（如果存在），否则尝试从 message 数组中提取文本。
        仅在消息事件中有意义。
        """
        # 优先返回 raw_message
        if self.raw_message:
            return self.raw_message
        
        # 否则尝试从 message 数组中提取文本
        message = self.message
        if isinstance(message, str):
            # 如果是字符串格式的 CQ 码，返回它
            return message
        elif isinstance(message, list):
            # 如果是消息段数组，提取文本内容
            text_parts = []
            for segment in message:
                if isinstance(segment, dict) and segment.get("type") == "text":
                    text_data = segment.get("data", {})
                    if "text" in text_data:
                        text_parts.append(str(text_data["text"]))
            return "".join(text_parts) if text_parts else None
        
        return None

    # ===== 便捷判断方法 =====

    @property
    def is_message(self) -> bool:
        """是否为消息事件。"""
        return self.post_type == "message"

    @property
    def is_notice(self) -> bool:
        """是否为通知事件。"""
        return self.post_type == "notice"

    @property
    def is_request(self) -> bool:
        """是否为请求事件。"""
        return self.post_type == "request"

    @property
    def is_meta_event(self) -> bool:
        """是否为元事件。"""
        return self.post_type == "meta_event"

    @property
    def is_group(self) -> bool:
        """是否为群消息。仅在消息事件中有意义。"""
        return self.message_type == "group"

    @property
    def is_private(self) -> bool:
        """是否为私聊消息。仅在消息事件中有意义。"""
        return self.message_type == "private"

    @property
    def is_anonymous(self) -> bool:
        """是否为匿名消息。仅在消息事件中有意义。"""
        return self.sub_type == "anonymous"


@dataclass
class MessageEvent(Event):
    """OneBot 11 消息事件类。

    支持私聊消息和群消息。
    """
    # MessageEvent 继承所有属性和方法，不需要额外定义
    # 这个类主要为了明确标识这是一个消息事件
    pass


@dataclass
class NoticeEvent(Event):
    """OneBot 11 通知事件类。"""
    
    @property
    def notice_type(self) -> Optional[str]:
        """通知类型。"""
        return self.raw.get("notice_type")


@dataclass
class RequestEvent(Event):
    """OneBot 11 请求事件类。"""
    
    @property
    def request_type(self) -> Optional[str]:
        """请求类型。"""
        return self.raw.get("request_type")


@dataclass
class MetaEvent(Event):
    """OneBot 11 元事件类。"""
    
    @property
    def meta_event_type(self) -> Optional[str]:
        """元事件类型。"""
        return self.raw.get("meta_event_type")


def create_event(raw_data: Dict[str, Any]) -> Event:
    """根据原始数据创建适当的事件对象。

    Args:
        raw_data: 原始 OneBot 11 事件数据

    Returns:
        适当的事件实例
    """
    # 现在 create_event 只是 Event 构造函数的别名
    return Event(raw_data)


__all__ = [
    "StopPropagation",
    "Event", 
    "MessageEvent", 
    "NoticeEvent", 
    "RequestEvent", 
    "MetaEvent",
    "create_event"
]