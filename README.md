# Nano Code

一个简化版的命令行 coding agent 项目，目标是复现 Claude Code。

当前版本已经支持：

- 多轮对话
- Anthropic `tool_use` / `tool_result` 循环
- 统一工具抽象、注册和分发
- 前台按“模型中间输出 -> 工具状态 -> 最终回答”的顺序展示
- 启动配置校验、日志落盘、异常兜底

## 当前已接入工具

- `bash`：执行 shell 命令
- `read_file`：读取工作区内文本文件
- `write_file`：写入工作区内文本文件
- `web_search`：返回简短网页搜索结果

工具定义和注册见 [tools/__init__.py](/home/luo/project/nano_code/tools/__init__.py) 和 [tools/registry.py](/home/luo/project/nano_code/tools/registry.py)。

## 快速开始

```bash
uv sync
cp .env.example .env
uv run python main.py
```

## 配置

需要配置以下环境变量：

- `ANTHROPIC_API_KEY`
- `ANTHROPIC_BASE_URL`
- `MODEL_ID`

环境变量模板见 [.env.example](/home/luo/project/nano_code/.env.example)。
运行日志默认写入 `logs/` 目录。

## 运行方式

启动后进入命令行交互：

```text
> 读取 README.md
> 当前目录有哪些 Python 文件
```

程序会维护会话历史，并在模型发起工具调用时自动执行工具，再将结果回填给模型继续推理。

## 项目结构

- [main.py](/home/luo/project/nano_code/main.py)：入口、日志、配置加载、主循环
- [agent_config.py](/home/luo/project/nano_code/agent_config.py)：配置数据结构
- [tools/base.py](/home/luo/project/nano_code/tools/base.py)：工具抽象
- [tools/registry.py](/home/luo/project/nano_code/tools/registry.py)：工具注册与执行
- [tools/bash.py](/home/luo/project/nano_code/tools/bash.py)：shell 工具
- [tools/read_file.py](/home/luo/project/nano_code/tools/read_file.py)：读文件工具
- [tools/write_file.py](/home/luo/project/nano_code/tools/write_file.py)：写文件工具
- [tools/web_search.py](/home/luo/project/nano_code/tools/web_search.py)：网页搜索工具
- [tools/utils.py](/home/luo/project/nano_code/tools/utils.py)：工作区路径限制
- [todo.md](/home/luo/project/nano_code/todo.md)：任务清单
- [running.md](/home/luo/project/nano_code/running.md)：当前迭代说明

## 文档

- 总体待办见 [todo.md](/home/luo/project/nano_code/todo.md)
- 当前迭代说明见 [running.md](/home/luo/project/nano_code/running.md)

## 参考

- [Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview)
- [Claude API Docs](https://platform.claude.com/docs/en/api/overview)
