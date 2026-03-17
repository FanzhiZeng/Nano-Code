# Nano Code

一个简易版 Claude Code 的复现项目。

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

## 文档

- 总体待办见 [todo.md](/home/luo/project/nano_code/todo.md)
- 下一步执行说明见 [running.md](/home/luo/project/nano_code/running.md)
- 当前入口代码见 [main.py](/home/luo/project/nano_code/main.py)

## 参考

- [Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview)
