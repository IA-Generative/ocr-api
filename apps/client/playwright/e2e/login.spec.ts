import { expect, test } from '@playwright/test'
import { login } from '../login-helper'

test.describe('Login with Keycloak', () => {
  test('should login successfully with valid credentials', async ({ page }) => {
    await login(page)
  })

  test('should show error with invalid credentials', async ({ page }) => {
    await page.goto('/')

    await page.locator('input[name="username"]').fill('test@gouv.fr')
    await page.locator('input[name="password"]').fill('testinho')

    await page.locator('#kc-login').click()

    // Verify error message on Keycloak page
    await expect(page.locator('#input-\\:r2\\:-desc-error')).toBeVisible()
    await expect(page.locator('#input-\\:r2\\:-desc-error')).toContainText('Nom d\'utilisateur ou mot de passe invalide.')
  })
})
