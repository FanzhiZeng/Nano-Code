from .base import Tool
from .bash import BASH_TOOL
from .read import READ_TOOL


TOOLS = [BASH_TOOL, READ_TOOL]

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
) -> str:
    registry = build_tool_registry() if tool_registry is None else tool_registry
    tool = registry.get(tool_name)
    if tool is None:
        return f"Error: Unknown tool: {tool_name}"

    try:
        return tool.handler(tool_input)
    except Exception as exc:
        return f"Error: {exc}"
