<script setup lang="ts">
import type { components } from '@/api/types/api.schema'
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import OcrViewer from '@/components/OcrViewer.vue'
import OcrTextModal from '@/components/OcrTextModal.vue'
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
      <span
        v-if="task?.type"
        class="px-2 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-600"
      >{{ task.type }}</span>
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
    <div v-else-if="!task?.output">
      <DsfrAlert
        type="warning"
        title="Résultats non disponibles"
        description="Cette tâche n'a pas encore de résultats."
      />
      <DsfrButton
        class="mt-4"
        label="Retour à l'accueil"
        @click="router.push('/')"
      />
    </div>

    <!-- Viewer OCR -->
    <template v-else>
      <OcrViewer
        :data="{ id: task.id, pages: task.output.pages, entities: (task.output as any).entities ?? [] }"
        :content-hash="task.content_hash ?? undefined"
        :result-path="(task.output as any).result_path ?? undefined"
        :template-name="(task as any).parameters?.name ?? undefined"
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
