import os

from cryptography.fernet import Fernet, InvalidToken

from .base import EncryptionProvider


class LocalEncryptionProvider(EncryptionProvider):
    """Chiffrement symétrique local (AES via Fernet).

    La clé vit dans la config de l'app (ENCRYPTION_KEY) — pas de rotation ni d'audit trail
    centralisé. Suffisant pour un premier chiffrement au repos ; à remplacer par un
    VaultEncryptionProvider (Vault Transit) si une gestion de clés centralisée/rotation
    devient nécessaire, sans changer les appelants (interface EncryptionProvider commune).
    """

    def __init__(self, key: str | None = None):
        key = key or os.environ.get("ENCRYPTION_KEY")
        if not key:
            raise ValueError(
                "ENCRYPTION_KEY is required for LocalEncryptionProvider. "
                "Generate one with LocalEncryptionProvider.generate_key()."
            )
        try:
            self._fernet = Fernet(key.encode("utf-8"))
        except (ValueError, TypeError) as e:
            raise ValueError("ENCRYPTION_KEY is not a valid Fernet key") from e

    def encrypt(self, plaintext: str) -> str:
        return self._fernet.encrypt(plaintext.encode("utf-8")).decode("utf-8")

    def decrypt(self, ciphertext: str) -> str:
        try:
            return self._fernet.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
        except InvalidToken as e:
            raise ValueError("Failed to decrypt: invalid token or wrong ENCRYPTION_KEY") from e

    @staticmethod
    def generate_key() -> str:
        return Fernet.generate_key().decode("utf-8")
