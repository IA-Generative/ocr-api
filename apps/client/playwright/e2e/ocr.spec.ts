import path from 'node:path'
import { expect, test } from '@playwright/test'
import { login } from '../login-helper'

test.describe('OCR with Document', () => {
  test('should display ocr for document', async ({ page }) => {
    await login(page)

    await page.locator('input[type="file"]').setInputFiles(path.resolve('./playwright/files', 'VVM.pdf'))
    await page.getByRole('button', { name: 'Extraire le texte' }).click()
  })
})
