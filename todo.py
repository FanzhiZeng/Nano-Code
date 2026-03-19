from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class TodoStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


@dataclass
class TodoItem:
    title: str
    content: str
    status: TodoStatus = TodoStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class TodoManager:
    def __init__(self, items: list[TodoItem] | None = None) -> None:
        self._items: list[TodoItem] = list(items) if items else []

    def add_item(
        self,
        title: str,
        content: str,
        status: TodoStatus = TodoStatus.PENDING,
    ) -> TodoItem:
        
        now = datetime.now()
        item = TodoItem(
            title=title.strip(),
            content=content.strip(),
            status=TodoStatus(status),
            created_at=now,
            updated_at=now,
        )

        self._items.append(item)

        return item

    def update_item(
        self,
        idx: int,
        title: str | None = None,
        content: str | None = None,
        status: TodoStatus | str | None = None,
    ) -> TodoItem:
        
        item = self._get_item_by_number(idx)
        if title is not None:
            item.title = title.strip()
        if content is not None:
            item.content = content.strip()
        if status is not None:
            if status not in TodoStatus:
                raise ValueError("Invalid Status")
            item.status = TodoStatus(status) 
        item.updated_at = datetime.now()
        return item

    def remove_item(self, idx: int) -> TodoItem:
        item = self._get_item_by_number(idx)
        self._items.remove(item)

        return item 

    def list_item(self, status: TodoStatus | str | None = None) -> list[TodoItem]:
        if status is None:
            return list(self._items)
        
        if status not in TodoStatus:
            raise ValueError("Invalid Status")

        return [item for item in self._items if item.status == status]

    def render_text(self, items: list[TodoItem] | None = None) -> str:
        if items is None:
            items = self._items

        if not items:
            return "No todo items."

        lines = ["Current todo status:"]
        for i, item in enumerate(items):
            lines.append(
                f"- {i + 1}. [{item.status}] {item.title}: {item.content}"
            )
        return "\n".join(lines)

    def _get_item_by_number(self, number: int):
        if number <= 0 or number > len(self._items):
            raise ValueError("Invalid Index")
        
        # 1-based -> 0-based
        return self._items[number - 1]