import type { Page } from '@playwright/test'
import { expect } from '@playwright/test'

export async function login (page: Page) {
  const username = process.env.VITE_USERNAME_KEYCLOAK
  const password = process.env.VITE_PASSWORD_KEYCLOAK

  if (!username || !password) {
    throw new Error('Variables d\'environnement VITE_USERNAME_KEYCLOAK et VITE_PASSWORD_KEYCLOAK requises pour les tests E2E')
  }

  await page.goto('/')
  await page.locator('input[name="username"]').fill(username)
  await page.locator('input[name="password"]').fill(password)
  await page.locator('#kc-login').click()
  await expect(page.getByTitle('Reconnaître un texte scanné')).toBeVisible()
}
