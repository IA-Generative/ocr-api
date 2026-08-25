import base64
from unittest.mock import MagicMock

import pytest
from hvac.exceptions import Forbidden

from src.connector.encryption.vault_provider import VaultEncryptionProvider


def _provider_with_mock_client() -> tuple[VaultEncryptionProvider, MagicMock]:
    client = MagicMock()
    provider = VaultEncryptionProvider(
        vault_addr="http://vault.local",
        vault_token="root-token",
        transit_key_name="ocr-api-task-content",
        client=client,
    )
    return provider, client


def test_encrypt_calls_transit_encrypt_endpoint():
    provider, client = _provider_with_mock_client()
    client.secrets.transit.encrypt_data.return_value = {"data": {"ciphertext": "vault:v1:ciphertexthere"}}

    ciphertext = provider.encrypt("hello world")

    assert ciphertext == "vault:v1:ciphertexthere"
    client.secrets.transit.encrypt_data.assert_called_once_with(
        name="ocr-api-task-content",
        plaintext=base64.b64encode(b"hello world").decode("utf-8"),
        mount_point="transit",
    )


def test_decrypt_calls_transit_decrypt_endpoint():
    provider, client = _provider_with_mock_client()
    encoded_plaintext = base64.b64encode(b"hello world").decode("utf-8")
    client.secrets.transit.decrypt_data.return_value = {"data": {"plaintext": encoded_plaintext}}

    plaintext = provider.decrypt("vault:v1:ciphertexthere")

    assert plaintext == "hello world"
    client.secrets.transit.decrypt_data.assert_called_once_with(
        name="ocr-api-task-content",
        ciphertext="vault:v1:ciphertexthere",
        mount_point="transit",
    )


def test_vault_error_response_raises():
    provider, client = _provider_with_mock_client()
    client.secrets.transit.encrypt_data.side_effect = Forbidden("permission denied")

    with pytest.raises(ValueError):
        provider.encrypt("hello")


@pytest.mark.parametrize(
    "kwargs",
    [
        {"vault_addr": "", "vault_token": "t", "transit_key_name": "k"},
        {"vault_addr": "http://vault.local", "vault_token": "", "transit_key_name": "k"},
        {"vault_addr": "http://vault.local", "vault_token": "t", "transit_key_name": ""},
    ],
)
def test_missing_required_config_raises(kwargs):
    with pytest.raises(ValueError):
        VaultEncryptionProvider(**kwargs)
