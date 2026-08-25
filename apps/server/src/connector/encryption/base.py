from abc import ABC, abstractmethod


class EncryptionProvider(ABC):
    """Chiffre/déchiffre du texte pour le stockage au repos.

    Une implémentation par backend de gestion de clés (local, Vault Transit, ...).
    Le reste de l'app ne dépend jamais du backend concret, seulement de cette interface,
    pour pouvoir remplacer le provider local par un provider Vault sans toucher au code
    appelant.
    """

    @abstractmethod
    def encrypt(self, plaintext: str) -> str: ...

    @abstractmethod
    def decrypt(self, ciphertext: str) -> str: ...
