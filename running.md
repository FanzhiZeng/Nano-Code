# RUNNING

## 当前目标

在现有 `tools/` 包基础上补齐第一批只读工具，并继续瘦身 `main.py`。当前项目已经有统一工具接口、注册表、`bash` 和 `read_file`，下一步重点是把“看代码库”常用能力补齐。

## 本轮范围

只做只读工具补齐和主循环整理。

包括：

- 保留现有 `bash` / `read_file` 工具能力
- 接入 `write_file`
- 接入 `search_text`
- 继续把 `call_request()` 中的工具细节拆出去
- 补齐工具日志和错误信息

不包括：

- 自动扫描项目上下文
- 大规模模块重构

## 具体事项

### 1. 把当前 `bash` 专用逻辑抽成通用工具接口

当前问题：

- 这一步已经基本完成
- 当前已有 [tools/base.py](/home/luo/project/nano_code/tools/base.py)、[tools/registry.py](/home/luo/project/nano_code/tools/registry.py)、[tools/bash.py](/home/luo/project/nano_code/tools/bash.py)、[tools/read.py](/home/luo/project/nano_code/tools/read.py)
- 但 `main.py` 里的 `call_request()` 仍然知道太多工具执行细节

要做的事：

- 保留现有工具接口不再大改
- 把“从响应中提取 tool_use 块”提成独立函数
- 把“执行单个工具并生成 tool_result”提成独立函数
- 让 `call_request()` 只负责循环和前台展示顺序

建议落点：

- [main.py](/home/luo/project/nano_code/main.py) 的 `call_request()`

### 2. 整理 `call_request()`，让它只负责循环，不负责知道每个工具细节

当前问题：

- 当前 `call_request()` 既负责：
  - 发请求
  - 打印中间文本
  - 打印工具状态
  - 调用通用工具执行器
  - 组装 `tool_result`
- 这会让它成为后续最容易失控的函数

要做的事：

- 保留 `call_request()` 对前台输出的控制
- 把“执行单个工具并返回 tool_result”提到独立函数
- 把“从响应中抽取所有 tool_use”提到独立函数
- 保持当前用户可见顺序：
  - 先显示模型中间话术
  - 再显示 `[Running]: ...`
  - 最后显示最终回答

建议实现方式：

- 这一轮可以继续留在 [main.py](/home/luo/project/nano_code/main.py)
- 但函数边界要继续切出来，后面再搬到独立 `agent` 模块

验收点：

- `call_request()` 不直接知道任何具体工具输入结构
- 新增工具时不需要再改主循环结构
- 工具名不存在时能返回清楚错误

### 3. 接入第一批只读工具

当前问题：

- 当前已有 `read_file`
- 但还缺两个高频只读工具：`list_dir` 和 `search_text`
- 没有这两个工具，模型仍会过度依赖 shell 来查看项目

要做的事：

- 实现 `list_dir`
  - 输入：`path`
  - 输出：目录下文件和子目录列表
- 实现 `read_file`
  - 输入：`path`
  - 输出：文件文本内容
- 实现 `search_text`
  - 输入：`pattern`、可选 `path`
  - 输出：匹配行结果

约束：

- 路径必须限制在当前工作区内
- 三个工具先只支持只读能力
- `search_text` 优先走 `rg`
- 输出要做长度控制，避免把整棵目录或超长文件直接塞回模型

验收点：

- 能列出项目根目录文件
- 能读取 `README.md`
- 能搜索到 `main.py` 中的 `agent_loop`

### 4. 保留并加强 `tool_result` 回填

当前问题：

- 当前已经能回填 `tool_result`
- 但回填逻辑仍放在 `main.py`，且工具状态输出和结果组装混在一起

要做的事：

- 遍历响应中的每个 `tool_use` 块
- 调用通用工具执行器拿到结果
- 生成对应的 `tool_result` 块，保留 `tool_use_id`
- 以新的 `user` 消息形式回填给模型
- 支持一轮中多个工具调用

验收点：

- 模型请求工具后，程序不会停在半路
- 工具结果会进入下一轮模型推理
- 如果工具失败，模型也能拿到错误结果，而不是程序中断

### 5. 文案和日志继续对齐当前交互风格

当前问题：

- 当前前台已采用“中间文本 -> Running/Finish -> 最终回答”
- 但工具日志仍偏粗
- `read_file`、后续 `list_dir`、`search_text` 需要更贴近工具本身的摘要字段

要做的事：

- 工具调用开始时写日志：工具名、入参摘要
- 工具成功时写日志：结果长度、命中数量或条目数
- 工具失败时写日志：异常细节
- 前台继续避免打印原始块结构和工具原始输出

建议前台策略：

- 模型有中间文本时先打印中间文本
- 工具执行时打印 `[Running]: ...`
- 工具结束时打印 `[Finish]: ...`
- 最后打印最终文本回答
- 详细内容全部进 `logs/`

### 6. 明确本轮完成标准

完成这一步后，程序应满足：

- 当前 `bash` 和 `read_file` 工具仍然可用
- 新增工具时不需要修改主循环的核心结构
- 用户问“查看 README 内容”时，模型可以优先调用 `read_file`
- 用户问“当前目录有哪些文件”时，模型可以优先调用 `list_dir`
- 用户问“哪里定义了 agent_loop”时，模型可以优先调用 `search_text`
- 工具执行过程前台输出简洁，详细过程写入日志文件
- 工具失败不会导致进程退出

## 建议实施顺序

1. 先实现 `list_dir`
2. 再实现 `search_text`
3. 然后继续拆 `call_request()` 里的工具结果组装
4. 最后补更细的日志和错误分类

## 手动验证

建议至少做下面 5 组检查：

1. 问一个需要 shell 的问题，确认当前 `bash` 工具仍可触发
2. 问“读取 README.md”，确认会优先触发 `read_file`
3. 问“当前目录有哪些文件”，确认会优先触发 `list_dir`
4. 给一个不存在的路径，确认工具失败会被记录并回传模型
5. 问“搜索 agent_loop 在哪里定义”，确认会优先触发 `search_text`

## 下一步衔接

这一步完成后，再进入写能力最合适。下一阶段优先做：

- 创建文件
- 定位并替换文件内容
- 受控 shell 命令执行

原因是只读工具已经能让模型理解代码库，下一步自然就是把“理解”推进到“修改和验证”。
