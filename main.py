import os
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv


SYSTEM = f"You are a coding agent at {os.getcwd()}."
LOGGER_NAME = "nano_code"


@dataclass
class Config:
    api_key: str
    model_id: str
    base_url: str | None = None


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


def request_message(client: Anthropic, messages: list[dict], model_id: str) -> str:
    logger = logging.getLogger(LOGGER_NAME)
    logger.debug("Sending request with %s messages", len(messages))

    response = client.messages.create(
        system=SYSTEM,
        messages=messages,
        model=model_id,
        max_tokens=256,
    )

    text_parts = [
        block.text for block in response.content if getattr(block, "type", None) == "text"
    ]
    if not text_parts:
        raise RuntimeError("Model response did not contain text content.")

    content = "".join(text_parts).strip()
    logger.debug("Received response with %s characters", len(content))
    return content


def print_startup(config: Config, log_path: Path) -> None:
    print(f"Using model: {config.model_id}")
    if config.base_url:
        print(f"Using base URL: {config.base_url}")
    else:
        print("Using default Anthropic base URL")
    print(f"Logging to: {log_path}")


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
            content = request_message(client, history, model_id)
        except Exception as exc:
            history.pop()
            logger.exception("Request failed")
            print("Request failed. Check the log file for details.")
            continue

        print(content)
        logger.info("Assistant response: %s", content)
        history.append({"role": "assistant", "content": content})


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
