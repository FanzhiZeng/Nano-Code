from .base import Tool
from .bash import BASH_TOOL
from .read_file import READ_TOOL
from .todo import TODO_TOOL
from .web_search import WEB_SEARCH_TOOL
from .write_file import WRITE_TOOL


TOOLS = [BASH_TOOL, READ_TOOL, WEB_SEARCH_TOOL, WRITE_TOOL, TODO_TOOL]

def get_tool_definitions(tools: list[Tool] | None = None) -> list[dict]:
    tool_list = TOOLS if tools is None else tools
    return [
        {
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.input_schema,
        }
        for tool in tool_list
    ]


def build_tool_registry(tools: list[Tool] | None = None) -> dict[str, Tool]:
    tool_list = TOOLS if tools is None else tools
    return {tool.name: tool for tool in tool_list}


def execute_tool(
    tool_name: str,
    tool_input: dict,
    tool_registry: dict[str, Tool] | None = None,
    runtime=None,
) -> str:
    registry = build_tool_registry() if tool_registry is None else tool_registry
    tool = registry.get(tool_name)
    if tool is None:
        return f"Error: Unknown tool: {tool_name}"

    try:
        return tool.handler(tool_input, runtime)
    except Exception as exc:
        return f"Error: {exc}"
