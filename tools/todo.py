from typing import Any

from .base import Tool
from todo import TodoItem, TodoManager, TodoStatus


TODO_ACTIONS = ["add", "update", "remove", "read"]
TODO_STATUSES = [status.value for status in TodoStatus]


def format_todo_item(item: TodoItem, idx: int) -> str:
    if item.content:
        return f"{idx}. [{item.status}] {item.title}: {item.content}"
    return f"{idx}. [{item.status}] {item.title}"


def todo_handler(tool_input: dict[str, Any], runtime) -> str:
    if runtime is None:
        return "Error: todo tool requires an active runtime session"

    manager: TodoManager = runtime.session.todo_manager
    action = str(tool_input["action"]).strip().lower()

    if action == "read":
        status = tool_input.get("status")
        items = manager.list_items(status=status) if status is not None else None
        return manager.render_text(items)

    if action == "add":
        title = str(tool_input.get("title", "")).strip()
        if not title:
            return "Error: title is required for add"

        content = str(tool_input.get("content", "")).strip()
        status = tool_input.get("status", "pending")
        manager.add_item(title=title, content=content, status=status)
        items = manager.list_items()
        new_index = len(items)
        return f"Added todo {format_todo_item(items[-1], new_index)}\n\n{manager.render_text()}"

    if action == "update":
        idx = tool_input.get("idx")
        if idx is None:
            return "Error: idx is required for update"

        title = tool_input.get("title")
        content = tool_input.get("content")
        status = tool_input.get("status")
        if title is None and content is None and status is None:
            return "Error: provide at least one of title, content, or status for update"

        updated = manager.update_item(
            idx=int(idx),
            title=str(title) if title is not None else None,
            content=str(content) if content is not None else None,
            status=str(status) if status is not None else None,
        )
        return f"Updated todo {format_todo_item(updated, int(idx))}\n\n{manager.render_text()}"

    if action == "remove":
        idx = tool_input.get("idx")
        if idx is None:
            return "Error: idx is required for remove"

        removed = manager.remove_item(int(idx))
        return f"Removed todo {format_todo_item(removed, int(idx))}\n\n{manager.render_text()}"

    valid_actions = ", ".join(TODO_ACTIONS)
    return f"Error: invalid action: {action}. Valid actions: {valid_actions}"


TODO_TOOL = Tool(
    name="todo",
    description="Read and manage the current session todo list.",
    input_schema={
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": TODO_ACTIONS,
                "description": "The todo action to perform: add, update, remove, or read.",
            },
            "idx": {
                "type": "integer",
                "description": "The 1-based todo item index to update or remove.",
            },
            "title": {
                "type": "string",
                "description": "The todo title to create or update.",
            },
            "content": {
                "type": "string",
                "description": "The todo details to create or update.",
            },
            "status": {
                "type": "string",
                "enum": TODO_STATUSES,
                "description": "The todo status to set or use as a read filter.",
            },
        },
        "required": ["action"],
    },
    handler=todo_handler,
)
