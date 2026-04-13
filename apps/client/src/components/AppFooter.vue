<script setup lang="ts">
import { ref, onMounted } from 'vue'
import createHttpClient from '@/api/http-client'
import { OCR_API_URL } from '@/utils/constants'

const version = ref<string>('')
const http = createHttpClient(OCR_API_URL)

async function loadVersion() {
  try {
    const resp = await http.get('/health')
    version.value = resp.data?.version ?? ''
  }
  catch (e) {
    console.warn('Failed fetching health/version:', e)
    version.value = ''
  }
}

onMounted(() => {
  loadVersion()
})
</script>

<template>
  <footer class="fr-container fr-mt-4w fr-mb-4w" aria-hidden="false">
    <div style="text-align:center;color:var(--text-muted, #64748b);font-size:0.875rem">Version {{ version }}</div>
  </footer>
</template>

<style scoped>
/* minimal styling, keep consistent with DSFR spacing */
</style>
