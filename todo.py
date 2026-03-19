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

    @staticmethod
    def parse_status(status: TodoStatus | str) -> TodoStatus:
        try:
            return TodoStatus(status)
        except ValueError as exc:
            valid = ", ".join(item.value for item in TodoStatus)
            raise ValueError(f"Invalid status: {status}. Valid values: {valid}") from exc

    def add_item(
        self,
        title: str,
        content: str,
        status: TodoStatus | str = TodoStatus.PENDING,
    ) -> TodoItem:
        now = datetime.now()
        item = TodoItem(
            title=title.strip(),
            content=content.strip(),
            status=self.parse_status(status),
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
            item.status = self.parse_status(status)
        item.updated_at = datetime.now()
        return item

    def remove_item(self, idx: int) -> TodoItem:
        item = self._get_item_by_number(idx)
        self._items.remove(item)

        return item

    def list_items(self, status: TodoStatus | str | None = None) -> list[TodoItem]:
        if status is None:
            return list(self._items)

        parsed_status = self.parse_status(status)
        return [item for item in self._items if item.status == parsed_status]

    def list_item(self, status: TodoStatus | str | None = None) -> list[TodoItem]:
        return self.list_items(status=status)

    def render_text(self, items: list[TodoItem] | None = None) -> str:
        if items is None:
            items = self._items

        if not items:
            return "No todo items."

        lines = ["Current todo status:"]
        for i, item in enumerate(items, start=1):
            lines.append(
                f"- {i}. [{item.status}] {item.title}: {item.content}"
            )
        return "\n".join(lines)

    def _get_item_by_number(self, number: int) -> TodoItem:
        if number <= 0 or number > len(self._items):
            raise ValueError("Invalid Index")

        # 1-based -> 0-based
        return self._items[number - 1]
