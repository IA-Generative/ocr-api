<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { OCR_API_URL } from '@/utils/constants'
import createHttpClient from '@/api/http-client'

const http = createHttpClient(OCR_API_URL)

const emit = defineEmits<{ close: [] }>()

const token = ref<string | null>(null)
const generating = ref(false)

type TokenItem = {
  id: string
  token: string
  created: string
  expires?: string | null
}

const tokenType = ref<'one_hour' | 'one_day' | 'one_week' | 'custom'>('one_hour')
const customExpiry = ref<string | null>(null)
const tokenList = ref<TokenItem[]>([])
const createStatus = ref<string | null>(null)
const router = useRouter()
const visibleOnce = ref(false)

const PAGE_SIZE = 5
const currentPage = ref(1)
const totalPages = computed(() => Math.max(1, Math.ceil(tokenList.value.length / PAGE_SIZE)))
const pagedTokenList = computed(() => {
  const start = (currentPage.value - 1) * PAGE_SIZE
  return tokenList.value.slice(start, start + PAGE_SIZE)
})
let visibleTimer: number | null = null

function setVisibleOnce(seconds = 8) {
  visibleOnce.value = true
  if (visibleTimer) window.clearTimeout(visibleTimer)
  visibleTimer = window.setTimeout(() => {
    visibleOnce.value = false
    visibleTimer = null
  }, seconds * 1000)
}

function formatDate(iso?: string | null) {
  if (!iso) return ''
  try {
    const d = new Date(iso)
    return d.toLocaleString()
  } catch {
    return iso
  }
}

function formatRelative(iso?: string | null) {
  if (!iso) return ''
  const d = new Date(iso).getTime()
  const now = Date.now()
  const diff = Math.round((now - d) / 1000) // seconds; positive => past
  const abs = Math.abs(diff)
  if (abs < 60) return diff >= 0 ? "à l'instant" : "dans quelques secondes"
  if (abs < 3600) return diff >= 0 ? `il y a ${Math.round(abs / 60)} min` : `dans ${Math.round(abs / 60)} min`
  if (abs < 86400) return diff >= 0 ? `il y a ${Math.round(abs / 3600)} h` : `dans ${Math.round(abs / 3600)} h`
  return diff >= 0 ? `${Math.round(abs / 86400)} j` : `dans ${Math.round(abs / 86400)} j`
}

function timeRemaining(iso?: string | null) {
  if (!iso) return { text: 'Jamais', variant: 'badge--info' }
  const t = new Date(iso).getTime()
  const seconds = Math.round((t - Date.now()) / 1000)
  if (seconds <= 0) return { text: 'Expiré', variant: 'badge--danger' }
  if (seconds < 60) return { text: `dans ${seconds}s`, variant: 'badge--warning' }
  if (seconds < 3600) return { text: `dans ${Math.round(seconds / 60)} min`, variant: 'badge--warning' }
  if (seconds < 86400) return { text: `dans ${Math.round(seconds / 3600)} h`, variant: 'badge--info' }
  return { text: `dans ${Math.round(seconds / 86400)} j`, variant: 'badge--info' }
}

function computeExpiry (created: Date, type: typeof tokenType.value, customDate?: string | null) {
  if (type === 'custom') {
    if (!customDate) return null
    // customDate is YYYY-MM-DD (date-only) — set expiry to end of that day
    const parsedEnd = new Date(customDate + 'T23:59:59')
    if (isNaN(parsedEnd.getTime())) return null
    return parsedEnd.toISOString()
  }
  const d = new Date(created)
  if (type === 'one_hour') d.setHours(d.getHours() + 1)
  else if (type === 'one_day') d.setDate(d.getDate() + 1)
  else if (type === 'one_week') d.setDate(d.getDate() + 7)
  return d.toISOString()
}

async function generateAndCreateToken() {
  generating.value = true
  try {
    const value = 'tk-' + Array.from(crypto.getRandomValues(new Uint8Array(32))).map(b => b.toString(16).padStart(2, '0')).join('')
    const created = new Date()
    const expires = computeExpiry(created, tokenType.value, customExpiry.value)
    const payload = { token: value, expired_at: expires ? Math.floor(new Date(expires).getTime() / 1000) : null }

    const { data } = await http.post('/v1/tokens/', payload)
    token.value = data.token ?? value
    setVisibleOnce(8)
    createStatus.value = 'Token créé et enregistré sur le serveur.'
    await fetchTokensFromServer()
  } catch (err: any) {
    const status = err?.response?.status
    if (status === 401) createStatus.value = 'Non autorisé — vérifiez votre clé API.'
    else if (status) createStatus.value = `Erreur serveur (${status}).`
    else createStatus.value = 'Serveur indisponible.'
  } finally {
    generating.value = false
  }
}



// Fix: was checking the ref object (always truthy) instead of .value
const customExpiryInvalid = computed(() => {
  if (!customExpiry.value) return true
  const end = new Date(customExpiry.value + 'T23:59:59')
  return isNaN(end.getTime()) || end.getTime() <= Date.now()
})

async function copyToClipboard(text: string) {
  try {
    if (navigator?.clipboard?.writeText) {
      await navigator.clipboard.writeText(text)
    } else {
      const ta = document.createElement('textarea')
      ta.value = text
      ta.style.position = 'fixed'
      ta.style.opacity = '0'
      document.body.appendChild(ta)
      ta.focus()
      ta.select()
      document.execCommand('copy')
      document.body.removeChild(ta)
    }
  } catch {}
}

async function revoke(id: string) {
  try {
    await http.delete(`/v1/tokens/${encodeURIComponent(id)}`)
    createStatus.value = 'Token supprimé.'
  } catch (err: any) {
    if (err?.response?.status === 404) {
      createStatus.value = 'Token supprimé.'
    } else {
      createStatus.value = `Suppression échouée (${err?.response?.status ?? 'réseau'})`
      return
    }
  }
  tokenList.value = tokenList.value.filter(t => t.id !== id)
  if (tokenList.value.length === 0) token.value = null
}

async function fetchTokensFromServer() {
  try {
    const { data } = await http.get('/v1/tokens/')
    tokenList.value = (data || [])
      .map((r: any) => ({
        id: r.id,
        token: r.token ?? null,
        created: r.created_at ? new Date(r.created_at * 1000).toISOString() : new Date().toISOString(),
        expires: r.expired_at ? new Date(r.expired_at * 1000).toISOString() : null,
      }))
      .sort((a: TokenItem, b: TokenItem) => new Date(b.created).getTime() - new Date(a.created).getTime())
    createStatus.value = `${tokenList.value.length} token(s) chargé(s).`
    currentPage.value = 1
  } catch (err: any) {
    createStatus.value = `Erreur réseau lors de la récupération des tokens (${err?.response?.status ?? 'réseau'}).`
  }
}

function viewToken(t: TokenItem) {
  token.value = t.token
  setVisibleOnce(8)
}

onMounted(() => { fetchTokensFromServer() })

function goDocs() {
  emit('close')
  router.push('/docs')
}

</script>

<template>
  <Teleport to="body">
    <div class="modal-overlay" role="presentation" @click.self="emit('close')">
      <div class="modal-panel" role="dialog" aria-modal="true" aria-label="Générateur de token">
        <div class="modal-header">
          <h2 class="modal-title">Générer un token</h2>
          <button class="modal-close-btn" aria-label="Fermer" @click="emit('close')">
            <span class="fr-icon-close-line" aria-hidden="true" />
          </button>
        </div>

        <div class="modal-body">
          <p>Liste des tokens pour l'utilisateur :</p>

          <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem">
            <button class="fr-btn fr-btn--sm fr-btn--secondary" @click="fetchTokensFromServer">Actualiser</button>
          </div>

          <div v-if="tokenList.length === 0" style="color:#64748b;margin-bottom:0.75rem">Aucun token trouvé pour cet utilisateur.</div>
          <div v-else class="token-list" style="margin-bottom:0.75rem">
            <div v-for="t in pagedTokenList" :key="t.id" class="token-item">
              <div style="display:flex;flex-direction:column;gap:0.25rem;min-width:0;">
                <div class="token-value">{{ t.token ? ((visibleOnce && token === t.token) ? t.token : (t.token.slice(0,4) + '…' + t.token.slice(-4))) : '(masqué)' }}</div>
                <div style="display:flex;gap:0.5rem;align-items:center;flex-wrap:wrap">
                  <div class="badge">Créé: <strong style="margin-left:0.4rem">{{ formatDate(t.created) }}</strong></div>
                  <div class="badge badge--muted">{{ formatRelative(t.created) }}</div>
                  <div v-if="t.expires" :class="['badge', timeRemaining(t.expires).variant]">Expire: <strong style="margin-left:0.4rem">{{ formatDate(t.expires) }}</strong></div>
                </div>
              </div>
              <div class="token-controls" style="display:flex;flex-direction:column;gap:0.25rem;align-items:flex-end">
                <button type="button" class="fr-btn fr-btn--sm fr-btn--secondary" @click="viewToken(t)" :disabled="!t.token">Voir</button>
                <button type="button" class="fr-btn fr-btn--tertiary fr-btn--sm" @click="revoke(t.id)">Supprimer</button>
              </div>
            </div>
          </div>

          <div v-if="totalPages > 1" class="pagination">
            <button class="pg-btn" :disabled="currentPage === 1" @click="currentPage--">&lsaquo;</button>
            <button
              v-for="p in totalPages" :key="p"
              :class="['pg-btn', { 'pg-btn--active': p === currentPage }]"
              @click="currentPage = p"
            >{{ p }}</button>
            <button class="pg-btn" :disabled="currentPage === totalPages" @click="currentPage++">&rsaquo;</button>
          </div>

          <hr style="border:none;border-top:1px solid #eef2ff;margin:0.5rem 0 1rem 0" />

          <p>Générer un nouveau token (choisir la durée/expiration) :</p>

          <div class="token-config">
            <label class="token-label">Expiration :</label>
            <select v-model="tokenType" class="token-select">
              <option value="one_hour">1 heure</option>
              <option value="one_day">24 heures</option>
              <option value="one_week">7 jours</option>
              <option value="custom">Date personnalisée...</option>
            </select>

            <div v-if="tokenType === 'custom'" style="display:flex;gap:0.5rem;align-items:center;margin-top:0.5rem;">
              <input type="date" v-model="customExpiry" class="token-select" />
              <div style="color:#e11d48;font-size:0.85rem;" v-if="customExpiryInvalid">Date invalide (doit être future ou aujourd'hui)</div>
            </div>

            <div class="token-row">
              <input class="token-input" :value="token ?? ''" readonly placeholder="Aucun token généré" />
              <div class="token-actions">
                <button class="fr-btn fr-btn--sm" :disabled="generating || (tokenType === 'custom' && customExpiryInvalid)" @click="generateAndCreateToken">
                  {{ generating ? 'Génération...' : 'Générer' }}
                </button>
                <button class="fr-btn fr-btn--secondary fr-btn--sm" v-if="visibleOnce && token" @click="copyToClipboard(token!)">Copier</button>
              </div>
            </div>

            <div style="color:#64748b;font-size:0.85rem;margin-top:0.5rem;">Le token est affiché uniquement juste après la génération pour des raisons de sécurité.</div>
          
            <div v-if="createStatus" style="margin-top:0.5rem;color:#0f172a">{{ createStatus }}</div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="fr-btn fr-btn--secondary" @click="fetchTokensFromServer">Actualiser</button>
          <button class="fr-btn fr-btn--secondary" @click="goDocs">Voir la documentation</button>
          <button class="fr-btn fr-btn--tertiary" @click="emit('close')">Fermer</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-overlay { position: fixed; inset: 0; z-index: 60; display:flex; align-items:center; justify-content:center; padding:1.25rem; background: rgba(15,23,42,0.55); }
.modal-panel { width:100%; max-width:48rem; border-radius:0.75rem; background:#fff; box-shadow:0 20px 48px rgba(2,6,23,0.3); overflow:hidden; display:flex; flex-direction:column; }
.modal-header { display:flex; align-items:center; justify-content:space-between; padding:1rem 1.25rem; border-bottom:1px solid #f1f5f9; }
.modal-title { margin:0; font-size:1rem; font-weight:600; }
.modal-close-btn { background:transparent; border:none; color:#94a3b8; width:2rem; height:2rem; border-radius:9999px; cursor:pointer; }
.modal-body { padding:1rem 1.25rem; background:#f8fafc; }
.token-row { display:flex; gap:0.5rem; align-items:center; margin-top:0.75rem; }
.token-input { flex:1; padding:0.5rem 0.75rem; border-radius:0.5rem; border:1px solid #e2e8f0; background:#fff; }
.token-actions { display:flex; gap:0.5rem; }
.examples-title { margin-top:0.75rem; margin-bottom:0.5rem; font-size:0.9375rem; }
.example-block { background:#fff; border:1px solid #e6eefc; border-radius:0.5rem; padding:0.5rem; margin-bottom:0.75rem; }
.example-header { display:flex; justify-content:space-between; align-items:center; gap:0.5rem; margin-bottom:0.5rem; }
.example-code { background:#0f172a; color:#e6eefc; padding:0.75rem; border-radius:0.375rem; overflow:auto; font-size:0.8125rem; white-space:pre-wrap; }
.token-config { display:flex; flex-direction:column; gap:0.5rem; }
.token-label { font-size:0.875rem; color:#334155; }
.token-select { padding:0.4rem 0.6rem; border-radius:0.375rem; border:1px solid #e2e8f0; max-width:16rem; }
.token-list { list-style:none; padding:0; margin:0.5rem 0 0 0; display:flex; flex-direction:column; gap:0.5rem; }
.token-item { display:flex; align-items:center; justify-content:space-between; padding:0.5rem; background:#fff; border:1px solid #eef2ff; border-radius:0.5rem; }
.token-value { font-family:monospace; font-size:0.875rem; color:#0f172a; }
.token-value { overflow-wrap:anywhere; max-width:22rem }
.token-meta { font-size:0.75rem; color:#64748b; margin-top:0.25rem; }
.token-main { display:flex; flex-direction:column; }
.token-controls { display:flex; gap:0.5rem; }
.modal-footer { padding:0.75rem 1.25rem; border-top:1px solid #f1f5f9; display:flex; justify-content:flex-end; gap:0.5rem; }
.pagination { display:flex; align-items:center; gap:0.25rem; margin-bottom:0.75rem; }
.pg-btn { min-width:2rem; height:2rem; padding:0 0.4rem; border-radius:0.375rem; border:1px solid #e2e8f0; background:#fff; color:#334155; font-size:0.875rem; cursor:pointer; transition:background 0.1s; }
.pg-btn:hover:not(:disabled) { background:#eef2ff; }
.pg-btn:disabled { opacity:0.4; cursor:default; }
.pg-btn--active { background:#2563eb; color:#fff; border-color:#2563eb; font-weight:600; }
.badge { display:inline-block; background:#eef2ff; color:#0f172a; padding:0.25rem 0.5rem; border-radius:0.5rem; font-size:0.85rem; margin-right:0.25rem }
.badge--warning { background:#fff7ed; color:#92400e }
.badge--danger { background:#fee2e2; color:#991b1b }
.badge--info { background:#ecfeff; color:#0f766e }
.badge--muted { background:transparent; color:#64748b; padding:0 }
</style>