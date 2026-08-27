import '@testing-library/jest-dom/vitest'

// jsdom ships no `matchMedia`; the DSFR components call it on mount.
window.matchMedia = (query: string): MediaQueryList => ({
  matches: false,
  media: query,
  onchange: null,
  addListener: () => {},
  removeListener: () => {},
  addEventListener: () => {},
  removeEventListener: () => {},
  dispatchEvent: () => false,
})
