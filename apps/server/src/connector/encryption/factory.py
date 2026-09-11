from enum import Enum
from typing import Optional

from src.config.encryption import EncryptionSettings

from .base import EncryptionProvider
from .local_provider import LocalEncryptionProvider
from .vault_provider import VaultEncryptionProvider


class EncryptionProviderType(str, Enum):
    LOCAL = "local"
    # Chiffrement centralisé via Vault Transit (clé jamais dans l'app, rotation/audit
    # gérés par Vault) — préférable à "local" dès qu'une gestion de clés centralisée
    # est disponible en prod.
    VAULT = "vault"


def create_encryption_provider(settings: Optional[EncryptionSettings] = None) -> EncryptionProvider:
    settings = settings or EncryptionSettings()

    if settings.ENCRYPTION_PROVIDER == EncryptionProviderType.LOCAL:
        return LocalEncryptionProvider(key=settings.ENCRYPTION_KEY)

    if settings.ENCRYPTION_PROVIDER == EncryptionProviderType.VAULT:
        return VaultEncryptionProvider(
            vault_addr=settings.VAULT_ADDR,
            vault_token=settings.VAULT_TOKEN,
            transit_key_name=settings.VAULT_TRANSIT_KEY_NAME,
            mount_path=settings.VAULT_TRANSIT_MOUNT_PATH,
            namespace=settings.VAULT_NAMESPACE,
        )

    raise ValueError(f"Encryption provider '{settings.ENCRYPTION_PROVIDER}' not supported")
