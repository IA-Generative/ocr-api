<script setup lang="ts">
import type { components } from '@/api/types/api.schema'
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MediaResultViewer from '@/components/MediaResultViewer.vue'
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
const isYoutubeTask = computed(() => task.value?.input?.content_type === 'video/youtube')
// `api.schema.d.ts` est généré depuis l'OpenAPI serveur et n'a pas encore été régénéré
// depuis l'ajout du type de tâche média (source_url / AudioTranscriptionResult côté serveur).
const mediaSourceUrl = computed(() => (task.value?.input as { source_url?: string } | undefined)?.source_url ?? '')

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
        <!-- Bandeau métadonnées DSFR -->
        <div class="fr-callout fr-callout--blue-cumulus fr-mb-3w fr-mt-2w">
          <div class="fr-callout__text">
            <!-- Ligne 1 : nom fichier + statut + type -->
            <div class="fr-grid-row fr-grid-row--gutters fr-grid-row--middle fr-mb-1w">
              <div class="fr-col fr-col-12 fr-col-md-auto">
                <p class="fr-text--xl fr-text--bold fr-mb-0">
                  <span class="fr-icon-file-line fr-mr-1w" aria-hidden="true" />
                  {{ task.input?.raw_filename ?? 'Fichier inconnu' }}
                </p>
              </div>
              <div class="fr-col-auto">
                <p
                  class="fr-badge fr-mb-0"
                  :class="{
                    'fr-badge--success': task.status === 'completed',
                    'fr-badge--error': task.status === 'failed',
                    'fr-badge--warning': ['in_progress', 'started', 'retrying'].includes(task.status),
                    'fr-badge--info': ['queued', 'created'].includes(task.status),
                  }"
                >
                  {{ task.status }}
                </p>
              </div>
              <div v-if="task.input?.content_type" class="fr-col-auto">
                <p class="fr-badge fr-badge--new fr-mb-0">
                  {{ task.input.content_type.split('/').pop() }}
                </p>
              </div>
            </div>

            <!-- Ligne 2 : métriques clés -->
            <div class="fr-grid-row fr-grid-row--gutters fr-text--sm fr-text--mention-grey">
              <div class="fr-col-auto">
                <span class="fr-icon-price-tag-3-line fr-mr-1v" aria-hidden="true" />
                <span class="fr-text--bold">ID :</span>
                <code class="fr-ml-1v">{{ task.id }}</code>
              </div>
              <div v-if="task.input?.size" class="fr-col-auto">
                <span class="fr-icon-file-download-line fr-mr-1v" aria-hidden="true" />
                {{ formatSize(task.input.size) }}
              </div>
              <div v-if="task.output?.total_pages" class="fr-col-auto">
                <span class="fr-icon-article-line fr-mr-1v" aria-hidden="true" />
                {{ task.output.total_pages }} page{{ task.output.total_pages > 1 ? 's' : '' }}
              </div>
              <div v-if="task.output?.model_name" class="fr-col-auto">
                <span class="fr-icon-robot-2-line fr-mr-1v" aria-hidden="true" />
                {{ task.output.model_name }}
              </div>
              <div class="fr-col-auto">
                <span class="fr-icon-calendar-event-line fr-mr-1v" aria-hidden="true" />
                {{ formatDate(task.created_at) }}
              </div>
              <div v-if="task.updated_at !== task.created_at" class="fr-col-auto">
                <span class="fr-icon-refresh-line fr-mr-1v" aria-hidden="true" />
                mis à jour {{ formatDate(task.updated_at) }}
              </div>
            </div>

            <!-- Erreur éventuelle -->
            <DsfrAlert
              v-if="task.status === 'failed' && task.extras?.error"
              type="error"
              :description="String(task.extras.error)"
              class="fr-mt-2w"
            />
          </div>
        </div>

        <div class="flex justify-center">
          <MediaResultViewer
            v-if="task.status === 'completed' && isYoutubeTask && task.output"
            :source-url="mediaSourceUrl"
            :output="(task.output as any)"
            class="w-full max-w-4xl"
          />
          <OcrViewer
            v-else-if="task.status === 'completed' && task.output?.pages?.length"
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
.no-preview {
  color: var(--text-mention-grey);
  font-style: italic;
}
</style>
