import type { KeycloakConfig, KeycloakInitOptions } from 'keycloak-js'
import type { IUser } from '@/interfaces/IUser.ts'
import Keycloak from 'keycloak-js'

import {
  KEYCLOAK_CLIENT_ID,
  KEYCLOAK_REALM,
  KEYCLOAK_REDIRECT_URI,
  KEYCLOAK_URL,
} from './constants'

// `VITE_REDIRECT_URI` n'est pas écrit de la même façon d'un environnement à l'autre (prod
// avec slash final, dev/staging/preprod sans). En matching exact Keycloak compare des
// chaînes : on normalise donc une bonne fois pour que la redirect_uri envoyée soit toujours
// exactement celle déclarée sur le client.
const REDIRECT_URI: string | undefined = (() => {
  if (!KEYCLOAK_REDIRECT_URI) {
    console.warn('[keycloak] VITE_REDIRECT_URI is not set, falling back to the current URL')
    return undefined
  }
  try {
    return new URL(KEYCLOAK_REDIRECT_URI).toString()
  }
  catch {
    console.warn(`[keycloak] VITE_REDIRECT_URI is not an absolute URL: ${KEYCLOAK_REDIRECT_URI}`)
    return undefined
  }
})()

export const keycloakInitOptions: KeycloakInitOptions = {
  onLoad: 'check-sso',
  flow: 'standard',
  // Toujours transmise à `init()` : sans elle keycloak-js retombe sur `location.href`,
  // et la redirect_uri devient alors dépendante de la barre d'adresse.
  redirectUri: REDIRECT_URI,
}

export const keycloakConfig: KeycloakConfig = {
  url: KEYCLOAK_URL,
  realm: KEYCLOAK_REALM,
  clientId: KEYCLOAK_CLIENT_ID,
}

let keycloak: Keycloak

// Depuis Keycloak 26.6.5/26.7.0, une redirect_uri dont la query string contient un paramètre
// de réponse OIDC est rejetée (protection HTTP Parameter Pollution), avant même la comparaison
// avec les valid redirect URIs du client - un wildcard ne rattrape donc pas le coup.
// Toutes les redirections passent maintenant par REDIRECT_URI, cette liste ne sert donc
// plus qu'à nettoyer la barre d'adresse (défense en profondeur).
const OIDC_RESPONSE_PARAMS = [
  'code',
  'state',
  'session_state',
  'iss',
  'error',
  'error_description',
  'id_token',
  'access_token',
  'token_type',
  'expires_in',
  'response',
  'kc_action',
  'kc_action_status',
]

// Route demandée avant la redirection SSO, rejouée au retour puisque la redirect_uri est fixe.
const POST_LOGIN_REDIRECT_KEY = 'ocr:post-login-redirect'

function cleanAuthParamsFromUrl () {
  const url = new URL(window.location.href)
  const mutated = OIDC_RESPONSE_PARAMS.reduce((acc, param) => {
    if (!url.searchParams.has(param)) {
      return acc
    }
    url.searchParams.delete(param)
    return true
  }, false)
  if (!mutated) {
    return
  }
  const query = url.searchParams.toString()
  window.history.replaceState({}, document.title, `${url.origin}${url.pathname}${query ? `?${query}` : ''}${url.hash}`)
}

// Seuls les chemins relatifs à l'application sont acceptés : une valeur absolue ou
// protocol-relative ("//evil.tld") transformerait la restauration en open redirect.
function isSafeInternalPath (path: string | null): path is string {
  return !!path && path.startsWith('/') && !path.startsWith('//')
}

export function rememberPostLoginRedirect (path: string) {
  try {
    if (isSafeInternalPath(path)) {
      window.sessionStorage.setItem(POST_LOGIN_REDIRECT_KEY, path)
    }
  }
  catch {
    // sessionStorage indisponible (navigation privée, cookies bloqués) : on perd le
    // retour à la page demandée, ce qui ne doit pas empêcher la connexion.
  }
}

function consumePostLoginRedirect (): string | null {
  try {
    const path = window.sessionStorage.getItem(POST_LOGIN_REDIRECT_KEY)
    window.sessionStorage.removeItem(POST_LOGIN_REDIRECT_KEY)
    return isSafeInternalPath(path) ? path : null
  }
  catch {
    return null
  }
}

// Rejoue la route demandée avant connexion. Appelé avant le montage de l'application :
// le router n'a pas encore navigué, donc réécrire l'historique suffit et évite à la fois
// une double navigation et l'affichage furtif de la route par défaut.
export function restorePostLoginRedirect () {
  if (!getKeycloak().authenticated) {
    return
  }
  const path = consumePostLoginRedirect()
  if (!path) {
    return
  }
  const current = `${window.location.pathname}${window.location.search}${window.location.hash}`
  if (path !== current) {
    window.history.replaceState({}, document.title, path)
  }
}

function isRefreshTokenValid (keycloak: Keycloak): boolean {
  const refreshExp = keycloak.refreshTokenParsed?.exp
  const now = Date.now() / 1000
  return typeof refreshExp === 'number' && refreshExp > now
}

function getTokenExpiration (keycloak: Keycloak): number | null {
  const tokenExp = keycloak.tokenParsed?.exp
  return typeof tokenExp === 'number' ? tokenExp : null
}

export function getKeycloak () {
  if (!keycloak) {
    keycloak = new Keycloak(keycloakConfig)
    keycloak.onAuthSuccess = () => {
      if (isRefreshTokenValid(keycloak)) {
        return
      }
      console.warn('Keycloak misconfiguration: refreshToken should not expire before token')
      const tokenExp = getTokenExpiration(keycloak)
      if (tokenExp) {
        const refreshTokenDelay = (tokenExp * 1000 - Date.now()) / 2
        setTimeout(() => {
          keycloak.updateToken()
        }, refreshTokenDelay)
      }
    }
    keycloak.onTokenExpired = () => {
      keycloak.updateToken(30)
    }
  }
  return keycloak
}

export function getUserProfile (): IUser {
  try {
    const keycloak = getKeycloak()
    const { email, sub: id, given_name: firstName, family_name: lastName, groups } = keycloak.idTokenParsed as { email: string, sub: string, given_name: string, family_name: string, groups: string[] }
    return {
      email,
      id,
      firstName,
      lastName,
      groups,
    }
  } catch (error) {
    if (error instanceof Error) {
      throw new TypeError(error.message)
    }
    throw new Error('Failed to retrieve the user\'s keycloak profile')
  }
}

export async function keycloakInit () {
  try {
    const { onLoad, flow, redirectUri } = keycloakInitOptions
    const keycloak = getKeycloak()
    // Nettoyage AVANT init : check-sso construit sa redirect_uri à partir de location.href,
    // qui contient encore les paramètres de réponse de la connexion précédente.
    cleanAuthParamsFromUrl()
    await keycloak.init({ onLoad, flow, redirectUri })
    // Le callback nominal arrive dans le fragment et keycloak-js le retire lui-même ;
    // ce nettoyage couvre les paramètres laissés par une autre source de redirection.
    cleanAuthParamsFromUrl()
  } catch (error) {
    // Si CORS: on log et on laisse l’app fonctionner (les guards feront une redirection manuelle).
    // If CORS: log the error and let the app continue (guards will handle manual redirection).
    console.error('[keycloakInit] init failed (often CORS). Manual redirections active.', error)
    if (error instanceof Error) {
      throw new TypeError(error.message)
    }
    throw new Error('keycloak initialization failed')
  }
}

export async function keycloakLogin () {
  try {
    const keycloak = getKeycloak()
    await keycloak.login({ redirectUri: REDIRECT_URI })
  } catch (error) {
    if (error instanceof Error) {
      throw new TypeError(error.message)
    }
    throw new Error('Failed to connect to Keycloak')
  }
}

export async function keycloakRegister () {
  try {
    const keycloak = getKeycloak()
    await keycloak.register({ redirectUri: REDIRECT_URI })
  } catch (error) {
    if (error instanceof Error) {
      throw new TypeError(error.message)
    }
    throw new Error('Failed to register with keycloak')
  }
}

export async function keycloakLogout () {
  try {
    const keycloak = getKeycloak()
    await keycloak.logout()
    await keycloak.clearToken()
  } catch (error) {
    if (error instanceof Error) {
      throw new TypeError(error.message)
    }
    throw new Error('Failed to logout from keycloak')
  }
}

export async function getAuthTokens () {
  const keycloak = getKeycloak()

  if (!keycloak.authenticated) {
    throw new Error('User is not authenticated')
  }

  return {
    accessToken: keycloak.token,
    refreshToken: keycloak.refreshToken,
    idToken: keycloak.idToken,
  }
}
