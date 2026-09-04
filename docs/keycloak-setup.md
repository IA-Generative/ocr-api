## Configurer un client Keycloak (BFF)

Ce guide décrit comment configurer, dans la console d'administration Keycloak, le client OpenID
Connect utilisé par le flow BFF (Backend-For-Frontend) de ce projet : le navigateur ne parle
jamais à Keycloak, seul le backend le fait, via `/api/auth/{login,callback,logout,me}`
(`ocr_backend/routers/auth.py`). Voir [`docs/variables.md`](./variables.md#variables-pour-lauthentification-keycloak-bff)
pour la liste des variables d'environnement correspondantes.

Pour un realm de test **prêt à l'emploi en local** (docker compose), voir
[`docker/keycloak/realm-mirai.json`](../docker/keycloak/realm-mirai.json), auto-provisionné au
démarrage — ce document sert à répliquer la même configuration à la main sur un realm Keycloak
existant (staging, prod, ou tout realm partagé géré par une autre équipe).

---

### 1. Choisir/créer le realm

Utilisez un realm dédié (pas `master`) — renseignez son nom dans `KEYCLOAK_REALM`.

---

### 2. Créer le client

**Clients → Create client**

| Champ | Valeur |
|:---|:---|
| Client type | `OpenID Connect` |
| Client ID | libre (ex. `ocr`) — c'est la valeur de `KEYCLOAK_CLIENT_ID` |

**Capability config** (étape suivante) :

| Champ | Valeur | Pourquoi |
|:---|:---|:---|
| Client authentication | **ON** | Le client doit être **confidentiel**, pas public : seul le backend échange le code d'autorisation, jamais le navigateur. C'est ce qui fait apparaître l'onglet "Credentials" (le secret). |
| Standard flow (Authorization Code) | **ON** | C'est le flow utilisé (`response_type=code` + PKCE `S256`, voir `login()` dans `ocr_backend/routers/auth.py`). |
| Direct access grants | OFF | Non utilisé — le mot de passe ne transite jamais par ce backend. |
| Implicit flow | OFF | Non utilisé. |
| Service accounts roles | OFF (sauf besoin spécifique hors du flow utilisateur) | Non utilisé par ce flow. |

---

### 3. Login settings (Access settings)

| Champ | Valeur |
|:---|:---|
| **Valid redirect URIs** | `{BACKEND_PUBLIC_URL}/api/auth/callback` — doit correspondre **exactement** (schéma + host + port + path) à la valeur de `BACKEND_PUBLIC_URL`. Exemple : `https://ocr-api.example.com/api/auth/callback`. |
| **Valid post logout redirect URIs** | `{FRONTEND_URL}` — utilisé pour rediriger le navigateur après un logout complet côté Keycloak (`_end_session_url()` dans `auth.py`, appelé sur `POST /api/auth/logout`). Sans ça, Keycloak refuse la redirection de fin de session SSO. |
| Web origins | Non requis pour ce flow : le navigateur n'appelle jamais Keycloak en JS/CORS, seul le backend le fait en server-to-server. Le CORS applicatif (origine autorisée par **notre** API) est géré par `FRONTEND_URL`, côté `ocr_backend/main.py`, pas par ce champ Keycloak. |

⚠️ Une redirect URI mal renseignée (slash final en trop, mauvais port, `http` au lieu de `https`)
fait échouer `/api/auth/callback` avec une erreur Keycloak `invalid_redirect_uri`, silencieuse
côté app (redirection vers `FRONTEND_URL` sans session créée — voir le `try/except` dans
`callback()`).

---

### 4. Récupérer le secret

**Credentials** (onglet visible uniquement si *Client authentication* est ON) → copier
**Client secret** → `KEYCLOAK_CLIENT_SECRET`.

---

### 5. Scopes demandés

Le backend demande `scope=openid profile email` (`login()` dans `auth.py`). Ce sont les
client scopes par défaut de tout nouveau client Keycloak — rien à faire sauf s'ils ont été
retirés manuellement (**Client scopes** de votre client → vérifier que `email` et `profile`
sont bien en *Default*, pas en *Optional* ni absents).

---

### 6. Rôles applicatifs (optionnel — pour `is_admin`)

`extract_identity()` (`ocr_backend/core/security/claims.py`) lit
`resource_access.<KEYCLOAK_CLIENT_ID>.roles` depuis le token, et positionne
`is_admin = "admin" in roles or "realm-admin" in roles`.

Ce sont des **rôles clients** (client roles) portés par **ce client** (pas des realm roles, pas
des rôles d'un autre client) — Keycloak les inclut automatiquement dans le token dès qu'un
utilisateur en a un d'assigné, sans mapper supplémentaire.

Pour donner les droits admin à un utilisateur :
1. **Clients → `<votre client>` → Roles → Create role** — créer un rôle nommé `admin` (ou
   `realm-admin`).
2. **Users → `<utilisateur>` → Role mapping → Assign role** — filtrer sur les rôles du client,
   assigner `admin`.

---

### 7. Claim `groups` (optionnel — pour `session.groups` / `/api/auth/me`)

Contrairement aux rôles clients, le claim `groups` **n'est pas inclus par défaut** dans le
token/userinfo Keycloak — il faut un mapper explicite :

1. **Clients → `<votre client>` → Client scopes → `<votre client>-dedicated` → Add mapper →
   By configuration → Group Membership**.
2. Name : `groups` — Token Claim Name : `groups`.
3. Activer *Add to userinfo* (le backend lit les claims via `userinfo()`, pas `introspect()` —
   voir la note dans `callback()` — donc c'est cette case qui compte, pas *Add to ID token*).
4. Full group path : à votre convenance (impacte juste le format des valeurs, ex. `/team-a` vs
   `team-a`) ; rien côté code n'en dépend au-delà de l'affichage.

Sans ce mapper, `session.groups` reste systématiquement vide (`claims.get("groups", [])` en
`claims.py`) — ce n'est pas un bug, juste une fonctionnalité non activée sur le realm.

---

### 8. Variables d'environnement à renseigner

```dotenv
KEYCLOAK_URL=https://sso.example.com          # atteint par le BACKEND (échange de code, refresh, logout)
KEYCLOAK_PUBLIC_URL=                            # à renseigner seulement si le navigateur résout Keycloak différemment du backend (ex. docker compose local)
KEYCLOAK_REALM=mon-realm
KEYCLOAK_CLIENT_ID=ocr
KEYCLOAK_CLIENT_SECRET=<secret récupéré à l'étape 4>
BACKEND_PUBLIC_URL=https://ocr-api.example.com  # doit matcher exactement la redirect URI de l'étape 3
FRONTEND_URL=https://ocr.example.com            # doit matcher exactement la post-logout redirect URI de l'étape 3
```

Détail de chaque variable : [`docs/variables.md`](./variables.md#variables-pour-lauthentification-keycloak-bff).

---

### 9. Vérifier

1. `GET {BACKEND_PUBLIC_URL}/api/auth/login` doit rediriger (307) vers l'écran de login Keycloak
   du bon realm.
2. Après authentification, le navigateur doit revenir sur `FRONTEND_URL` avec un cookie
   `ocr_session` (`httpOnly`, voir `SESSION_COOKIE_NAME`) posé.
3. `GET {BACKEND_PUBLIC_URL}/api/auth/me` (avec ce cookie) doit renvoyer `id`/`email`/
   `firstName`/`lastName`/`groups`.
4. `POST {BACKEND_PUBLIC_URL}/api/auth/logout` doit renvoyer `{"redirectUrl": "..."}` pointant
   vers le `end_session_endpoint` Keycloak, et le cookie doit être supprimé.

Une erreur à l'étape 1 ou 2 est presque toujours une redirect URI mal enregistrée (étape 3) ou
un `KEYCLOAK_REALM`/`KEYCLOAK_CLIENT_ID` qui ne correspond pas à ce qui a été créé aux étapes
1-2.
