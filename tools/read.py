from pathlib import Path

from .base import Tool


MAX_READ_CHARS = 50000


def resolve_workspace_path(path: str) -> Path:
    workspace = Path.cwd().resolve()
    candidate = (workspace / path).resolve()

    try:
        candidate.relative_to(workspace)
    except ValueError as exc:
        raise ValueError("Path is outside the workspace") from exc

    return candidate


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
