def extract_identity(claims: dict, client_id: str) -> dict:
    """Map Keycloak claims (introspection or userinfo) onto our session/context fields.

    Shared between the OAuth callback (building a session) and anywhere else that needs
    to turn raw Keycloak claims into the same shape, so the roles/is_admin logic only
    lives in one place.
    """
    roles = claims.get("resource_access", {}).get(client_id, {}).get("roles", [])
    return {
        "user_id": claims.get("sub", ""),
        "email": claims.get("email", ""),
        "first_name": claims.get("given_name", ""),
        "last_name": claims.get("family_name", ""),
        "groups": claims.get("groups", []),
        "roles": roles,
        "is_admin": "admin" in roles or "realm-admin" in roles,
    }
