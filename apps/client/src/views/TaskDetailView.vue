<script setup lang="ts">
import type { components } from '@/api/types/api.schema'
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import OcrViewer from '@/components/OcrViewer.vue'
import SideBar from '@/components/SideBar.vue'
import { useOcrStore } from '@/stores/ocr'

type TaskModel = components['schemas']['TaskModel']

const route = useRoute()
const router = useRouter()
const store = useOcrStore()

const task = ref<TaskModel | null>(null)
const loading = ref(true)
const loadError = ref<string | null>(null)

const taskId = computed(() => String(route.params.id))

function formatSize (size: number | null | undefined) {
  if (size === null || size === undefined) {
    return '—'
  }
  if (size < 1024) {
    return `${size} o`
  }
  if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(1)} Ko`
  }
  return `${(size / (1024 * 1024)).toFixed(1)} Mo`
}

function formatDate (ts: any) {
  if (ts === null || ts === undefined || ts === '') {
    return ''
  }
  try {
    let n = Number(ts)
    if (Number.isNaN(n)) {
      return String(ts)
    }
    if (n < 1e12) {
      n = n * 1000
    }
    return new Date(n).toLocaleString()
  }
  catch {
    return String(ts)
  }
}

async function load () {
  loading.value = true
  loadError.value = null
  try {
    task.value = await store.getTask(taskId.value)
  }
  catch (err: any) {
    loadError.value = err?.message ?? 'Erreur inconnue'
  }
  finally {
    loading.value = false
  }
}

onMounted(() => {
  void load()
})

function goBack () {
  router.push('/')
}
</script>

<template>
  <div class="main-page">
    <SideBar :other-tools="[]" />
    <div class="main-page__container">
      <div class="mt-[35px]">
        <DsfrButton
          size="sm"
          priority="tertiary"
          @click="goBack"
        >
          ← Retour à la liste des tâches
        </DsfrButton>

        <h1 class="flex items-center gap-3">
          <span>Détail de la tâche</span>
        </h1>
      </div>

      <div v-if="loading">
        Chargement…
      </div>

      <DsfrAlert
        v-else-if="loadError"
        type="error"
        :description="loadError"
      />

      <template v-else-if="task">
        <dl class="detail-list">
          <div class="detail-item">
            <dt>ID de tâche</dt>
            <dd class="mono">
              {{ task.id }}
            </dd>
          </div>
          <div class="detail-item">
            <dt>Fichier</dt>
            <dd>{{ task.input?.raw_filename ?? '—' }}</dd>
          </div>
          <div class="detail-item">
            <dt>Statut</dt>
            <dd>{{ task.status }}</dd>
          </div>
          <div class="detail-item">
            <dt>Type de contenu</dt>
            <dd>{{ task.input?.content_type ?? '—' }}</dd>
          </div>
          <div class="detail-item">
            <dt>Taille du fichier</dt>
            <dd>{{ formatSize(task.input?.size) }}</dd>
          </div>
          <div class="detail-item">
            <dt>Modèle utilisé</dt>
            <dd>{{ task.output?.model_name ?? '—' }}</dd>
          </div>
          <div class="detail-item">
            <dt>Nombre de pages</dt>
            <dd>{{ task.output?.total_pages ?? '—' }}</dd>
          </div>
          <div class="detail-item">
            <dt>Créé le</dt>
            <dd>{{ formatDate(task.created_at) }}</dd>
          </div>
          <div class="detail-item">
            <dt>Mis à jour le</dt>
            <dd>{{ formatDate(task.updated_at) }}</dd>
          </div>
          <div class="detail-item">
            <dt>Hash du contenu</dt>
            <dd class="mono">
              {{ task.content_hash ?? '—' }}
            </dd>
          </div>
          <div
            v-if="task.status === 'failed' && task.extras?.error"
            class="detail-item detail-item--error"
          >
            <dt>Erreur</dt>
            <dd>{{ task.extras.error }}</dd>
          </div>
        </dl>

        <div class="flex justify-center">
          <OcrViewer
            v-if="task.status === 'completed' && task.output?.pages?.length"
            :data="{ id: task.id, pages: task.output.pages }"
          />
          <p
            v-else-if="task.status === 'completed'"
            class="no-preview"
          >
            Aucun aperçu disponible pour cette tâche.
          </p>
          <p
            v-else
            class="no-preview"
          >
            La tâche n'est pas terminée — aucun aperçu à afficher pour le moment.
          </p>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.detail-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 8px 24px;
  margin: 24px 0;
}

.detail-item {
  display: flex;
  flex-direction: column;
}

.detail-item dt {
  font-size: 0.75rem;
  font-weight: bold;
  color: #666;
}

.detail-item dd {
  margin: 0;
  overflow-wrap: anywhere;
}

.detail-item--error dd {
  color: #c00;
}

.mono {
  font-family: monospace;
}

.no-preview {
  color: #666;
  font-style: italic;
}
</style>
