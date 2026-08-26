import logging
import os
import warnings
from ocr_backend.core.security import keycloak_client
from ocr_backend.core.security.token import BaseVerifyToken, RequestContext, parse_header_context
from fastapi import HTTPException, Request, status

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
    """Authenticates a request either via a service `Authorization: Bearer <API key>`
    header, or via the BFF session cookie set by `/api/auth/callback`.

    The browser never holds a Keycloak token: the frontend only ever sends the opaque
    session cookie, and the actual access/refresh tokens stay server-side in Redis
    (see `ocr_backend.core.security.session.SessionStore`).
    """

    def __init__(self):
        super().__init__(verify_token=True, is_fastapi=True)
        logger.info("Using Keycloak session-cookie verification")
        self.__api_token_verifier = ApiToken()

    def verify(self, ctx: RequestContext) -> bool:  # pragma: no cover - unused, see __call__
        raise NotImplementedError("KeycloakToken reads the session cookie via __call__, not verify()")

    def __call__(self, request: Request) -> RequestContext:
        ctx = parse_header_context(request, is_fastapi=self.is_fastapi)

        if self.__api_token_verifier.verify(ctx):
            logger.info("API token valid, skipping session verification")
            return ctx

        sid = request.cookies.get(keycloak_client.keycloak_settings.SESSION_COOKIE_NAME)
        session = keycloak_client.session_store.get(sid) if sid else None
        if session:
            session = keycloak_client.session_store.ensure_fresh(sid, session)

        if not session:
            logger.warning("Rejecting request without a valid session")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="UNAUTHORIZED")

        ctx.user_id = session.user_id
        ctx.email = session.email
        ctx.roles = session.roles
        ctx.groups = session.groups
        ctx.is_admin = session.is_admin
        ctx.token = session.access_token
        logger.info("User ID: %s is connected", ctx.user_id)
        return ctx


SECURITY_FACTORY: dict[str, BaseVerifyToken] = {
    "full-access": AllowAllAccess,
    "dev": DevToken,
    "keycloak": KeycloakToken,
}

TokenVerifier: BaseVerifyToken = SECURITY_FACTORY[os.environ.get("VERIFY_TOKEN_MODEL", "keycloak")]()
