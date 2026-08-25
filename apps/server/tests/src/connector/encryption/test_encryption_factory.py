import pytest

from src.config.encryption import EncryptionSettings
from src.connector.encryption.factory import create_encryption_provider
from src.connector.encryption.local_provider import LocalEncryptionProvider
from src.connector.encryption.vault_provider import VaultEncryptionProvider


def test_creates_local_provider_by_default():
    settings = EncryptionSettings(ENCRYPTION_PROVIDER="local", ENCRYPTION_KEY=LocalEncryptionProvider.generate_key())

    provider = create_encryption_provider(settings)

    assert isinstance(provider, LocalEncryptionProvider)


def test_creates_vault_provider():
    settings = EncryptionSettings(
        ENCRYPTION_PROVIDER="vault",
        VAULT_ADDR="http://vault.local",
        VAULT_TOKEN="root-token",
        VAULT_TRANSIT_KEY_NAME="ocr-api-task-content",
    )

    provider = create_encryption_provider(settings)

    assert isinstance(provider, VaultEncryptionProvider)


def test_vault_provider_missing_config_raises():
    settings = EncryptionSettings(ENCRYPTION_PROVIDER="vault")

    with pytest.raises(ValueError):
        create_encryption_provider(settings)


def test_unknown_provider_raises():
    settings = EncryptionSettings(ENCRYPTION_PROVIDER="does-not-exist")

    with pytest.raises(ValueError):
        create_encryption_provider(settings)
