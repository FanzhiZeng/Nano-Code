from dataclasses import dataclass

@dataclass
class Config:
    api_key: str
    model_id: str
    base_url: str | None = None