import type { NavigationGuardNext, RouteLocationNormalized } from 'vue-router'
import { createRouter, createWebHistory } from 'vue-router'

import { useUserStore } from '@/stores/user'
import { getKeycloak, keycloakLogin, rememberPostLoginRedirect } from '@/utils/keycloak'
import Home from '../views/AppHome.vue'
import TaskDetailView from '../views/TaskDetailView.vue'

// La connexion passe par keycloak-js et non par une URL d'autorisation construite à la main :
// on hérite ainsi de PKCE (S256 par défaut), du `state`, du `nonce` et du response_mode
// `fragment`. La redirect_uri est fixe, la route demandée est rejouée après `init()`.
function authGuard () {
  return async (
    to: RouteLocationNormalized,
    _from: RouteLocationNormalized,
    next: NavigationGuardNext,
  ) => {
    const keycloak = getKeycloak()
    const ssoBypass = import.meta.env.VITE_SSO_BYPASS === 'true' || (window as any).VITE_SSO_BYPASS === 'true'
    if (!keycloak.authenticated && !ssoBypass) {
      rememberPostLoginRedirect(to.fullPath)
      await keycloakLogin()
      return
    }
    next()
  }
}

const routes = [
  {
    path: '/',
    redirect: '/ocr',
  },
  {
    path: '/ocr',
    name: 'Ocr',
    component: Home,
    beforeEnter: authGuard(),
  },
  {
    path: '/tasks/:id',
    name: 'TaskDetail',
    component: TaskDetailView,
    beforeEnter: authGuard(),
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
]

const router = createRouter({
  history: createWebHistory(import.meta.env?.BASE_URL || ''),
  routes,
})

export default router
