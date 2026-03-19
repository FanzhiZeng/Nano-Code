# RUNNING

## 当前目标

让当前项目从“具备基础任务规划能力的 coding agent”继续推进到“更稳定、更可控的 coding agent”。

按照最新的 [README.md](/home/luo/project/nano_code/README.md) 和 [todo.md](/home/luo/project/nano_code/todo.md)，当前版本已经具备对话、工具调用、读写文件、基础网页搜索和会话级 todo 任务规划能力。下一轮工作的重点不再是把 todo 能力“接上”，而是验证规划策略的稳定性，并继续补安全、测试和上下文控制。

## 当前代码状态

已经具备：

- `Anthropic` SDK 多轮对话
- `tool_use` / `tool_result` 循环
- 统一工具抽象、注册和分发
- `bash`、`read_file`、`write_file`、`web_search`、`todo`
- `AgentSession` / `AgentRuntime`
- `TodoManager` 和会话级 todo 列表
- system prompt 中的 todo 摘要注入
- “每次收到新任务先规划 todo，再执行”的基础约束
- 启动配置校验、日志落盘、异常兜底
- 前台按“模型中间输出 -> 工具状态 -> 最终回答”的顺序展示

当前主入口的大致职责边界是：

- [main.py](/home/luo/project/nano_code/main.py) 中的 `agent_loop()` 负责一次请求内的模型调用和工具回填循环
- [main.py](/home/luo/project/nano_code/main.py) 中的 `run()` 负责命令行输入和会话历史维护
- [agent_runtime.py](/home/luo/project/nano_code/agent_runtime.py) 负责组织运行时依赖和会话状态
- [todo.py](/home/luo/project/nano_code/todo.py) 负责 todo 状态管理
- [tools/todo.py](/home/luo/project/nano_code/tools/todo.py) 负责将 todo 状态暴露给模型

目前主要短板：

- `main.py` 仍然偏重，函数边界虽然比以前更清楚，但还没有真正拆出模块
- system prompt 只是在策略层要求“先规划后执行”，还没有在程序层强制校验
- 还没有观察真实对话中 `todo` 使用是否稳定，可能出现模型漏调或过度更新
- 工具层日志和错误表达还不够统一
- `bash`、`write_file`、`web_search` 的安全和错误处理仍然偏粗
- 没有测试，也没有上下文选择能力

## 本轮范围

下一轮建议聚焦三件事：

1. 验证并稳定 `todo` 规划策略
2. 继续收口 [main.py](/home/luo/project/nano_code/main.py) 中的主循环和编排逻辑
3. 对齐工具层日志、错误表达和基础安全边界

本轮不做：

- 大规模模块重构
- 自动扫描整个项目后注入上下文
- 更复杂的文件编辑协议

## 具体事项

### 1. 验证 `todo` 规划策略

目标：

- 观察模型是否会在每个新任务开始时先调用 `todo`
- 确认 todo 项拆解粒度合理，不会过粗或过细
- 评估是否需要在代码层增加更强的约束或兜底

验收点：

- 多步骤请求会先生成 todo，再执行其他工具
- 模型在任务推进时会更新状态，而不是只新增不维护
- todo 规划不会明显干扰现有工具调用闭环

### 2. 继续收口主循环

当前问题：

- `agent_loop()` 仍然同时处理模型请求、文本打印、工具状态输出、工具执行和 `tool_result` 回填
- `run()` 已经从命名上和 `agent_loop()` 分开，但主入口仍集中在一个文件里

要做的事：

- 继续提取消息构造和系统提示相关逻辑
- 给后续上下文选择和更复杂的规划逻辑留出边界
- 避免 `main.py` 继续堆积 prompt、打印和编排细节

验收点：

- `agent_loop()` 更短，职责更单一
- 接入更多上下文逻辑时不需要继续堆在主循环里
- 工具失败不会导致进程退出

### 3. 补齐日志、错误表达和安全边界

目标：

- 工具调用开始时记录工具名和入参摘要
- 工具完成时记录结果长度、命中数或条目数
- 工具失败时记录明确错误
- 统一工具层返回格式，区分成功、失败和摘要信息
- 继续收紧 `bash`、`write_file`、`web_search` 的边界

验收点：

- 日志里能快速看出一次请求做了什么
- 工具失败时前台和日志都能给出可读信息
- 工具层行为更稳定，不依赖主循环做过多兜底

## 建议实施顺序

1. 先验证 `todo` 规划策略的真实表现
2. 再整理 `agent_loop()` 和 prompt 相关边界
3. 然后统一工具层日志和返回格式
4. 最后补基础安全限制和错误分类

## 手动验证

建议至少验证下面这些场景：

1. 给一个多步骤请求，确认任务会先写入 todo 再执行
2. 连续发送两个不同任务，确认 todo 会被更新而不是完全失控累积
3. 问“读取 README.md”，确认现有 `read_file` 仍正常工作
4. 让模型执行需要写文件的任务，确认 `write_file` 仍可用
5. 给一个错误路径或异常输入，确认工具失败会回传模型而不是中断程序
6. 问一个需要 shell 的问题，确认 `bash` 仍然可用且日志完整

## 下一步衔接

这一轮接入 todo 后，下一阶段优先考虑：

- 启动时采集项目文件结构
- 根据用户问题挑选相关文件片段加入上下文
- 控制上下文长度
- 提供更细的文件编辑协议，而不是依赖整文件重写
