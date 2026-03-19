from dataclasses import dataclass
import logging
from pathlib import Path

from anthropic import Anthropic

from todo import TodoManager


@dataclass
class AgentSession:
    history: list[dict]
    todo_manager: TodoManager


@dataclass
class AgentRuntime:
    client: Anthropic
    model_id: str
    logger: logging.Logger
    workspace_root: Path
    session: AgentSession