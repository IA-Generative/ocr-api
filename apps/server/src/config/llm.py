import os
from typing import Any, Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.logger import logger

# Renamed fields: read the new (canonical) name, fall back to the deprecated
# one with a warning so the deploy side can migrate at its own pace.
_DEPRECATED_ENV_ALIASES = {
    "OPENAI_API_BASE_URL": "OPENAI_API_BASE",
    "OPENAI_VLM_MODEL_NAME": "VISION_MODEL_NAME",
}

# The LLM hub remaps this generic alias to whichever concrete engine is live.
# Falling back to a concrete engine name (e.g. "mistral-small-3.1-24b-instruct-2503")
# breaks the moment the hub decommissions or renames that engine.
GENERIC_VISION_ALIAS = "chat"


class OpenAISettings(BaseSettings):
    """Single source of truth for LLM configuration, read once by services.factory.load_worker."""

    OPENAI_API_KEY: str = ""
    OPENAI_API_BASE_URL: Optional[str] = None
    OPENAI_VLM_MODEL_NAME: str = GENERIC_VISION_ALIAS
    # Pure-text tasks (see business.llm.models.template.FormFieldExtractor); defaults
    # to the vision model so deployments that don't set it keep today's behavior.
    INSTRUCT_MODEL_NAME: Optional[str] = None

    model_config = SettingsConfigDict(from_attributes=True, case_sensitive=True, env_file=".env", extra="allow")

    @model_validator(mode="before")
    @classmethod
    def _apply_deprecated_env_aliases(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        for new_key, old_key in _DEPRECATED_ENV_ALIASES.items():
            if data.get(new_key) is None and os.environ.get(old_key) is not None:
                logger.warning(
                    "Environment variable %s is deprecated, use %s instead.",
                    old_key,
                    new_key,
                )
                data[new_key] = os.environ[old_key]

        return data

    @model_validator(mode="after")
    def _require_base_url(self) -> "OpenAISettings":
        if not self.OPENAI_API_BASE_URL:
            raise RuntimeError(
                "OPENAI_API_BASE_URL is not set. Refusing to silently send requests (and "
                "the API key) to the public OpenAI endpoint — set it explicitly to your LLM "
                "hub's base URL."
            )
        return self

    @property
    def instruct_model_name(self) -> str:
        return self.INSTRUCT_MODEL_NAME or self.OPENAI_VLM_MODEL_NAME
