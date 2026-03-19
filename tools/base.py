from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from agent_runtime import AgentRuntime

ToolHandler = Callable[[dict[str, Any], "AgentRuntime | None"], str]

@dataclass
class Tool:
    name: str
    description: str
    input_schema: dict[str, Any]
    handler: ToolHandler
