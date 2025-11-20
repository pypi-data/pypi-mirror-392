"""QQBot 主类。

特点：
    - 严格配置：ws_url / http_url 必须显式配置
    - 启动前即可发现配置问题并给出修复建议
"""

from __future__ import annotations

import asyncio
import inspect
from contextvars import ContextVar
from typing import Any, Iterable, Optional, Sequence, Union

from .adapter import NapCatAdapter
from .config import Config, ConfigError
from .deco import EventHandler
from .event import Event, StopPropagation
from .discovery import discover_handlers
from .logging import get_logger, setup_logging
from ..plugin import PluginSpec, PluginConfig, PluginPath, PluginManager
from ..plugin.config import PluginConfigManager

logger = get_logger("core.bot")


# 当前协程内的 Bot / Event 上下文，用于 ctx 和省略参数的 API
_current_bot: ContextVar["Bot"] = ContextVar("asa_current_bot")
_current_event: ContextVar[Event] = ContextVar("asa_current_event")


class Bot:
    """严格配置机器人。

    - ws_url / http_url / token 必须显式指定
    - 使用 Condition 装饰器注册消息处理函数
    - run() 内部维护事件循环与 NapCat 连接
    """

    def __init__(
        self,
        ws_url: Optional[str] = None,
        http_url: Optional[str] = None,
        token: Optional[str] = None,
        *,
        plugin_config_manager: PluginConfigManager = PluginConfigManager(),
        auto_discover: bool = True,
        discover_packages: Optional[Sequence[str]] = None,
    ):
        """创建 Bot 实例。

        Args:
            ws_url: NapCat WebSocket 地址（参数、环境变量或 .env）
            http_url: NapCat HTTP API 基础地址（参数、环境变量或 .env）
            token: NapCat 访问令牌，会作为 Bearer Token 放在 HTTP 请求头里
            auto_discover: 是否自动扫描并导入处理器模块，默认开启
            discover_packages: 自动扫描的包列表，默认为 ["bot"]

        Raises:
            ConfigError: 配置缺失或格式错误时抛出，包含修复提示。
        """
        try:
            self.config = Config(ws_url, http_url, token)
        except ConfigError as exc:
            self._print_config_help(exc)
            raise

        # 基于配置的日志级别初始化全局日志系统（Loguru）。
        # 只会在第一次调用时生效，后续创建 Bot 实例不会重复添加 sink。
        setup_logging(self.config.log_level)

        self.adapter = NapCatAdapter(
            self.config.ws_url,
            self.config.http_url,
            self.config.token,
        )
        self.handler = EventHandler()
        self.plugin_config_manager = plugin_config_manager
        self.plugin_manager = PluginManager(self, self.plugin_config_manager)

        self._initialized = False
        self.login_info: Optional[dict[str, Any]] = None
        self.login_info_raw: Optional[dict[str, Any]] = None

        if auto_discover:
            packages: Iterable[str] = discover_packages or ("bot",)
            discover_handlers(self, packages)

    @staticmethod
    def _print_config_help(error: ConfigError) -> None:
        """打印配置错误和快速修复指南。"""
        sep = "=" * 50
        print(f"\n{sep}")
        print("配置错误！")
        print(sep)
        print(error)
        print("\n快速修复示例：")
        print("-" * 50)
        print("方式1：代码参数")
        print("  bot = Bot(")
        print("      ws_url='ws://127.0.0.1:3001',")
        print("      http_url='http://127.0.0.1:3000',")
        print("      token='YOUR_NAPCAT_TOKEN',")
        print("  )")
        print()
        print("方式2：环境变量")
        print("  export WS_URL=ws://127.0.0.1:3001")
        print("  export HTTP_URL=http://127.0.0.1:3000")
        print("  export NAPCAT_TOKEN=YOUR_NAPCAT_TOKEN")
        print()
        print("方式3：.env 文件")
        print("  创建 .env 文件并写入：")
        print("  WS_URL=ws://127.0.0.1:3001")
        print("  HTTP_URL=http://127.0.0.1:3000")
        print("  NAPCAT_TOKEN=YOUR_NAPCAT_HTTP_TOKEN")
        print(sep + "\n")

    def _diagnose_on_start(self) -> None:
        """启动时的基础诊断钩子。"""
        logger.info(
            f"启动 Bot，ws_url={self.config.ws_url} http_url={self.config.http_url} admins={self.config.admin_qq}"
        )

    async def _fetch_login_info(self) -> None:
        """调用 get_login_info 获取当前登录账号信息并缓存到 bot 上。"""
        try:
            resp = await self.adapter.call_action("get_login_info")
        except Exception:
            logger.exception("调用 get_login_info 失败")
            return

        if not isinstance(resp, dict):
            logger.warning(f"get_login_info 响应不是 JSON 对象: {resp!r}")
            return

        self.login_info_raw = resp

        # OneBot 11 标准结构：{status, retcode, data, message, wording, echo}
        data = resp.get("data")
        if isinstance(data, dict):
            self.login_info = data
        else:
            # 有些实现可能直接返回 data
            self.login_info = resp

        logger.info(
            f"已获取登录信息: user_id={self.account_id} nickname={self.account_nickname}"
        )

    # 便捷访问账号信息
    @property
    def account_id(self) -> Optional[int]:
        """当前登录 QQ 号（如果已成功获取）。"""
        info = self.login_info or {}
        uid = info.get("user_id")
        try:
            return int(uid) if uid is not None else None
        except (TypeError, ValueError):
            return None

    @property
    def account_nickname(self) -> Optional[str]:
        """当前登录账号昵称（如果已成功获取）。"""
        info = self.login_info or {}
        name = info.get("nickname")
        return str(name) if name is not None else None

    # ===== 对外 API：OneBot 11 消息操作封装 =====

    async def send_private(
        self,
        message: str,
        user_id: Optional[int] = None,
        *,
        auto_escape: bool = False,
    ) -> Any:
        """发送私聊消息（兼容 OneBot 11 的 send_private_msg）。"""
        if user_id is None:
            # 尝试从当前事件获取
            try:
                current_event = _current_event.get()
            except LookupError:
                current_event = None
            if current_event is None or current_event.user_id is None:
                raise RuntimeError("send_private() 需要显式提供 user_id，或在事件上下文中调用")
            user_id = current_event.user_id

        return await self.adapter.send_private_msg(
            user_id=user_id,
            message=message,
            auto_escape=auto_escape,
        )

    async def send_group(
        self,
        message: str,
        group_id: Optional[int] = None,
        *,
        auto_escape: bool = False,
    ) -> Any:
        """发送群消息（兼容 OneBot 11 的 send_group_msg）。"""
        if group_id is None:
            try:
                current_event = _current_event.get()
            except LookupError:
                current_event = None
            if current_event is None or current_event.group_id is None:
                raise RuntimeError("send_group() 需要显式提供 group_id，或在事件上下文中调用")
            group_id = current_event.group_id

        return await self.adapter.send_group_msg(
            group_id=group_id,
            message=message,
            auto_escape=auto_escape,
        )

    async def reply(
        self,
        message: str,
        event: Optional[Event] = None,
        *,
        at_sender: bool = False,
        auto_escape: bool = False,
    ) -> Any:
        """基于事件快速回复。

        对私聊消息：调用 send_private
        对群消息：调用 send_group，可选择是否自动 at 发送者。
        """
        if event is None:
            try:
                event = _current_event.get()
            except LookupError:
                event = None

        if event is None:
            raise RuntimeError("reply() 需要显式提供 event，或在事件上下文中调用")

        if event.is_private and event.user_id is not None:
            return await self.send_private(
                message=message,
                auto_escape=auto_escape,
            )

        if event.is_group and event.group_id is not None:
            text = message
            if at_sender and event.user_id is not None:
                # 使用 OneBot 11 CQ 码 at 发送者
                text = f"[CQ:at,qq={event.user_id}] {message}"
            return await self.send_group(
                message=text,
                auto_escape=auto_escape,
            )

        # 其它情况暂不支持，直接返回 None
        logger.warning(f"无法基于该事件回复：{event.raw}")
        return None

    async def delete_message(self, message_id: int) -> Any:
        """根据 message_id 撤回一条消息。"""
        return await self.adapter.delete_msg(message_id=message_id)

    async def delete(self, event: Event) -> Any:
        """根据事件撤回消息（如果 message_id 存在）。"""
        if event.message_id is None:
            logger.warning(f"事件不包含 message_id，无法撤回：{event.raw}")
            return None
        return await self.delete_message(event.message_id)

    async def ban_sender(self, event: Event, duration: int = 30 * 60) -> Any:
        """根据事件禁言发送者。"""
        if not event.is_group or event.group_id is None or event.user_id is None:
            logger.warning(f"事件不包含群号或用户号，无法禁言：{event.raw}")
            return None
        return await self.adapter.set_group_ban(
            group_id=event.group_id,
            user_id=event.user_id,
            duration=duration,
        )

    async def kick_sender(
        self,
        event: Event,
        *,
        reject_add_request: bool = False,
    ) -> Any:
        """根据事件踢出发送者。"""
        if not event.is_group or event.group_id is None or event.user_id is None:
            logger.warning(f"事件不包含群号或用户号，无法踢人：{event.raw}")
            return None
        return await self.adapter.set_group_kick(
            group_id=event.group_id,
            user_id=event.user_id,
            reject_add_request=reject_add_request,
        )
    async def _handle_raw_event(self, raw: dict) -> None:
        """将原始 NapCat 事件分发给符合条件的处理器。"""
        from .ctx import _event_ext  # 延迟导入避免循环引用

        event = Event(raw=raw)
        handlers = self.handler.get_handlers()

        if not handlers:
            logger.debug(f"收到事件但没有注册任何消息处理函数: {raw}")
            return

        bot_token = _current_bot.set(self)
        evt_token = _current_event.set(event)
        # 初始化事件扩展数据上下文
        ext_store = {}
        ext_token = _event_ext.set(ext_store)
        try:
            for entry in handlers:
                func = entry.get("func")
                cond = entry.get("condition") or getattr(func, "_condition", None)

                if cond is not None:
                    try:
                        if not cond(event):
                            continue
                    except Exception:
                        logger.exception(f"条件 {cond!r} 评估出错，跳过处理函数 {func!r}")
                        continue

                # 根据函数参数个数决定是否注入 bot 实例
                try:
                    sig = inspect.signature(func)
                    param_count = len(sig.parameters)
                except (TypeError, ValueError):
                    param_count = 1  # 无法解析时，退回到只传 event

                try:
                    if inspect.iscoroutinefunction(func):
                        if param_count == 0:
                            await func()  # type: ignore[misc]
                        elif param_count == 1:
                            await func(event)  # type: ignore[misc]
                        else:
                            await func(event, self)  # type: ignore[misc]
                    else:
                        if param_count == 0:
                            func()
                        elif param_count == 1:
                            func(event)
                        else:
                            func(event, self)
                except StopPropagation:
                    logger.debug(f"事件传播被 {func!r} 阻断")
                    break
                except Exception:
                    logger.exception(f"消息处理函数 {func!r} 执行出错")
        finally:
            _current_event.reset(evt_token)
            _current_bot.reset(bot_token)
            # 重置扩展数据上下文
            _event_ext.reset(ext_token)

    async def _run_main(self) -> None:
        """内部主协程：诊断 + 事件循环。"""
        self._diagnose_on_start()
        await self._fetch_login_info()
        try:
            await self.adapter.run_ws_loop(self._handle_raw_event)
        finally:
            await self.adapter.close()

    def run(self) -> None:
        """启动机器人（同步阻塞）。

        典型用法：

            bot = Bot(...)

            @on_group_message
            async def handle_group(event, bot):
                ...

            bot.run()
        """
        try:
            asyncio.run(self._run_main())
        except KeyboardInterrupt:
            logger.info(f"asa bot 退出")

    def load(self,
            spec: Union[PluginSpec, PluginPath, Iterable[PluginSpec]],
            config: PluginConfig | None = None) -> Any:
        """加载插件的统一接口。

         支持以下调用方式：
         - bot.load("plugins.weather")                    # 单个插件，无配置
         - bot.load("plugins.weather", {"key": "value"})  # 单个插件，有配置
         - bot.load(("plugins.weather", {"key": "val"}))  # 单个插件元组形式
         - bot.load(["plugins.weather", "plugins.admin"]) # 批量加载
         - bot.load([("plugins.weather", conf), ...])     # 批量加载带配置
         """
        try:
            return self.plugin_manager.load(spec, config)
        except RuntimeError:
            logger.warning(f"插件加载失败: {spec!r}")




AsaBot = Bot

__all__ = ["Bot", "AsaBot"]
