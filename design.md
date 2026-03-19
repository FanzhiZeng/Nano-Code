# Design

## 目标

为当前项目接入 `TodoManager`，让 agent 具备最小可用的任务规划能力，同时不破坏现有的：

- 多轮对话
- `tool_use -> tool_result` 闭环
- 文件读写和 shell 工具能力

本轮重点不是做复杂规划算法，而是先把“会话状态”和“任务状态”的架构边界立住。

## 核心设计

### 1. AgentSession 只保存会话状态

`AgentSession` 负责承载当前会话中的可变状态，不负责持有 SDK client。

建议字段：

- `history`
- `todo_manager`

示意：

```python
@dataclass
class AgentSession:
    history: list[dict]
    todo_manager: TodoManager
```

### 2. AgentRuntime 保存运行时依赖

运行时依赖和会话状态分开，避免后续扩展多 agent 时把状态和依赖耦合在一起。

建议字段：

- `client`
- `model_id`
- `logger`
- `workspace_root`
- `session`

示意：

```python
@dataclass
class AgentRuntime:
    client: Anthropic
    model_id: str
    logger: logging.Logger
    workspace_root: Path
    session: AgentSession
```

## TodoManager 设计

### 1. TodoItem

第一版只保留最小字段，不引入复杂逻辑。

建议字段：

- `title` // 标题
- `content` // 具体内容
- `status`
- `created_at`
- `updated_at`

状态建议：

- `pending`
- `in_progress`
- `completed`
- `blocked`
- `cancelled`

### 2. TodoManager 职责

`TodoManager` 只做确定性的状态管理，不做智能规划。

负责：

- 新增任务
- 更新任务描述
- 更新任务描述或状态
- 删除任务
- 查询任务列表
- 输出简短摘要给模型

不负责：

- 自动推断任务拆解
- 自动决定下一步执行什么
- 直接与模型 SDK 交互

### 3. 当前接口设计

第一版 `TodoManager` 采用尽量简单的接口，不引入稳定 `id`，而是直接使用任务在列表中的编号。

约定：

- 对外编号为 `1-based`
- 内部仍然使用 Python 列表存储
- 所有按编号访问的方法都由 `TodoManager` 负责做边界检查

当前公开接口可理解为：

```python
class TodoManager:
    def add_item(title, content, status=TodoStatus.PENDING) -> TodoItem: ...
    def update_item(idx, title=None, content=None, status=None) -> TodoItem: ...
    def remove_item(idx) -> TodoItem: ...
    def list_item(status=None) -> list[TodoItem]: ...
    def render_text(items=None) -> str: ...
```

说明：

- `add_item` 用于新增任务
- `update_item` 可以更新标题、内容，也可以顺带更新状态
- `remove_item` 按编号删除任务
- `list_item` 支持按状态筛选
- `render_text` 返回当前任务的纯文本摘要

## Tool 设计

### 1. 现有工具保留

保留以下工具：

- `bash`
- `read_file`
- `write_file`
- `web_search`

### 2. 新增 todo 相关工具

#### todo

用途：

- 访问和修改当前会话中的任务列表

第一版支持的操作建议包括：

- `add`
- `update` // 更新标题、内容或状态
- `remove`
- `read` // 返回当前所有todo信息

建议保持和当前 `TodoManager` 一致，不额外拆出 `set_status` 操作。

## Tool Runtime 设计

当前工具签名需要升级，避免 `todo` 工具依赖全局变量。

当前形式：

```python
handler(tool_input) -> str
```

建议改成：

```python
handler(tool_input, runtime) -> str
```

这样每个工具都能拿到：

- 当前 `session`
- 当前 `todo_manager`
- `logger`
- `workspace_root`

## run() 和 agent_loop() 的职责

### 1. run(runtime: AgentRuntime)

`run()` 只负责：

- 命令行输入输出
- 会话生命周期管理
- 把请求交给 `agent_loop()`

执行顺序：

```text
input -> append user message -> agent_loop(runtime) -> input
```

### 2. agent_loop(runtime: AgentRuntime)

`agent_loop()` 负责一次请求内的完整闭环。

建议执行顺序：

```text
build_messages(history + todo_summary)
-> messages.create()
-> print text
-> if tool_use:
     execute tools
     append tool_result
     continue loop
-> end
```

注意：

- `todo` 应该和其他工具一样，在同一个 `tool-use loop` 中执行

## build_context 

`build_context` 不应是一个模糊概念，建议拆成两部分：

- 构建消息历史
- 注入 `todo_manager.render_text()` 生成的任务摘要


## 建议的模块拆分

建议新增或调整以下模块：

- `agent_runtime.py`
- `todo.py`
- `tools/todo.py`

现有模块继续保留：

- `main.py`
- `tools/base.py`
- `tools/registry.py`

## 建议实现顺序

1. 实现 `TodoItem` 和 `TodoManager`
2. 引入 `AgentSession` 和 `AgentRuntime`
3. 修改工具签名，接入 `runtime`
4. 实现 `todo` 工具
5. 修改 `agent_loop()`，把 todo 摘要注入上下文
6. 补充日志和基础错误处理
