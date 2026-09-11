from src.connector.encryption.envelope import decrypt_json, encrypt_json, is_encrypted
from src.connector.encryption.local_provider import LocalEncryptionProvider


def _provider() -> LocalEncryptionProvider:
    return LocalEncryptionProvider(key=LocalEncryptionProvider.generate_key())


def test_encrypt_json_wraps_ciphertext_in_envelope():
    provider = _provider()

    envelope = encrypt_json(provider, {"text": "contenu sensible"})

    assert is_encrypted(envelope)
    assert envelope["ciphertext"] != "contenu sensible"


def test_encrypt_then_decrypt_roundtrip():
    provider = _provider()
    original = {"type": "ocr", "text": "contenu sensible", "pages": [1, 2, 3]}

    envelope = encrypt_json(provider, original)
    decrypted = decrypt_json(provider, envelope)

    assert decrypted == original


def test_none_passthrough():
    provider = _provider()

    assert encrypt_json(provider, None) is None
    assert decrypt_json(provider, None) is None


def test_decrypt_legacy_plaintext_returned_as_is():
    provider = _provider()
    legacy_value = {"type": "ocr", "text": "écrit avant activation du chiffrement"}

    assert decrypt_json(provider, legacy_value) == legacy_value


def test_is_encrypted_false_for_plain_dict():
    assert is_encrypted({"type": "ocr", "text": "..."}) is False
    assert is_encrypted(None) is False
    assert is_encrypted("not-a-dict") is False
