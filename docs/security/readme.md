# Sécurité & Configuration Keycloak

> Voir aussi : [Scan de sécurité Strix (CI/CD)](strix.md)

L'authentification suit un modèle **Backend-for-Frontend (BFF)** : le frontend ne parle jamais
directement à Keycloak et ne détient aucun jeton. C'est le backend (`ocr_backend`) qui possède
tout le flow OAuth2 Authorization Code + PKCE, via `/api/auth/{login,callback,logout,me}`
(`ocr_backend/routers/auth.py`). Le navigateur ne reçoit qu'un cookie de session opaque
(`httpOnly`, `Secure` en production) ; les jetons Keycloak (access/refresh) restent côté backend,
dans Redis (`ocr_backend/core/security/session.py`).

Pour que ce flow fonctionne correctement, **toutes les valeurs de configuration Keycloak doivent
être définies dans le Vault** (ou dans vos variables d'environnement) — jamais commitées.

## Variables requises

- `KEYCLOAK_URL` : URL de Keycloak jointe **par le backend** (échange de code, refresh,
  introspection, logout). Exemple : `https://keycloak.example.com`
- `KEYCLOAK_PUBLIC_URL` : URL de Keycloak vue **par le navigateur** lors de la redirection de
  login. Optionnelle — retombe sur `KEYCLOAK_URL` si absente ; à renseigner uniquement si le
  backend et le navigateur ne résolvent pas Keycloak de la même façon (typiquement en dev local,
  voir plus bas).
- `KEYCLOAK_REALM` : Nom du realm Keycloak utilisé
- `KEYCLOAK_CLIENT_ID` : ID du client OpenID configuré dans Keycloak — **doit être un client
  confidentiel** (`publicClient: false`), jamais public : seul le backend échange le code
  d'autorisation, le navigateur ne doit avoir aucun moyen de s'authentifier directement auprès de
  Keycloak.
- `KEYCLOAK_CLIENT_SECRET` : Secret du client confidentiel
- `BACKEND_PUBLIC_URL` : URL publique de cette API. Sert à construire le `redirect_uri` fixe
  envoyé à Keycloak (`{BACKEND_PUBLIC_URL}/api/auth/callback`) — **doit correspondre exactement**
  à une redirect URI enregistrée sur le client Keycloak.
- `FRONTEND_URL` : URL publique du frontend. Sert d'origine CORS autorisée (une origine explicite
  est obligatoire dès lors que le cookie de session est envoyé avec les requêtes —
  `allow_origins: ["*"]` est rejeté par les navigateurs en présence de `allow_credentials: true`)
  et de cible de redirection après le callback de login.

**Aucune valeur par défaut ne doit être utilisée en production.**
Toutes ces valeurs doivent être stockées et injectées de façon sécurisée via Vault.

## Cookie de session

En complément, ces variables contrôlent le cookie de session posé sur le navigateur — leurs
défauts (`src/config/keycloak.py`) sont déjà corrects pour un déploiement HTTPS et n'ont
normalement pas besoin d'être surchargés en production :

- `SESSION_COOKIE_NAME` (défaut `ocr_session`)
- `SESSION_COOKIE_SECURE` (défaut `True`) : **ne jamais désactiver en production** — ce cookie
  porte l'accès à la session utilisateur, il doit toujours être limité à HTTPS. Ne le passer à
  `False` qu'en dev local HTTP (voir `docker-compose.yaml`).
- `SESSION_COOKIE_SAMESITE` (défaut `lax`)
- `SESSION_TTL_SECONDS` (défaut `604800`, 7 jours) : plafond côté Redis, l'expiration réelle reste
  bornée par celle du refresh token Keycloak.

## Exemple (Vault)

Dans votre Vault, ajoutez les clés suivantes :

```
KEYCLOAK_URL=https://keycloak.example.com
KEYCLOAK_REALM=mon-realm
KEYCLOAK_CLIENT_ID=mon-client
KEYCLOAK_CLIENT_SECRET=mon-secret
BACKEND_PUBLIC_URL=https://ocr-api.example.com
FRONTEND_URL=https://ocr.example.com
```

## Bonnes pratiques

- **Ne jamais** committer ces valeurs dans le code source.
- Toujours utiliser Vault ou un gestionnaire de secrets pour injecter ces variables à l'exécution.
- Vérifier que toutes les variables sont bien présentes avant de démarrer l'application.
- Le client Keycloak doit rester confidentiel (`publicClient: false`) : le navigateur n'a jamais
  besoin d'un secret ou d'un flow public, seul le backend parle à Keycloak.
- `SESSION_COOKIE_SECURE` doit rester à `True` dès que le trafic passe par HTTPS, c'est-à-dire
  partout hors dev local.

## Tester en local

`docker-compose.yaml` inclut un service `keycloak` (image officielle, mode `start-dev`) qui
importe automatiquement un realm de test (`docker/keycloak/realm-mirai.json` : realm `mirai`,
client confidentiel `ocr`, un utilisateur de test) — aucune configuration manuelle n'est
nécessaire pour tester le flow de bout en bout localement. Voir les variables `KEYCLOAK_*` déjà
renseignées dans `.env` à la racine du repo pour un exemple fonctionnel complet.

---
Pour plus d'informations, consultez la documentation Keycloak et celle de votre gestionnaire de
secrets.
