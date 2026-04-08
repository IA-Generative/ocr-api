import { ref } from 'vue'
import type { components } from '@/api/types/api.schema'
import createHttpClient from '@/api/http-client'
import { OCR_API_URL } from '@/utils/constants'

type Page = components['schemas']['Page']

const http = createHttpClient(OCR_API_URL)

export interface ChatSource {
  pageIdx: number        // première page (pour la navigation)
  pageIndices: number[]  // toutes les pages impliquées (0-based)
  boxIdx: number         // premier bbox (compatibilité)
  boxIndices: number[]   // tous les bbox indices du chunk
  text: string
  pageLabel: string
  score?: number
}

export interface ChatMessage {
  id: number
  role: 'user' | 'bot'
  content: string
  sources?: ChatSource[]
  isLoading?: boolean
}

// ---- Types matching the backend ----
interface BackendMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

interface UsedChunk {
  page_nums: number[]
  bbox_indices: number[]
  text: string
}

interface AskResponse {
  message: BackendMessage
  sources: UsedChunk[]
}

interface EmbedResponse {
  vector: number[]
  model: string
}

// ---- Session persistence helpers ----
function storageKey (contentHash: string) {
  return `ocr-chat:${contentHash}`
}

function loadMessages (contentHash: string): ChatMessage[] {
  try {
    const raw = sessionStorage.getItem(storageKey(contentHash))
    if (!raw) return []
    const msgs: ChatMessage[] = JSON.parse(raw)
    // Migrate old messages that don't have boxIndices / pageIndices
    for (const msg of msgs) {
      if (msg.sources) {
        msg.sources = msg.sources.map(s => ({
          ...s,
          boxIndices: s.boxIndices ?? [s.boxIdx],
          pageIndices: s.pageIndices ?? [s.pageIdx],
        }))
      }
    }
    return msgs
  }
  catch {
    return []
  }
}

function saveMessages (contentHash: string, msgs: ChatMessage[]) {
  try {
    // Don't persist transient loading state
    const toStore = msgs.map(m => ({ ...m, isLoading: undefined }))
    sessionStorage.setItem(storageKey(contentHash), JSON.stringify(toStore))
  }
  catch { /* quota exceeded — silently ignore */ }
}

// ---- Keyword fallback (no vector index) ----
function keywordSources (query: string, pages: Page[], maxResults = 4): ChatSource[] {
  const terms = query.toLowerCase().split(/\s+/).filter(t => t.length > 2)
  const scored: { source: ChatSource; hits: number }[] = []

  for (let pi = 0; pi < pages.length; pi++) {
    const boxes = pages[pi].boxes ?? []
    for (let bi = 0; bi < boxes.length; bi++) {
      const text = boxes[bi].text?.trim() ?? ''
      if (!text) continue
      const lower = text.toLowerCase()
      const hits = terms.reduce((n, t) => n + (lower.includes(t) ? 1 : 0), 0)
      if (hits > 0) {
        scored.push({
          source: {
            pageIdx: pi,
            pageIndices: [pi],
            boxIdx: bi,
            boxIndices: [bi],
            text,
            pageLabel: `Page ${pi + 1}`,
          },
          hits,
        })
      }
    }
  }
  scored.sort((a, b) => b.hits - a.hits)
  return scored.slice(0, maxResults).map(s => s.source)
}

// ---- Convert local messages to backend format (skip bot messages as "assistant") ----
function toBackendHistory (msgs: ChatMessage[]): BackendMessage[] {
  return msgs
    .filter(m => !m.isLoading)
    .map(m => ({
      role: m.role === 'user' ? 'user' : 'assistant',
      content: m.content,
    }))
}

export function useOcrChatbot (getPages: () => Page[], getContentHash?: () => string | undefined, getTaskId?: () => string | undefined) {
  const taskId = getTaskId?.()
  const sessionKey = taskId ?? getContentHash?.()
  const persisted = sessionKey ? loadMessages(sessionKey) : []

  const messages = ref<ChatMessage[]>(persisted)
  const isLoading = ref(false)
  let nextId = (persisted.length ? Math.max(...persisted.map(m => m.id)) + 1 : 1)

  async function sendMessage (content: string) {
    if (!content.trim() || isLoading.value) return

    const userMsg: ChatMessage = { id: nextId++, role: 'user', content }
    messages.value = [...messages.value, userMsg]
    isLoading.value = true

    const currentTaskId = getTaskId?.()

    try {
      // 1. Get embedding for the user query
      let queryVector: number[] | undefined
      try {
        const { data: embedData } = await http.post<EmbedResponse>('/chat/embed', { text: content })
        queryVector = embedData.vector
      }
      catch {
        // embedding failed — we'll skip vector search and use keyword fallback
      }

      // 2. Call /api/chat/ask with full conversation history + task_id
      const history = toBackendHistory(messages.value)
      const { data } = await http.post<AskResponse>('/chat/ask', {
        messages: history,
        task_id: currentTaskId,
        query_vector: queryVector ?? null,
        top_k: 5,
      })

      // 3. Map backend sources to ChatSource
      let sources: ChatSource[] = data.sources.map(s => ({
        pageIdx: s.page_nums[0] ?? 0,
        pageIndices: s.page_nums,
        boxIdx: s.bbox_indices[0] ?? 0,
        boxIndices: s.bbox_indices,
        text: s.text,
        pageLabel: s.page_nums.length > 1
          ? `Pages ${s.page_nums.map(p => p + 1).join(', ')}`
          : `Page ${(s.page_nums[0] ?? 0) + 1}`,
      }))

      // Keyword fallback if backend returned no sources and no vector search
      if (sources.length === 0 && !queryVector) {
        sources = keywordSources(content, getPages())
      }

      const botMsg: ChatMessage = {
        id: nextId++,
        role: 'bot',
        content: data.message.content,
        sources: sources.length > 0 ? sources : undefined,
      }
      messages.value = [...messages.value, botMsg]
    }
    catch (err) {
      // Network / auth error — show a user-friendly message
      messages.value = [
        ...messages.value,
        {
          id: nextId++,
          role: 'bot',
          content: 'Une erreur est survenue lors de la communication avec le serveur. Veuillez réessayer.',
        },
      ]
    }
    finally {
      isLoading.value = false
      const key = getTaskId?.() ?? getContentHash?.()
      if (key) saveMessages(key, messages.value)
    }
  }

  function clearMessages () {
    messages.value = []
    const key = getTaskId?.() ?? getContentHash?.()
    if (key) sessionStorage.removeItem(storageKey(key))
  }

  return { messages, isLoading, sendMessage, clearMessages }
}

