# Sécurité & Configuration Keycloak

> Voir aussi : [Scan de sécurité Strix (CI/CD)](strix.md)

Pour que l’authentification via Keycloak fonctionne correctement avec OpenID Connect, **toutes les valeurs de configuration Keycloak doivent être définies dans le Vault** (ou dans vos variables d’environnement).

## Variables requises

Voici les variables à renseigner :

- `KEYCLOAK_URL` : URL du serveur Keycloak (exemple : `https://keycloak.example.com`)
- `KEYCLOAK_REALM` : Nom du realm Keycloak utilisé
- `KEYCLOAK_CLIENT_ID` : ID du client OpenID configuré dans Keycloak
- `KEYCLOAK_CLIENT_SECRET` : Secret du client (si nécessaire)

**Aucune valeur par défaut ne doit être utilisée en production.**
Toutes ces valeurs doivent être stockées et injectées de façon sécurisée via Vault.

## Exemple (Vault)

Dans votre Vault, ajoutez les clés suivantes :

```
KEYCLOAK_URL=https://keycloak.example.com
KEYCLOAK_REALM=mon-realm
KEYCLOAK_CLIENT_ID=mon-client
KEYCLOAK_CLIENT_SECRET=mon-secret
```

## Bonnes pratiques

- **Ne jamais** committer ces valeurs dans le code source.
- Toujours utiliser Vault ou un gestionnaire de secrets pour injecter ces variables à l’exécution.
- Vérifier que toutes les variables sont bien présentes avant de démarrer l’application.

---
Pour plus d’informations, consultez la documentation Keycloak et celle de votre gestionnaire de
