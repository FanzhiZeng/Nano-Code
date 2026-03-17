from pathlib import Path

from .base import Tool
from .utils import resolve_workspace_path


MAX_READ_CHARS = 50000


def read_file(path: str) -> str:
    target = resolve_workspace_path(path)

    if not target.exists():
        return f"Error: File not found: {path}"
    if not target.is_file():
        return f"Error: Not a file: {path}"

    content = target.read_text(encoding="utf-8")
    return content[:MAX_READ_CHARS]


def read_handler(tool_input: dict[str, str]) -> str:
    path = tool_input["path"]
    return read_file(path)


READ_TOOL = Tool(
    name="read_file",
    description="Read a text file from the current workspace.",
    input_schema={
        "type": "object",
        "properties": {"path": {"type": "string"}},
        "required": ["path"],
    },
    handler=read_handler,
)
