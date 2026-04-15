<script setup lang="ts">
import type { components } from '@/api/types/api.schema'
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import OcrViewer from '@/components/OcrViewer.vue'
import OcrTextModal from '@/components/OcrTextModal.vue'
import ClassificationResult from '@/components/ClassificationResult.vue'
import type { ClassificationPage } from '@/components/ClassificationResult.vue'
import { useOcrStore } from '@/stores/ocr'

type TaskModel = components['schemas']['TaskModel']

const route = useRoute()
const router = useRouter()
const store = useOcrStore()

const task = ref<TaskModel | null>(null)
const isLoading = ref(true)
const error = ref<string | null>(null)
const resolvedTaskId = ref<string>('')
const showTextModal = ref(false)

const isClassification = computed(() => task.value?.type === 'page_classification')

const classificationPages = computed<ClassificationPage[]>(() => {
  const pages = task.value?.output?.pages ?? []
  return pages
    .filter((p: any) => p.classifications?.length > 0)
    .map((p: any) => {
      const classifications = p.classifications.map((c: any) => ({
        label: c.label,
        confidence: c.confidence,
        scorePercent: Math.round(Math.max(0, Math.min(100, ((c.confidence + 1) / 2) * 100))),
      }))
      classifications.sort((a: any, b: any) => b.scorePercent - a.scorePercent)
      return {
        page: p.page,
        pageUrl: p.page_url ?? null,
        topLabel: classifications[0]?.label?.label ?? null,
        classifications,
      }
    })
})

onMounted(async () => {
  const taskId = route.params.taskId as string
  resolvedTaskId.value = taskId
  if (!taskId) {
    error.value = 'Identifiant de tâche manquant dans l\'URL.'
    isLoading.value = false
    return
  }
  try {
    task.value = await store.getTask(taskId)
  }
  catch (err: any) {
    error.value = err.message ?? 'Impossible de charger la tâche.'
  }
  finally {
    isLoading.value = false
  }
})

</script>

<template>
  <div>
    <!-- Bouton retour -->
    <div class="mb-4 flex items-center gap-3">
      <DsfrButton
        label="Retour"
        icon="fr-icon-arrow-left-line"
        priority="tertiary"
        @click="router.back()"
      />
      <span class="text-sm text-slate-400 truncate">{{ resolvedTaskId }}</span>
    </div>

    <!-- Chargement -->
    <div
      v-if="isLoading"
      class="flex items-center justify-center py-24 text-slate-400"
    >
      <span class="fr-icon-refresh-line animate-spin mr-2" aria-hidden="true" />
      Chargement des résultats…
    </div>

    <!-- Erreur -->
    <div v-else-if="error">
      <DsfrAlert
        type="error"
        :title="error"
      />
      <DsfrButton
        class="mt-4"
        label="Retour à l'accueil"
        @click="router.push('/')"
      />
    </div>

    <!-- Résultat non disponible -->
    <div v-else-if="!task?.output || (isClassification && classificationPages.length === 0)">
      <DsfrAlert
        type="warning"
        title="Résultats non disponibles"
        :description="isClassification ? 'Cette tâche ne contient pas encore de résultats de classification.' : 'Cette tâche n\'a pas encore de résultats OCR.'"
      />
      <DsfrButton
        class="mt-4"
        label="Retour à l'accueil"
        @click="router.push('/')"
      />
    </div>

    <!-- Résultat Classification -->
    <template v-else-if="isClassification">
      <div class="border border-[var(--border-default-grey)] p-5">
        <ClassificationResult :pages="classificationPages" />
      </div>
    </template>

    <!-- Viewer OCR -->
    <template v-else>
      <OcrViewer
        :data="{ id: task.id, pages: task.output.pages }"
        :content-hash="task.content_hash ?? undefined"
      >
        <template v-if="task.output.text" #extra-actions>
          <button
            class="inline-flex items-center gap-1.5 rounded-xl bg-slate-100 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-200 transition-colors"
            @click="showTextModal = true"
          >
            <span class="fr-icon-file-text-line" style="font-size: 14px;" aria-hidden="true" />
            Voir le texte
          </button>
        </template>
      </OcrViewer>

      <OcrTextModal
        v-if="showTextModal && task.output.text"
        :text="task.output.text"
        :filename="task.input?.raw_filename ?? null"
        @close="showTextModal = false"
      />
    </template>
  </div>
</template>
