import { afterEach, describe, expect, it, vi } from 'vitest'
import { openLink } from '@/utils/methods'

describe('openLink', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('opens the url in a new tab', () => {
    const open = vi.spyOn(window, 'open').mockReturnValue(null)

    openLink('https://example.gouv.fr')

    expect(open).toHaveBeenCalledWith('https://example.gouv.fr', '_blank')
  })
})
