from .base import Tool
from .utils import resolve_workspace_path


def write_file(path: str, content: str) -> str:
    target = resolve_workspace_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return f"Wrote {len(content)} characters to {path}"


def write_handler(tool_input: dict[str, str], runtime=None) -> str:
    path = tool_input["path"]
    content = tool_input["content"]
    return write_file(path, content)


WRITE_TOOL = Tool(
    name="write_file",
    description="Write text content to a file in the current workspace.",
    input_schema={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The relative path of the file to write from the workspace root.",
            },
            "content": {
                "type": "string",
                "description": "The full text content to write into the target file.",
            },
        },
        "required": ["path", "content"],
    },
    handler=write_handler,
)
