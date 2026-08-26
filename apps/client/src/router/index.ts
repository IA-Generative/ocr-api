import type { NavigationGuardNext, RouteLocationNormalized } from 'vue-router'
import { createRouter, createWebHistory } from 'vue-router'

import { useUserStore } from '@/stores/user'
import Home from '../views/AppHome.vue'
import TaskDetailView from '../views/TaskDetailView.vue'

// L'authentification passe entièrement par le backend (BFF) : le navigateur ne fait
// jamais de redirection OIDC lui-même. `checkAuth` interroge `/api/auth/me` (cookie de
// session), et une navigation complète vers `/api/auth/login?redirect=...` déclenche le
// flow côté backend, qui revient directement sur la route demandée après le callback.
function authGuard () {
  return async (
    to: RouteLocationNormalized,
    _from: RouteLocationNormalized,
    next: NavigationGuardNext,
  ) => {
    const userStore = useUserStore()
    const ssoBypass = import.meta.env.VITE_SSO_BYPASS === 'true' || (window as any).VITE_SSO_BYPASS === 'true'
    if (ssoBypass) {
      next()
      return
    }
    const isLoggedIn = await userStore.checkAuth()
    if (!isLoggedIn) {
      userStore.login(to.fullPath)
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
    // `login`/`logout` are full-page navigations (see utils/auth.ts) - the guard never
    // reaches `next()` because the browser leaves the SPA before it would resolve.
    beforeEnter: () => {
      const userStore = useUserStore()
      userStore.login()
    },
    component: Home,
  },
  {
    path: '/logout',
    name: 'Logout',
    beforeEnter: () => {
      const userStore = useUserStore()
      void userStore.logout()
    },
    component: Home,
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env?.BASE_URL || ''),
  routes,
})

export default router
