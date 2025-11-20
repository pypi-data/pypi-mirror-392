"""NapCat 适配器实现。

职责：
    - 管理到 NapCat 的 WebSocket 连接
    - 提供带 Bearer Token 的 HTTP 请求能力
"""

from __future__ import annotations

import json
from typing import Any, Awaitable, Callable, Dict, Optional

import aiohttp
from aiohttp import ClientSession, WSMsgType

from .logging import get_logger

logger = get_logger("core.adapter")


RawEventHandler = Callable[[Dict[str, Any]], Awaitable[None]]


class NapCatAdapter:
    """NapCat 适配器。"""

    def __init__(self, ws_url: str, http_url: str, token: str) -> None:
        if not ws_url or not http_url:
            raise ValueError("ws_url 和 http_url 不能为空")
        if not token:
            raise ValueError("NapCat 访问令牌 token 不能为空")

        self.ws_url = ws_url
        self.http_url = http_url.rstrip("/")
        # 所有 HTTP / WS 请求都带上 Bearer Token
        self._auth_header: Dict[str, str] = {"Authorization": f"Bearer {token}"}

        self._session: Optional[ClientSession] = None

    async def _ensure_session(self) -> ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(headers=self._auth_header)
        return self._session

    async def close(self) -> None:
        """关闭底层 HTTP/WS 连接。"""
        if self._session and not self._session.closed:
            await self._session.close()

    async def request(
        self,
        method: str,
        path: str,
        *,
        json_body: Any | None = None,
        params: Dict[str, Any] | None = None,
    ) -> Any:
        """向 NapCat HTTP API 发起请求。

        Args:
            method: HTTP 方法，例如 "GET" / "POST"
            path: 相对路径，例如 "/send_message"
            json_body: 作为 JSON 发送的请求体
            params: 查询参数

        Returns:
            一般返回 JSON 解码后的对象；如果非 JSON 响应，则返回文本。
        """
        session = await self._ensure_session()
        url = f"{self.http_url}/{path.lstrip('/')}"

        async with session.request(
            method.upper(),
            url,
            json=json_body,
            params=params,
            headers=self._auth_header,
        ) as resp:
            resp.raise_for_status()

            content_type = resp.headers.get("Content-Type", "")
            if "application/json" in content_type:
                return await resp.json()
            return await resp.text()

    # ===== OneBot 11 HTTP API 封装 =====

    async def call_action(self, action: str, **params: Any) -> Any:
        """调用 OneBot 11 风格的 HTTP API。

        默认使用 RESTful 风格的路径：

            POST /send_group_msg  {\"group_id\": ..., \"message\": ...}

        如果你的 NapCat 实例使用的是其它风格（例如 POST / 传 action），
        可以在你自己的适配器子类中重写此方法。
        """
        path = f"/{action.lstrip('/')}"
        return await self.request("POST", path, json_body=params)

    async def send_private_msg(
        self,
        user_id: int,
        message: Any,
        *,
        auto_escape: bool = False,
    ) -> Any:
        """发送私聊消息。"""
        return await self.call_action(
            "send_private_msg",
            user_id=user_id,
            message=message,
            auto_escape=auto_escape,
        )

    async def send_group_msg(
        self,
        group_id: int,
        message: Any,
        *,
        auto_escape: bool = False,
    ) -> Any:
        """发送群消息。"""
        return await self.call_action(
            "send_group_msg",
            group_id=group_id,
            message=message,
            auto_escape=auto_escape,
        )

    async def delete_msg(self, message_id: int) -> Any:
        """撤回一条消息。"""
        return await self.call_action("delete_msg", message_id=message_id)

    async def set_group_ban(
        self,
        group_id: int,
        user_id: int,
        *,
        duration: int = 30 * 60,
    ) -> Any:
        """禁言群成员。"""
        return await self.call_action(
            "set_group_ban",
            group_id=group_id,
            user_id=user_id,
            duration=duration,
        )

    async def set_group_kick(
        self,
        group_id: int,
        user_id: int,
        *,
        reject_add_request: bool = False,
    ) -> Any:
        """将成员踢出群。"""
        return await self.call_action(
            "set_group_kick",
            group_id=group_id,
            user_id=user_id,
            reject_add_request=reject_add_request,
        )

    async def run_ws_loop(self, on_event: RawEventHandler) -> None:
        """连接 NapCat WebSocket 并循环消费事件。

        Args:
            on_event: 每收到一条 JSON 事件就调用一次。
        """
        session = await self._ensure_session()

        async with session.ws_connect(self.ws_url, headers=self._auth_header) as ws:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                    except json.JSONDecodeError:
                        logger.warning(f"收到非 JSON 文本消息: {msg.data}")
                        continue

                    try:
                        await on_event(data)
                    except Exception:  # pragma: no cover - 防止用户 handler 崩掉整个循环
                        logger.exception("处理 NapCat 事件时出错")

                elif msg.type == WSMsgType.ERROR:
                    logger.error(f"WebSocket 错误: {msg.data}")
                    break
                elif msg.type in (WSMsgType.CLOSED, WSMsgType.CLOSING):
                    logger.info("WebSocket 连接已关闭")
                    break


__all__ = ["NapCatAdapter", "RawEventHandler"]
