import { fileURLToPath } from 'node:url'
import { configDefaults, defineConfig, mergeConfig } from 'vitest/config'
import viteConfig from './vite.config'

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      environment: 'jsdom',
      root: fileURLToPath(new URL('./', import.meta.url)),
      include: ['src/**/*.{spec,test}.{ts,tsx}', 'src/**/__tests__/**/*.{ts,tsx}'],
      // Playwright owns `playwright/e2e` — running those specs under Vitest just
      // fails on a missing `@playwright/test` runner.
      exclude: [...configDefaults.exclude, 'playwright/**'],
      // There is no unit-test suite yet; don't fail `make test-frontend` for it.
      passWithNoTests: true,
      setupFiles: [
        fileURLToPath(new URL('./vitest-setup.ts', import.meta.url)),
      ],
      coverage: {
        provider: 'v8',
        reporter: ['text', 'lcov'],
        include: ['src/**/*.{ts,vue}'],
        exclude: ['src/**/*.d.ts', 'src/api/types/**'],
      },
    },
  }),
)
