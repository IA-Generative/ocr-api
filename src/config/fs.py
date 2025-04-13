from pydantic_settings import BaseSettings, SettingsConfigDict


class FileSystemSettings(BaseSettings):
    FOLDER: str = "./tmp"
    model_config = SettingsConfigDict(
        from_attributes=True, case_sensitive=True, env_file=".env",  extra="allow"
    )
