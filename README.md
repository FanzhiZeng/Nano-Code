# Nano Code

一个简易版 Claude Code 的复现项目。

当前版本已经具备最小工具调用闭环：

- 支持多轮对话
- 支持 Anthropic `tool_use` / `tool_result` 循环
- 内置一个实验性的 `bash` 工具
- 前台会先显示模型中间话术，再显示 `[Running]` / `[Finish]` 工具状态，最后显示最终回答

## 快速开始

```bash
uv sync
cp .env.example .env
uv run python main.py
```

## 配置

- `ANTHROPIC_API_KEY`
- `ANTHROPIC_BASE_URL`
- `MODEL_ID`

环境变量模板见 [.env.example](/home/luo/project/nano_code/.env.example)。
运行日志默认写入 `logs/` 目录。

## 文档

- 总体待办见 [todo.md](/home/luo/project/nano_code/todo.md)
- 下一步执行说明见 [running.md](/home/luo/project/nano_code/running.md)
- 当前入口代码见 [main.py](/home/luo/project/nano_code/main.py)

## 当前限制

- 目前只有一个硬编码的 `bash` 工具
- 工具注册、权限控制和路径约束还没有抽象出来
- 代码仍集中在 `main.py`，还没有拆成模块

## 参考

- [Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview)
- [Claude API Docs](https://platform.claude.com/docs/en/api/overview)
