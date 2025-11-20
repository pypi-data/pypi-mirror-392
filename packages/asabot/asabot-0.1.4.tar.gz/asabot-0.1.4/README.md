# asabot（asa）—— 为 NapCat 设计的现代化 QQ 机器人框架

一个基于 OneBot 11 协议、面向 [NapCat](https://github.com/NapNeko/NapCat) 的 Python 异步 QQ 机器人框架。

- **项目名（安装）**: `asabot`
- **包名（导入）**: `asa`
- **Python 要求**: `>=3.13`

## ✨ 设计哲学与核心特性

- 🔌 **插件化设计**: 通过简单的配置文件 `plugins.toml` 即可管理所有插件的加载、卸载与配置。
- 🔥 **配置热重载**: 无需重启机器人，修改 `plugins.toml` 即可动态更新插件行为，极大提升开发和调试效率。
- 🎯 **条件路由 DSL**: 使用 ` @on_keyword("天气")` 这样直观的装饰器来描述事件触发条件，支持灵活组合。
- 📦 **开箱即用**: 提供清晰的项目结构建议和丰富的 API，让你专注于业务逻辑而非底层实现。
- 🛡️ **严格配置**: 关键配置（如 NapCat 地址和 Token）必须显式提供，避免隐式默认值带来的问题。
- 🤖 **OneBot 11 兼容**: 事件结构和 API 设计紧密贴合 OneBot 11 标准，并针对 NapCat 的特性进行优化。

> **适用场景**: 期望用现代 Python 工具链（异步、类型提示）快速开发功能丰富、易于维护的 QQ 机器人。

---

## 🚀 快速上手

### 1. 安装

```bash
# 建议使用 uv 或其它虚拟环境
uv pip install asabot
```

### 2. 配置 NapCat 连接

`asabot` 需要连接到一个正在运行的 OneBot 11 服务（如 NapCat）。

在你的项目根目录创建一个 `.env` 文件，并填入以下内容：
```env
# .env

# NapCat 的 WebSocket 事件上报地址
WS_URL="ws://127.0.0.1:3001"

# NapCat 的 HTTP API 调用地址
HTTP_URL="http://127.0.0.1:3000"

# NapCat 的访问令牌 (Token)
NAPCAT_TOKEN="YOUR_SECRET_TOKEN"
```
框架会自动加载 `.env` 文件。

### 3. 推荐项目结构

```text
your_project/
├── plugins/
│   ├── __init__.py
│   └── echo.py           # 你的第一个插件
├── .env                  # NapCat 配置文件
├── plugins.toml          # 插件管理文件
└── main.py               # 主入口文件
```

### 4. 创建你的第一个插件

`plugins/echo.py`:
```python
from asa import on_keyword, Bot
from asa.event import MessageEvent

# 使用 @on_keyword 装饰器来响应包含特定关键词的消息
@on_keyword("ping")
async def handle_ping(event: MessageEvent, bot: Bot):
    # event.text 包含消息的纯文本内容
    # bot.reply 是一个便捷 API，可以自动回复到消息来源（群或私聊）
    await bot.reply("pong!", at_sender=True) # at_sender=True 会 @ 消息发送者

@on_keyword("你是谁")
async def handle_who_are_you(event: MessageEvent, bot: Bot):
    # bot.account_nickname 缓存了当前登录的机器人昵称
    await bot.reply(f"我是 {bot.account_nickname} ~")
```

### 5. 配置并启用插件

`plugins.toml`:
```toml
# plugins.toml

# 所有插件都定义在 [plugins] 表下
[plugins]

  # key 是插件的 "target"
  # 对于模块插件，就是 Python 的模块路径
  [plugins."plugins.echo"]
  enabled = true  # 启用这个插件
```

### 6. 编写主入口文件

`main.py`:
```python
from asa import Bot
from asa.plugin.config import PluginConfigManager

if __name__ == "__main__":
    # 1. 创建插件配置管理器，它会自动读取 plugins.toml
    plugin_config = PluginConfigManager(auto_scan=True)
    
    # 2. 启动文件监听，实现热重载 (开发时非常有用)
    plugin_config.start_watch()

    # 3. 创建机器人实例，传入插件配置管理器
    #    框架会自动从 .env 加载 NapCat 连接配置
    bot = Bot(plugin_config_manager=plugin_config)

    # 4. 运行机器人
    print("Bot is running...")
    bot.run()
```

### 7. 运行！

```bash
python main.py
```
现在，向你的机器人或它所在的群发送 "ping"，它就会回复 "pong!"。

---

## 🧩 插件系统详解

插件是 `asabot` 的核心。框架通过 `plugins.toml` 文件来管理插件，支持模块插件和类插件。

### 模块插件（推荐）

模块插件是一个 Python 模块，其中的处理器函数由装饰器标记。这是最简单和直接的方式。

`plugins/weather.py`:
```python
from asa import on_keyword, Bot, MessageEvent

# 可以在插件模块顶层定义一个 __setup__ 函数
# 它会在插件加载时被调用，并接收插件配置
def __setup__(bot: Bot, api_key: str, **kwargs):
    print(f"Weather 插件已加载，API Key: {api_key}")

@on_keyword("天气")
async def weather_handler(event: MessageEvent, bot: Bot):
    # 在这里实现你的天气查询逻辑
    await bot.reply("今天天气晴朗~")
```

`plugins.toml`:
```toml
[plugins]
  [plugins."plugins.weather"]
  enabled = true
  # 在这里为插件提供配置
  api_key = "your_secret_weather_api_key"
```

### 类插件（适用于复杂场景）

当插件需要维护自身状态时，可以使用类插件。

`plugins/counter.py`:
```python
from asa import on_keyword, Bot, MessageEvent

class CounterPlugin:
    def __init__(self, initial_value: int = 0, **kwargs):
        # __init__ 接收插件配置
        self.count = initial_value
        print(f"Counter 插件已加载，初始值为 {self.count}")

    @on_keyword("计数")
    async def count_handler(self, event: MessageEvent, bot: Bot):
        self.count += 1
        await bot.reply(f"当前计数: {self.count}")
```

`plugins.toml`:
```toml
[plugins]
  # 类插件的 target 格式为 "模块路径:类名"
  [plugins."plugins.counter:CounterPlugin"]
  enabled = true
  initial_value = 100 # 配置会传递给 __init__
```

### 🔥 配置热重载

当你运行 `main.py` 后，可以尝试修改 `plugins.toml`：
- 将一个插件的 `enabled` 从 `true` 改为 `false` -> 插件及其功能会被立刻卸载。
- 修改插件的配置（如 `api_key` 或 `initial_value`） -> 插件会自动重载，并使用新的配置重新初始化。
- 添加一个新的插件配置 -> 新插件会被立刻加载。

这个特性在开发和调试时极为有用，无需反复重启机器人。

---

## 📡 事件系统 (`Event`)

框架会将 NapCat 上报的所有事件都包装成 `Event` 对象。

### 事件类型

`asa.event` 定义了与 OneBot 11 事件体系对应的类：
- `Event`: 所有事件的基类。
- `MessageEvent`: 消息事件，包含私聊和群聊。
- `NoticeEvent`: 通知事件（如群成员增加/减少）。
- `RequestEvent`: 请求事件（如加好友/加群请求）。
- `MetaEvent`: 元事件（如心跳）。

框架会根据事件的 `post_type` 自动创建正确的事件对象。在编写处理器时，**建议使用最精确的事件类型注解**，这可以提高性能，因为框架会跳过不匹配的事件类型，避免不必要的条件检查。

### 常用事件属性

对于一个 `MessageEvent` 实例 `event`：

- `event.raw`: 原始事件 `dict`。
- `event.post_type`: `'message'`
- `event.message_type`: `'private'` 或 `'group'`。
- `event.is_private`, `event.is_group`: 便捷的布尔判断。
- `event.message_id`: 消息 ID。
- `event.user_id`: 发送者 QQ 号。
- `event.group_id`: 群号（仅群聊）。
- `event.text`: 消息的纯文本内容。

---

## 🎯 条件装饰器

条件装饰器是 `asabot` 路由的核心，它们都基于 `Condition` 对象，可以灵活组合。

### 常用装饰器

```python
from asa import on_group_message, on_private_message, on_at_me, on_keyword, from_user, from_group
```

- **`@on_group_message` / `@on_private_message`**: 匹配群消息/私聊消息。
- **`@on_at_me`**: 匹配 @机器人的消息。
- **`@on_keyword(*keywords)`**: 消息文本包含任意一个关键字。
- **`@from_user([user_id1, ...])`**: 匹配来自指定用户的消息。
- **`@from_group([group_id1, ...])`**: 匹配来自指定群组的消息。

装饰器可以叠加使用，代表条件 "与" (AND) 的关系：
```python
@on_group_message
@on_keyword("晚安")
async def good_night(event: MessageEvent, bot: Bot):
    # 这个处理器只会在群里收到 "晚安" 时触发
    await bot.reply("晚安~")
```

### 优先级与事件传播

处理器支持 `priority` 参数，数字越大，优先级越高。
```python
from asa.event import StopPropagation

@on_keyword("黑名单", priority=100)
async def block_handler(event: MessageEvent, bot: Bot):
    # 这是一个高优先级处理器
    await bot.reply("禁止访问！")
    # 抛出 StopPropagation 来阻止事件继续传播给其他处理器
    raise StopPropagation

@on_keyword("黑名单", priority=0)
async def another_handler(event: MessageEvent, bot: Bot):
    # 因为上面的处理器阻断了事件，所以这里永远不会执行
    ...
```

---

## 🤖 `Bot` 实例 API

`Bot` 实例提供了丰富的 API 来与 QQ 交互。在处理器中，它可以作为第二个参数注入。

### 账号信息

- `bot.account_id`: 机器人自己的 QQ 号。
- `bot.account_nickname`: 机器人自己的昵称。

### 消息发送

- `await bot.send_private(user_id, message)`
- `await bot.send_group(group_id, message)`
- `await bot.reply(message, at_sender=False)`: 自动回复到事件来源。

### 其他操作
- `await bot.delete_message(message_id)`: 撤回消息。
- `await bot.ban_sender(event, duration=60)`: 根据事件禁言发送者（默认60秒）。
- `await bot.kick_sender(event)`: 根据事件踢出发送者。
- `await bot.adapter.call_action("action_name", **params)`: 调用任意 OneBot 11 API。