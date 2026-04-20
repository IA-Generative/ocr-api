import type { NavigationGuardNext, RouteLocationNormalized } from 'vue-router'
import { createRouter, createWebHistory } from 'vue-router'

import { useUserStore } from '@/stores/user'
import { KEYCLOAK_CLIENT_ID, KEYCLOAK_REALM, KEYCLOAK_REDIRECT_URI, KEYCLOAK_URL } from '@/utils/constants'
import { getKeycloak } from '@/utils/keycloak'
import Home from '../views/AppHome.vue'
import DevOcrViewer from '../views/DevOcrViewer.vue'
import OcrResultView from '../views/OcrResultView.vue'
import Documentation from '../views/Documentation.vue'
import TemplatesView from '../views/TemplatesView.vue'

function redirectToSSO () {
  const loginUrl = `${KEYCLOAK_URL}/realms/${KEYCLOAK_REALM}/protocol/openid-connect/auth?client_id=${encodeURIComponent(KEYCLOAK_CLIENT_ID)}&redirect_uri=${encodeURIComponent(KEYCLOAK_REDIRECT_URI)}&response_type=code`
  window.location.href = loginUrl
}

// Force la redirection explicite vers le serveur
// Si l'utilisateur n'est pas authentifié, provoque
// alors le processus SSO (trappé par oauth2-proxy)
function authGuard (_path: string) {
  return async (
    _to: RouteLocationNormalized,
    _from: RouteLocationNormalized,
    next: NavigationGuardNext
  ) => {
    const keycloak = getKeycloak()
    const ssoBypass = import.meta.env.VITE_SSO_BYPASS === 'true' || (window as any).VITE_SSO_BYPASS === 'true'
    if (!keycloak.authenticated && !ssoBypass) {
      redirectToSSO()
      return
    }
    next()
  }
}

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    beforeEnter: authGuard('/'),
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: Home,
    beforeEnter: authGuard('/tasks'),
  },
  {
    path: '/login',
    name: 'Login',
    beforeEnter: async (_to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext) => {
      const userStore = useUserStore()
      await userStore.login()
      next()
    },
    component: Home,
  },
  {
    path: '/logout',
    name: 'Logout',
    beforeEnter: async (_to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext) => {
      const userStore = useUserStore()
      await userStore.logout()
      next()
    },
    component: Home,
  },
  {
    path: '/dev/ocr-viewer',
    name: 'DevOcrViewer',
    component: DevOcrViewer,
  },
  {
    path: '/docs',
    name: 'Documentation',
    component: Documentation,
    beforeEnter: authGuard('/docs'),
  },
  {
    path: '/templates',
    name: 'Templates',
    component: TemplatesView,
    props: { fullscreen: true },
    beforeEnter: authGuard('/templates'),
  },
  {
    path: '/:taskId',
    name: 'OcrResult',
    component: OcrResultView,
    beforeEnter: authGuard('/:taskId'),
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env?.BASE_URL || ''),
  routes,
})

export default router
