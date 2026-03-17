import os
import subprocess

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

from agent_config import Config

from tools import execute_tool, get_tool_definitions

SYSTEM = f"You are a coding agent at {os.getcwd()}."
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


def call_request(client: Anthropic, messages: list[dict], model_id: str) -> list[dict]:
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

    logger = logging.getLogger(LOGGER_NAME)
    logger.debug("Sending request with %s messages", len(messages))

    while True:
        response = client.messages.create(
            system=SYSTEM,
            messages=messages,
            model=model_id,
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

        # Execute each tool call, collect results
        results = []
        for block in response.content:
            if block.type == "tool_use":
                print(format_tool_status(block, "Running"))
                logger.info("Running tool %s with input: %s", block.name, block.input)

                output = execute_tool(block.name, block.input)

                print(format_tool_status(block, "Finish"))
                logger.info("Tool %s output preview: %s", block.name, output[:1000])
                results.append({"type": "tool_result", "tool_use_id": block.id,
                                "content": output})
        messages.append({"role": "user", "content": results})

    return messages


def print_startup(config: Config, log_path: Path) -> None:
    print(f"Nano Code ready. Model: {config.model_id}")
    print(f"Log file: {log_path}")


def agent_loop(client: Anthropic, model_id: str) -> None:
    logger = logging.getLogger(LOGGER_NAME)
    history: list[dict] = []

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
        history.append({"role": "user", "content": query})

        try:
            history = call_request(client, history, model_id)
        except Exception as exc:
            history.pop()
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
    agent_loop(client, config.model_id)


if __name__ == "__main__":
    main()
