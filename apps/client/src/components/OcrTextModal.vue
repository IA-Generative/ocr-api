<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  text: string
  filename?: string | null
}>()

const emit = defineEmits<{ close: [] }>()

const copySuccess = ref(false)
let _copyTimeout: any = null

async function copyToClipboard(text: string) {
  try {
    if (navigator?.clipboard?.writeText) {
      await navigator.clipboard.writeText(text)
    }
    else {
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
    copySuccess.value = true
    clearTimeout(_copyTimeout)
    _copyTimeout = setTimeout(() => { copySuccess.value = false }, 2000)
  }
  catch {}
}
</script>

<template>
  <Teleport to="body">
    <!-- Overlay -->
    <div
      class="modal-overlay"
      role="presentation"
      @click.self="emit('close')"
    >
      <!-- Panel -->
      <div
        class="modal-panel"
        role="dialog"
        aria-modal="true"
        aria-label="Contenu textuel du document"
      >
        <!-- Header -->
        <div class="modal-header">
          <div class="flex items-center gap-2">
            <span class="fr-icon-file-text-line modal-header-icon" aria-hidden="true" />
            <div>
              <h2 class="modal-title">
                Contenu extrait
              </h2>
              <p
                v-if="filename"
                class="modal-subtitle"
              >
                {{ filename }}
              </p>
            </div>
          </div>
          <button
            class="modal-close-btn"
            aria-label="Fermer"
            @click="emit('close')"
          >
            <span class="fr-icon-close-line" aria-hidden="true" />
          </button>
        </div>

        <!-- Contenu texte -->
        <div class="modal-body">
          <pre class="modal-text">{{ text }}</pre>
        </div>

        <!-- Footer -->
        <div class="modal-footer">
          <button
            class="copy-btn"
            :class="{ 'copy-btn--success': copySuccess }"
            @click="copyToClipboard(text)"
          >
            <span
              :class="copySuccess ? 'fr-icon-check-line' : 'fr-icon-clipboard-line'"
              style="font-size: 14px;"
              aria-hidden="true"
            />
            {{ copySuccess ? 'Copié !' : 'Copier le texte' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background: rgba(15, 23, 42, 0.55);
  backdrop-filter: blur(4px);
}

.modal-panel {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 52rem;
  max-height: 90vh;
  border-radius: 1.25rem;
  background: #fff;
  box-shadow: 0 24px 64px -12px rgba(15, 23, 42, 0.25);
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #f1f5f9;
  flex-shrink: 0;
}

.modal-header-icon {
  font-size: 1.25rem;
  color: #3b82f6;
  margin-top: 2px;
}

.modal-title {
  font-size: 0.9375rem;
  font-weight: 600;
  color: #0f172a;
  line-height: 1.4;
  margin: 0;
}

.modal-subtitle {
  font-size: 0.75rem;
  color: #94a3b8;
  margin: 0.125rem 0 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 36rem;
}

.modal-close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  flex-shrink: 0;
  border-radius: 9999px;
  border: none;
  background: transparent;
  color: #94a3b8;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}
.modal-close-btn:hover {
  background: #f1f5f9;
  color: #334155;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.25rem 1.5rem;
  background: #f8fafc;
}

.modal-text {
  margin: 0;
  font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
  font-size: 0.8125rem;
  line-height: 1.75;
  color: #334155;
  white-space: pre-wrap;
  word-break: break-word;
}

.modal-footer {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #f1f5f9;
  flex-shrink: 0;
}

.copy-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 1rem;
  border-radius: 0.625rem;
  border: 1.5px solid #e2e8f0;
  background: #fff;
  font-size: 0.8125rem;
  font-weight: 500;
  color: #475569;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s, color 0.15s;
}
.copy-btn:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
  color: #1e293b;
}
.copy-btn--success {
  border-color: #6ee7b7;
  background: #ecfdf5;
  color: #059669;
}
</style>
