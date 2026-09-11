import pytest

from src.connector.encryption.local_provider import LocalEncryptionProvider


def test_encrypt_decrypt_roundtrip():
    key = LocalEncryptionProvider.generate_key()
    provider = LocalEncryptionProvider(key=key)

    ciphertext = provider.encrypt("hello world")

    assert ciphertext != "hello world"
    assert provider.decrypt(ciphertext) == "hello world"


def test_ciphertext_differs_between_keys():
    provider_a = LocalEncryptionProvider(key=LocalEncryptionProvider.generate_key())
    provider_b = LocalEncryptionProvider(key=LocalEncryptionProvider.generate_key())

    ciphertext = provider_a.encrypt("secret")

    with pytest.raises(ValueError):
        provider_b.decrypt(ciphertext)


def test_missing_key_raises(monkeypatch):
    monkeypatch.delenv("ENCRYPTION_KEY", raising=False)
    with pytest.raises(ValueError):
        LocalEncryptionProvider(key=None)


def test_invalid_key_raises():
    with pytest.raises(ValueError):
        LocalEncryptionProvider(key="not-a-valid-fernet-key")
