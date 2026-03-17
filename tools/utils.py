from pathlib import Path


def resolve_workspace_path(path: str) -> Path:
    workspace = Path.cwd().resolve()
    candidate = (workspace / path).resolve()

    try:
        candidate.relative_to(workspace)
    except ValueError as exc:
        raise ValueError("Path is outside the workspace") from exc

    return candidate
