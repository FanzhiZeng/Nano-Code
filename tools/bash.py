import os
import subprocess

from .base import Tool


def run_bash(command: str) -> str:
    dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
    if any(d in command for d in dangerous):
        return "Error: Dangerous command blocked"
    try:
        r = subprocess.run(command, shell=True, cwd=os.getcwd(),
                           capture_output=True, text=True, timeout=120)
        out = (r.stdout + r.stderr).strip()
        return out[:50000] if out else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Timeout (120s)"


def bash_handler(tool_input: dict[str, str], runtime=None) -> str:
    command = tool_input["command"]
    return run_bash(command)


BASH_TOOL = Tool(
    name="bash",
    description="Execute a shell command in the current workspace.",
    input_schema={
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The shell command to run in the current workspace.",
            }
        },
        "required": ["command"],
    },
    handler=bash_handler,
)
