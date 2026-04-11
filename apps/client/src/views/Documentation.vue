<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const md = ref<string | null>(null)
const error = ref<string | null>(null)

async function loadMarkdown() {
  try {
    const resp = await fetch('/docs.md')
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
    const txt = await resp.text()
    // Dynamically import `marked` for Markdown -> HTML conversion.
    try {
      const { marked } = await import('marked')
      md.value = marked.parse(txt)
    } catch (e) {
      // If `marked` is not installed, fall back to showing raw markdown
      md.value = `<pre style="white-space:pre-wrap">${escapeHtml(txt)}</pre>`
      error.value = 'Librairie `marked` non installée — affichage brut. Exécutez `pnpm add marked` pour un rendu HTML.'
    }
  } catch (e: any) {
    error.value = e?.message || String(e)
  }
}

function escapeHtml(s: string) {
  return s.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;')
}

function goBack() {
  if (window.history.length > 1) router.back()
  else router.push('/')
}

onMounted(() => { loadMarkdown() })
</script>

<template>
  <div class="doc-container">
    <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.5rem;">
      <button class="fr-btn fr-btn--tertiary" @click="goBack">Retour</button>
      <h1 style="margin:0">Documentation</h1>
    </div>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="md" v-html="md"></div>
    <div v-else-if="!error">Chargement…</div>
  </div>
</template>

<style scoped>
.doc-container { padding: 1rem; max-width: 800px; margin: 0 auto; }
.error { color: #b91c1c; margin-bottom: 0.75rem }
</style>
