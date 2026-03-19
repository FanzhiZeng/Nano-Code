import os

import logging
from datetime import datetime
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

from agent_config import Config
from agent_runtime import AgentRuntime, AgentSession
from todo import TodoManager

from tools import execute_tool, get_tool_definitions

BASE_SYSTEM = (
    f"You are a coding agent at {os.getcwd()}.\n"
    "Use the available tools when needed.\n"
    "For every new user task, use the todo tool first to create or update a plan before doing any other work.\n"
    "Break the task into clear todo items, then execute the task.\n"
    "Keep the todo list updated as work progresses, especially when starting, completing, blocking, or changing a step.\n"
    "Do not skip todo planning, even when the task seems simple."
)
LOGGER_NAME = "nano_code"


TOOLS = get_tool_definitions()


def extract_text_from_blocks(content_blocks) -> str:
    parts = []
    for block in content_blocks:
        if getattr(block, "type", None) == "text":
            parts.append(block.text)
    return "".join(parts).strip()


def print_assistant_message(content_blocks) -> None:
    text = extract_text_from_blocks(content_blocks)
    if text:
        print(f"\n{text}\n")


def format_tool_status(block, status: str) -> str:
    tool_name = getattr(block, "name", "tool")
    return f"[{status}]: {tool_name}"


def build_system_prompt(runtime: AgentRuntime) -> str:
    todo_summary = runtime.session.todo_manager.render_text()
    return f"{BASE_SYSTEM}\n\nCurrent session todos:\n{todo_summary}"


def setup_logging() -> Path:
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    log_path = logs_dir / f"nano_code_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    logger.propagate = False

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    )
    logger.addHandler(file_handler)

    logger.debug("Logger initialized")
    return log_path


def load_config() -> Config:
    load_dotenv()

    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    model_id = os.getenv("MODEL_ID", "").strip()
    base_url = os.getenv("ANTHROPIC_BASE_URL", "").strip() or None

    missing = []
    if not api_key:
        missing.append("ANTHROPIC_API_KEY")
    if not model_id:
        missing.append("MODEL_ID")

    if missing:
        names = ", ".join(missing)
        raise ValueError(
            f"Missing required environment variables: {names}. "
            "Copy .env.example to .env and fill them in."
        )

    config = Config(api_key=api_key, model_id=model_id, base_url=base_url)
    logging.getLogger(LOGGER_NAME).debug(
        "Configuration loaded: model_id=%s, base_url=%s",
        config.model_id,
        config.base_url or "<default>",
    )
    return config


def build_client(config: Config) -> Anthropic:
    kwargs = {"api_key": config.api_key}
    if config.base_url:
        kwargs["base_url"] = config.base_url

    logging.getLogger(LOGGER_NAME).info(
        "Initializing client with model_id=%s and base_url=%s",
        config.model_id,
        config.base_url or "<default>",
    )
    return Anthropic(**kwargs)


def execute_tool_block(block, runtime: AgentRuntime) -> dict:
    print(format_tool_status(block, "Running"))
    runtime.logger.info("Running tool %s with input: %s", block.name, block.input)

    output = execute_tool(block.name, block.input, runtime=runtime)

    print(format_tool_status(block, "Finish"))
    runtime.logger.info("Tool %s output preview: %s", block.name, output[:1000])
    return {"type": "tool_result", "tool_use_id": block.id, "content": output}


def collect_tool_results(response, runtime: AgentRuntime) -> list[dict]:
    results = []
    for block in response.content:
        if block.type == "tool_use":
            results.append(execute_tool_block(block, runtime))
    return results


def agent_loop(runtime: AgentRuntime) -> list[dict]:
    """
    The tooluse Loop
    The entire secret of an AI coding agent in one pattern:
    while stop_reason == "tool_use":
        response = LLM(messages, tools)
        execute tools
        append results
    +--------+      +-------+      +------------------+
    |  User  | ---> |  LLM  | ---> | Tool Dispatch    |
    | prompt |      |       |      | {                |
    +--------+      +---+---+      |   bash: run_bash |
                        ^           |   read: run_read |
                        |           |   write: run_wr  |
                        +-----------+   edit: run_edit |
                        tool_result | }                |
                                    +------------------+
                            (loop continues)
    This is the core loop: feed tool results back to the model
    until the model decides to stop.
    """

    logger = runtime.logger
    messages = runtime.session.history
    logger.debug("Sending request with %s messages", len(messages))

    while True:
        response = runtime.client.messages.create(
            system=build_system_prompt(runtime),
            messages=messages,
            model=runtime.model_id,
            tools=TOOLS,
            max_tokens=2048,
        )

        messages.append({
            "role": "assistant",
            "content": response.content,
        })

        if extract_text_from_blocks(response.content):
            logger.info("Assistant intermediate/final text generated")
            print_assistant_message(response.content)

        if response.stop_reason != "tool_use":
            break

        results = collect_tool_results(response, runtime)
        messages.append({"role": "user", "content": results})

    return messages


def print_startup(config: Config, log_path: Path) -> None:
    print(f"Nano Code ready. Model: {config.model_id}")
    print(f"Log file: {log_path}")


def run(runtime: AgentRuntime) -> None:
    logger = runtime.logger
    while True:
        try:
            query = input("> ").strip()
        except EOFError:
            logger.info("Session ended via EOF")
            print("\nBye.")
            break
        except KeyboardInterrupt:
            logger.info("Session interrupted by user")
            print("\nBye.")
            break

        if not query:
            continue

        logger.info("User input received: %s", query)
        runtime.session.history.append({"role": "user", "content": query})

        try:
            agent_loop(runtime)
        except Exception as exc:
            runtime.session.history.pop()
            logger.exception("Request failed")
            print("Request failed. Check the log file for details.")
            continue


def main() -> None:
    log_path = setup_logging()

    try:
        config = load_config()
    except ValueError as exc:
        logging.getLogger(LOGGER_NAME).exception("Configuration error")
        print(f"Configuration error: {exc}")
        raise SystemExit(1)

    print_startup(config, log_path)
    client = build_client(config)
    runtime = AgentRuntime(
        client=client,
        model_id=config.model_id,
        logger=logging.getLogger(LOGGER_NAME),
        workspace_root=Path.cwd().resolve(),
        session=AgentSession(history=[], todo_manager=TodoManager()),
    )
    run(runtime)


if __name__ == "__main__":
    main()
