import type { IUser } from '@/interfaces/IUser.ts'
import { OCR_API_URL } from './constants'

// Le backend est la seule partie de l'app à parler à Keycloak (BFF) : le navigateur ne
// détient aucun jeton, seulement le cookie de session `httpOnly` posé par
// `/api/auth/callback`. `login`/`logout` sont donc des navigations complètes, jamais des
// appels XHR - `login` traverse une redirection vers Keycloak, `logout` doit pouvoir
// clore la session même si le JS de la page courante ne survit pas au retour.

function currentPath (): string {
  return `${window.location.pathname}${window.location.search}${window.location.hash}`
}

export function login (redirectPath?: string): void {
  const redirect = encodeURIComponent(redirectPath ?? currentPath())
  window.location.href = `${OCR_API_URL}/auth/login?redirect=${redirect}`
}

export async function logout (): Promise<void> {
  try {
    await fetch(`${OCR_API_URL}/auth/logout`, {
      method: 'POST',
      credentials: 'include',
    })
  } catch (error) {
    console.error('[auth] logout request failed, clearing local state anyway:', error)
  }
  window.location.href = '/'
}

export async function fetchMe (): Promise<IUser | null> {
  const response = await fetch(`${OCR_API_URL}/auth/me`, {
    credentials: 'include',
  })
  if (!response.ok) {
    return null
  }
  return response.json() as Promise<IUser>
}
