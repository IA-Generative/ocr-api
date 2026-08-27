import type { AxiosInstance, InternalAxiosRequestConfig } from 'axios'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import createHttpClient from '@/api/http-client'

const { keycloak } = vi.hoisted(() => ({
  keycloak: {
    authenticated: true,
    token: 'initial-token',
    tokenParsed: undefined as { typ?: string } | undefined,
    updateToken: vi.fn(),
    login: vi.fn(),
  },
}))

vi.mock('@/utils/keycloak', () => ({ getKeycloak: () => keycloak }))

/**
 * Swaps the transport out from under the client while leaving both interceptors
 * in place, so the tests exercise the real request/response chain.
 */
function withTransport (client: AxiosInstance, handler: (config: InternalAxiosRequestConfig) => unknown) {
  client.defaults.adapter = async (config) => {
    const result = await handler(config as InternalAxiosRequestConfig)
    return { data: result, status: 200, statusText: 'OK', headers: {}, config } as never
  }
}

function httpError (config: InternalAxiosRequestConfig, status: number) {
  return Object.assign(new Error(`Request failed with status code ${status}`), {
    config,
    isAxiosError: true,
    response: { status, data: {}, statusText: '', headers: {}, config },
  })
}

describe('createHttpClient', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    keycloak.authenticated = true
    keycloak.token = 'initial-token'
    keycloak.tokenParsed = undefined
  })

  describe('request interceptor', () => {
    it('attaches the keycloak token as a Bearer header', async () => {
      const client = createHttpClient('http://api.test')
      withTransport(client, config => config.headers.Authorization)

      const { data } = await client.get('/health')

      expect(data).toBe('Bearer initial-token')
    })

    it('honours a non-Bearer token type advertised by the token', async () => {
      keycloak.tokenParsed = { typ: 'DPoP' }
      const client = createHttpClient('http://api.test')
      withTransport(client, config => config.headers.Authorization)

      const { data } = await client.get('/health')

      expect(data).toBe('DPoP initial-token')
    })

    it('sends no Authorization header when the user is not authenticated', async () => {
      keycloak.authenticated = false
      const client = createHttpClient('http://api.test')
      withTransport(client, config => config.headers.Authorization ?? null)

      const { data } = await client.get('/health')

      expect(data).toBeNull()
    })
  })

  describe('401 handling', () => {
    it('refreshes the token and replays the request once', async () => {
      keycloak.updateToken.mockImplementation(async () => {
        keycloak.token = 'refreshed-token'
        return true
      })

      const client = createHttpClient('http://api.test')
      const seen: (string | undefined)[] = []
      let attempt = 0
      client.defaults.adapter = async (config) => {
        seen.push(config.headers.Authorization as string | undefined)
        attempt += 1
        if (attempt === 1) {
          throw httpError(config as InternalAxiosRequestConfig, 401)
        }
        return { data: 'ok', status: 200, statusText: 'OK', headers: {}, config } as never
      }

      const { data } = await client.get('/tasks')

      expect(data).toBe('ok')
      expect(keycloak.updateToken).toHaveBeenCalledExactlyOnceWith(30)
      expect(seen).toEqual(['Bearer initial-token', 'Bearer refreshed-token'])
    })

    it('gives up after a single retry rather than looping', async () => {
      keycloak.updateToken.mockResolvedValue(true)
      const client = createHttpClient('http://api.test')
      const adapter = vi.fn(async (config) => {
        throw httpError(config as InternalAxiosRequestConfig, 401)
      })
      client.defaults.adapter = adapter as never

      await expect(client.get('/tasks')).rejects.toThrow('status code 401')

      // Original request plus exactly one replay.
      expect(adapter).toHaveBeenCalledTimes(2)
      expect(keycloak.updateToken).toHaveBeenCalledTimes(1)
    })

    it('does not replay when the refresh reports the token was still valid', async () => {
      keycloak.updateToken.mockResolvedValue(false)
      const client = createHttpClient('http://api.test')
      const adapter = vi.fn(async (config) => {
        throw httpError(config as InternalAxiosRequestConfig, 401)
      })
      client.defaults.adapter = adapter as never

      await expect(client.get('/tasks')).rejects.toThrow('status code 401')

      expect(adapter).toHaveBeenCalledTimes(1)
      expect(keycloak.login).not.toHaveBeenCalled()
    })

    it('falls back to a fresh login when the refresh itself fails', async () => {
      keycloak.updateToken.mockRejectedValue(new Error('refresh token expired'))
      vi.spyOn(console, 'error').mockImplementation(() => {})

      const client = createHttpClient('http://api.test')
      client.defaults.adapter = (async (config: InternalAxiosRequestConfig) => {
        throw httpError(config, 401)
      }) as never

      await expect(client.get('/tasks')).rejects.toThrow('status code 401')

      expect(keycloak.login).toHaveBeenCalledOnce()
    })
  })

  it('lets non-401 failures through without touching the session', async () => {
    const client = createHttpClient('http://api.test')
    client.defaults.adapter = (async (config: InternalAxiosRequestConfig) => {
      throw httpError(config, 500)
    }) as never

    await expect(client.get('/tasks')).rejects.toThrow('status code 500')

    expect(keycloak.updateToken).not.toHaveBeenCalled()
    expect(keycloak.login).not.toHaveBeenCalled()
  })
})
