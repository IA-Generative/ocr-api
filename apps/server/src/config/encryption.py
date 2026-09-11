from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class EncryptionSettings(BaseSettings):
    # "local" (clé symétrique dans la config) ou "vault" (Vault Transit, clé jamais dans l'app).
    ENCRYPTION_PROVIDER: str = "local"

    # Provider "local"
    ENCRYPTION_KEY: Optional[str] = None

    # Provider "vault"
    VAULT_ADDR: Optional[str] = None
    VAULT_TOKEN: Optional[str] = None
    VAULT_TRANSIT_KEY_NAME: Optional[str] = None
    VAULT_TRANSIT_MOUNT_PATH: str = "transit"
    VAULT_NAMESPACE: Optional[str] = None

    model_config = SettingsConfigDict(from_attributes=True, case_sensitive=True, env_file=".env", extra="allow")
