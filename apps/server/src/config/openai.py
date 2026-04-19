from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class OpenAISettings(BaseSettings):
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: Optional[str] = None  # Ex: https://api.openai.com/v1
    OPENAI_MODEL: str = "gpt-4o-mini"  # Alias used in .env — takes precedence when set
    OPENAI_VISION_MODEL: str = "mistral-small-3.2-24b-instruct-2506"
    EMBEDDINGS_MODEL: str = "text-embedding-3-small"

    model_config = SettingsConfigDict(from_attributes=True, case_sensitive=True, env_file=".env", extra="allow")
