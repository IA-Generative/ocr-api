import os
import sys
import warnings
from ocr_backend.core.security.token import BaseVerifyToken, RequestContext
from keycloak import KeycloakOpenID
from src.services.token_service import (
    get_token_by_user_and_token,
    create_token,
    get_token_by_value,
)
import json
from hashlib import sha256
from loguru import logger


logger.remove()  # Remove default logger
logger.add(sys.stdout, level="DEBUG", format="{time} - {level} - {message}", colorize=True)


def pre_create_default_token() -> None:
    api_json = os.environ.get(
        "API_KEYS",
        None,
    )
    if not api_json:
        logger.warning("No API keys provided, using default key: secret-api")
    else:
        api_keys = json.loads(api_json)
        for value in api_keys:
            try:
                request_context = RequestContext.model_validate(value)
                hash_token = sha256((request_context.token or "").encode()).hexdigest()
                if (
                    request_context.user_id
                    and request_context.token
                    and not get_token_by_user_and_token(
                        user_id=request_context.user_id,
                        token_str=hash_token,
                    )
                ):
                    create_token(
                        user_id=request_context.user_id,
                        token_str=hash_token,
                        roles=(json.dumps(request_context.roles) if request_context.roles else None),
                    )
                else:
                    logger.info(f"Token for user_id={request_context.user_id} already exists, skipping creation")
            except Exception as e:
                logger.error(f"Error validating API key: {e}")


pre_create_default_token()


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

    def verify(self, ctx: RequestContext) -> bool:
        logger.debug(f"Verifying API token for user_id={ctx.user_id}")
        query_token = sha256((ctx.token or "").encode()).hexdigest()
        user_id = ctx.user_id or ""
        if get_token_by_value(token_str=query_token):
            logger.info(f"Valid token found for user_id={user_id}")
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
        logger.debug(f"Keycloak URL: {self.keycloak_url}, Realm: {self.realm_name}, Client ID: {self.client_id}")
        self.__api_token_verifier = ApiToken()

    def verify(self, ctx: RequestContext) -> bool:
        """Vérifie le token JWT avec Keycloak et remplit ctx avec les infos utilisateur"""
        if self.__api_token_verifier.verify(ctx):
            logger.info("API token valid, skipping Keycloak verification")
            return True
        try:
            user_info = self.keycloak_openid.introspect(ctx.token)
            logger.debug(f"Token info: {user_info.keys()}")
            if user_info.get("active") is False:
                return False

            # Remplir le contexte avec les informations récupérées
            ctx.user_id = user_info.get("sub", "")  # Subject = user ID
            logger.info(f"User ID: {ctx.user_id} is connected")
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
            logger.error(f"Erreur lors de la vérification du token: {e}")
            return False


SECURITY_FACTORY: dict[str, BaseVerifyToken] = {
    "full-access": AllowAllAccess,
    "dev": DevToken,
    "keycloak": KeycloakToken,
    "api-token": ApiToken,
}  # ty:ignore[invalid-assignment]

TokenVerifier: BaseVerifyToken = SECURITY_FACTORY[os.environ.get("VERIFY_TOKEN_MODEL", "keycloak")]()  # ty:ignore[missing-argument, invalid-assignment]
