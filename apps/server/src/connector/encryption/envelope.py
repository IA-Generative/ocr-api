import json
from typing import Any, Optional

from .base import EncryptionProvider

ENVELOPE_MARKER = "__enc__"
ENVELOPE_VERSION = "v1"


def is_encrypted(value: Any) -> bool:
    return isinstance(value, dict) and value.get(ENVELOPE_MARKER) == ENVELOPE_VERSION


def encrypt_json(provider: EncryptionProvider, value: Optional[dict]) -> Optional[dict]:
    """Sérialise `value` en JSON puis chiffre le tout en un seul blob, dans une enveloppe
    {"__enc__": "v1", "ciphertext": "..."}. Le format exposé par l'API (le modèle Pydantic
    validé à partir de la donnée déchiffrée) ne change pas : seul le stockage change."""
    if value is None:
        return None
    ciphertext = provider.encrypt(json.dumps(value))
    return {ENVELOPE_MARKER: ENVELOPE_VERSION, "ciphertext": ciphertext}


def decrypt_json(provider: EncryptionProvider, value: Optional[dict]) -> Optional[dict]:
    """Déchiffre une enveloppe produite par `encrypt_json`. Une valeur sans enveloppe est
    une donnée legacy écrite avant l'activation du chiffrement : renvoyée telle quelle,
    sans erreur, pour rester lisible pendant la transition."""
    if value is None:
        return None
    if not is_encrypted(value):
        return value
    return json.loads(provider.decrypt(value["ciphertext"]))
