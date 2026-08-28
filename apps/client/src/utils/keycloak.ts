import type { KeycloakConfig, KeycloakInitOptions } from 'keycloak-js'
import type { IUser } from '@/interfaces/IUser.ts'
import Keycloak from 'keycloak-js'

import {
  KEYCLOAK_CLIENT_ID,
  KEYCLOAK_REALM,
  KEYCLOAK_REDIRECT_URI,
  KEYCLOAK_URL,
} from './constants'

export const keycloakInitOptions: KeycloakInitOptions = {
  onLoad: 'check-sso',
  flow: 'standard',
  redirectUri: KEYCLOAK_REDIRECT_URI,
}

export const keycloakConfig: KeycloakConfig = {
  url: KEYCLOAK_URL,
  realm: KEYCLOAK_REALM,
  clientId: KEYCLOAK_CLIENT_ID,
}

let keycloak: Keycloak

export class SessionExpiredError extends Error {
  constructor () {
    super('Session expired: refresh token is no longer valid')
    this.name = 'SessionExpiredError'
  }
}

const REFRESH_TOKEN_BUFFER_SECONDS = 30
let loginRedirectAlreadyInProgress = false

function isRefreshTokenValid (keycloak: Keycloak): boolean {
  const refreshTokenExpirationDate = keycloak.refreshTokenParsed?.exp
  if (refreshTokenExpirationDate === undefined) {
    return false
  }

  const nowInSeconds = Math.floor(Date.now() / 1000)
  const skew = keycloak.timeSkew ?? 0
  return nowInSeconds - skew < refreshTokenExpirationDate - REFRESH_TOKEN_BUFFER_SECONDS
}

export function getKeycloak () {
  if (!keycloak) {
    keycloak = new Keycloak(keycloakConfig)
  }
  return keycloak
}

export async function getValidToken (): Promise<string> {
  const keycloak = getKeycloak()

  if (!keycloak.authenticated || !isRefreshTokenValid(keycloak)) {
    return handleDeadSession(keycloak)
  }

  try {
    await keycloak.updateToken(REFRESH_TOKEN_BUFFER_SECONDS)
  }
  catch {
    return handleDeadSession(keycloak)
  }
  return keycloak.token!
}

function handleDeadSession (keycloak: Keycloak): never {
  if (!loginRedirectAlreadyInProgress) {
    loginRedirectAlreadyInProgress = true
    keycloak.login()
  }
  throw new SessionExpiredError()
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
  }
  catch (error) {
    if (error instanceof Error) {
      throw new TypeError(error.message)
    }
    throw new Error('Failed to retrieve the user\'s keycloak profile')
  }
}

export function buildAuthUrl (opts?: { register?: boolean, redirectUri?: string }) {
  const redirect = encodeURIComponent(opts?.redirectUri || KEYCLOAK_REDIRECT_URI)
  const base = `${KEYCLOAK_URL}/realms/${KEYCLOAK_REALM}/protocol/openid-connect/auth`
  const params = new URLSearchParams({
    client_id: KEYCLOAK_CLIENT_ID,
    redirect_uri: redirect,
    response_type: 'code',
    scope: 'openid',
  })
  if (opts?.register) {
    params.set('kc_action', 'register')
  }
  return `${base}?${params.toString()}`
}

export function redirectToKeycloakLogin (redirectUri?: string) {
  window.location.href = buildAuthUrl({ redirectUri })
}

export function redirectToKeycloakRegister (redirectUri?: string) {
  window.location.href = buildAuthUrl({ register: true, redirectUri })
}

const AUTH_CALLBACK_PARAMS = ['code', 'state', 'session_state', 'iss']

function withoutAuthParams (search: string): string | null {
  const params = new URLSearchParams(search)
  if (!AUTH_CALLBACK_PARAMS.some(param => params.has(param))) {
    return null
  }
  AUTH_CALLBACK_PARAMS.forEach(param => params.delete(param))
  return params.toString()
}

function stripAuthCallbackParams () {
  const url = new URL(window.location.href)
  const cleanedQuery = withoutAuthParams(url.search)
  const cleanedHash = withoutAuthParams(url.hash.replace(/^#/, ''))

  if (cleanedQuery === null && cleanedHash === null) {
    return
  }

  const query = cleanedQuery ?? url.search.replace(/^\?/, '')
  const hash = cleanedHash ?? url.hash.replace(/^#/, '')
  const clean = url.origin + url.pathname + (query ? `?${query}` : '') + (hash ? `#${hash}` : '')
  window.history.replaceState({}, document.title, clean)
}

export async function keycloakInit () {
  try {
    const { onLoad, flow } = keycloakInitOptions
    const keycloak = getKeycloak()
    await keycloak.init({
      onLoad,
      flow,
      // on laisse Keycloak utiliser la redirectUri définie dans la config (évite boucles avec ?code=)
    })
    stripAuthCallbackParams()
  }
  catch (error) {
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
    const currentUrl = new URL(window.location.href)
    const redirectUri = `${window.location.origin}${currentUrl.pathname}${currentUrl.search}`
    await keycloak.login({ redirectUri })
  }
  catch (error) {
    if (error instanceof Error) {
      throw new TypeError(error.message)
    }
    throw new Error('Failed to connect to Keycloak')
  }
}

export async function keycloakRegister () {
  try {
    const keycloak = getKeycloak()
    const currentUrl = new URL(window.location.href)
    const redirectUri = `${window.location.origin}${currentUrl.pathname}${currentUrl.search}`
    await keycloak.register({ redirectUri })
  }
  catch (error) {
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
  }
  catch (error) {
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
