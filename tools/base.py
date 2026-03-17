from dataclasses import dataclass
from typing import Any, Callable

ToolHandler = Callable[[dict[str, Any]], str]

@dataclass
class Tool:
    name: str
    description: str
    input_schema: dict[str, Any]
    handler: ToolHandler