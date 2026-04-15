from pydantic_settings import BaseSettings, SettingsConfigDict


class ClassificationSettings(BaseSettings):
    ENABLED: bool = False
    CLIP_MODEL_DIR: str = "/app/models/clip"
    MODEL_NAME: str = "RN50"
    model_config = SettingsConfigDict(from_attributes=True, case_sensitive=True, env_file=".env", extra="allow")
