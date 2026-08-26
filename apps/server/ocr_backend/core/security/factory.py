import logging
import os
import warnings
from ocr_backend.core.security.token import BaseVerifyToken, RequestContext
from keycloak import KeycloakOpenID

# Pas de `logging.basicConfig` ici : ce module est importé, pas un point d'entrée. L'appel
# était sans effet en production (le logger racine a déjà des handlers via sentry-sdk), ce
# qui rendait muette toute cette vérification et a masqué un incident d'authentification.
logger = logging.getLogger(__name__)


class AllowAllAccess(BaseVerifyToken):
    def __init__(self, verify_token=True):
        super().__init__(verify_token, is_fastapi=True)
        warnings.warn(message="YOU USE DEV MODE PLEASE DON'T USE THAT IN PRODUCTION")

    def verify(self, ctx: RequestContext) -> bool:
        ctx.user_id = "test_user"
        return True


class DevToken(BaseVerifyToken):
    def __init__(self):
        super().__init__(verify_token=True, is_fastapi=True)
        warnings.warn(message="YOU USE DEV MODE PLEASE DON'T USE THAT IN PRODUCTION")
        self.user_info = {
            "token1": RequestContext(user_id="test1", email="r@exemple.com", roles=[], token="token1"),
            "token2": RequestContext(user_id="test2", email="r@exemple.com", roles=[], token="token2"),
        }

    def verify(self, ctx: RequestContext):
        if ctx.token in self.user_info:
            current_user = self.user_info[ctx.token]
            return ctx.user_id == current_user.user_id

        return False


class ApiToken(BaseVerifyToken):
    def __init__(self):
        super().__init__(verify_token=True, is_fastapi=True)
        logger.info("Using API Token for verification")
        # TODO: use db or vault to store API keys and get user info associated with the key
        # Fail closed: an unset API_KEYS means no key is accepted, not a guessable default.
        self.__api_keys = {key.strip() for key in os.environ.get("API_KEYS", "").split(",") if key.strip()}
        logger.info("Loaded %d API key(s) for verification", len(self.__api_keys))

    def verify(self, ctx: RequestContext) -> bool:
        if ctx.token in self.__api_keys:
            ctx.user_id = "api_user"
            # `parse_header_context` alimente roles/is_admin depuis l'en-tête X-Roles, que
            # l'appelant contrôle. La branche Keycloak les réécrit depuis le jeton ; ici il
            # n'y a pas de jeton, donc on remet à zéro plutôt que de faire confiance.
            ctx.roles = []
            ctx.groups = []
            ctx.is_admin = False
            return True
        return False


class KeycloakToken(BaseVerifyToken):
    def __init__(self):
        super().__init__(verify_token=True, is_fastapi=True)
        logger.info("Using Keycloak for token verification")

        # Configuration Keycloak depuis les variables d'environnement
        self.keycloak_url = os.environ.get("KEYCLOAK_URL", "http://localhost:8080")
        self.realm_name = os.environ.get("KEYCLOAK_REALM", "master")
        self.client_id = os.environ.get("KEYCLOAK_CLIENT_ID", "your-client-id")
        self.keycloak_openid = KeycloakOpenID(
            server_url=self.keycloak_url,
            client_id=self.client_id,
            realm_name=self.realm_name,
            client_secret_key=os.environ.get("KEYCLOAK_CLIENT_SECRET", "secret"),
        )
        logger.debug("Keycloak URL: %s, Realm: %s, Client ID: %s", self.keycloak_url, self.realm_name, self.client_id)
        self.__api_token_verifier = ApiToken()

    def verify(self, ctx: RequestContext) -> bool:
        """Vérifie le token JWT avec Keycloak et remplit ctx avec les infos utilisateur"""
        if self.__api_token_verifier.verify(ctx):
            logger.info("API token valid, skipping Keycloak verification")
            return True
        if not ctx.token:
            logger.warning("Rejecting request without a bearer token")
            return False

        try:
            user_info = self.keycloak_openid.introspect(ctx.token)
            logger.debug("Token introspection claims: %s", sorted(user_info.keys()))
            if user_info.get("active") is False:
                # Keycloak répond 200 {"active": false} sans jamais dire pourquoi. Depuis
                # 26.6.2 la cause la plus fréquente n'est pas un jeton expiré mais un `aud`
                # qui ne contient pas le client d'introspection : sans ce log, le rejet est
                # indiscernable d'un jeton invalide.
                logger.warning(
                    "Token introspection returned inactive for client %s "
                    "(expired/revoked token, or client absent from the token audience)",
                    self.client_id,
                )
                return False

            # Remplir le contexte avec les informations récupérées
            ctx.user_id = user_info.get("sub", "")  # Subject = user ID
            logger.info("User ID: %s is connected", ctx.user_id)
            ctx.email = user_info.get("email", "")
            ctx.groups = user_info.get("groups", [])

            # Récupérer les rôles (peut varier selon la config Keycloak)
            ctx.roles = user_info.get("resource_access", {}).get(self.client_id, {}).get("roles", [])
            # Ou si les rôles sont dans realm_access :
            # ctx.roles = user_info.get("realm_access", {}).get("roles", [])

            # Déterminer si l'utilisateur est admin
            ctx.is_admin = "admin" in ctx.roles or "realm-admin" in ctx.roles

            return True

        except Exception as e:
            logger.error("Erreur lors de la vérification du token: %s", e, exc_info=True)
            return False


SECURITY_FACTORY: dict[str, BaseVerifyToken] = {
    "full-access": AllowAllAccess,
    "dev": DevToken,
    "keycloak": KeycloakToken,
}

TokenVerifier: BaseVerifyToken = SECURITY_FACTORY[os.environ.get("VERIFY_TOKEN_MODEL", "keycloak")]()
