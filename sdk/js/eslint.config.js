import antfu from '@antfu/eslint-config'

// TypeScript-only config for this package - a standalone Node.js package (own
// package.json, own ESLint), not part of the pnpm workspace apps/client lives in.
// See ../../eslint.config.js for why the repo root ignores this directory.
export default antfu(
  {
    vue: false,
    typescript: true,
    stylistic: {
      overrides: {
        'style/comma-dangle': ['error', 'always-multiline'],
        'style/space-before-function-paren': ['error', 'always'],
      },
    },
    ignores: ['dist/**', 'node_modules/**', 'coverage/**'],
  },
).override('antfu/node/rules', {
  rules: {
    'node/prefer-global/process': ['error', 'always'],
    'node/prefer-global/console': ['error', 'always'],
    'node/prefer-global/buffer': ['error', 'always'],
  },
})
