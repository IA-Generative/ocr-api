import base64
from typing import Optional

import hvac
from hvac.exceptions import VaultError

from .base import EncryptionProvider


class VaultEncryptionProvider(EncryptionProvider):
    """Chiffrement centralisé via le moteur Transit de HashiCorp Vault.

    La clé ne quitte jamais Vault : l'app lui envoie du texte en clair/chiffré et reçoit
    le résultat, Vault gère la clé, sa rotation et l'audit trail. Contrairement à
    LocalEncryptionProvider, aucun secret de chiffrement n'est stocké côté app (seulement
    un token Vault avec les droits encrypt/decrypt sur la clé).
    """

    def __init__(
        self,
        vault_addr: str,
        vault_token: str,
        transit_key_name: str,
        mount_path: str = "transit",
        namespace: Optional[str] = None,
        timeout: float = 5.0,
        client: Optional[hvac.Client] = None,
    ):
        if not vault_addr or not vault_token or not transit_key_name:
            raise ValueError("vault_addr, vault_token and transit_key_name are required for VaultEncryptionProvider")

        self._key_name = transit_key_name
        self._mount_path = mount_path.strip("/")
        self._client = client or hvac.Client(
            url=vault_addr,
            token=vault_token,
            namespace=namespace,
            timeout=timeout,
        )

    def encrypt(self, plaintext: str) -> str:
        encoded = base64.b64encode(plaintext.encode("utf-8")).decode("utf-8")
        try:
            response = self._client.secrets.transit.encrypt_data(
                name=self._key_name,
                plaintext=encoded,
                mount_point=self._mount_path,
            )
        except VaultError as e:
            raise ValueError(f"Vault transit encrypt failed: {e}") from e
        return response["data"]["ciphertext"]

    def decrypt(self, ciphertext: str) -> str:
        try:
            response = self._client.secrets.transit.decrypt_data(
                name=self._key_name,
                ciphertext=ciphertext,
                mount_point=self._mount_path,
            )
        except VaultError as e:
            raise ValueError(f"Vault transit decrypt failed: {e}") from e
        encoded = response["data"]["plaintext"]
        return base64.b64decode(encoded).decode("utf-8")
