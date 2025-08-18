import path from 'node:path'
import { expect, test } from '@playwright/test'
import { login } from '../login-helper'

test.describe('OCR with Document', () => {
  test('should display ocr for document', async ({ page }) => {
    await login(page)

    const filePath = path.join(process.cwd(), 'playwright', 'files', 'VVM.pdf')

    const fileInput = page.locator('input[type="file"]')
    await expect(fileInput).toBeAttached()

    await fileInput.setInputFiles(filePath)

    const extractButton = page.getByRole('button', { name: 'Extraire le texte' })
    await expect(extractButton).toBeVisible({ timeout: 10000 })
    await expect(extractButton).toBeEnabled({ timeout: 5000 })

    await extractButton.click()
    await page.waitForTimeout(8000)
    await expect(page.getByRole('button', { name: 'Télécharger' })).toBeVisible()
  })
})
