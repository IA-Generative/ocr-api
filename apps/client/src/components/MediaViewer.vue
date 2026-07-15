<script setup lang="ts">
import { computed, ref } from 'vue'
import useToaster from '@/composables/use-toaster'
import { useOcrStore } from '@/stores/ocr'
import MediaResultViewer from '@/components/MediaResultViewer.vue'

interface TranscriptionSegment {
  start_time: number
  end_time: number
  label: string
  confidence?: number
  text: string
}

interface LanguageTranscript {
  language: string
  is_original: boolean
  segmentations: TranscriptionSegment[]
  text: string
}

interface AudioTranscriptionResult {
  segmentations: TranscriptionSegment[]
  transcription_text: string
  transcripts: LanguageTranscript[]
  extras?: { duration?: number, default_language?: string, [key: string]: unknown } | null
}

const store = useOcrStore()
const { addErrorMessage } = useToaster()

const youtubeUrl = ref('')

const isProcessing = ref(false)
const resultOutput = ref<AudioTranscriptionResult | null>(null)
const resultSourceUrl = ref('')

const youtubeEmbedUrl = computed(() => {
  const match = youtubeUrl.value.match(/(?:youtu\.be\/|[?&]v=|embed\/)([a-zA-Z0-9_-]{11})/)
  return match ? `https://www.youtube.com/embed/${match[1]}` : null
})

const canProcess = computed(() => !!youtubeEmbedUrl.value)

function resetResult() {
  resultOutput.value = null
  resultSourceUrl.value = ''
}

async function pollYoutubeTask(taskId: string, intervalMs = 2000): Promise<void> {
  const task = await store.getTask(taskId)

  if (task.status === 'completed') {
    resultOutput.value = task.output as unknown as AudioTranscriptionResult
    resultSourceUrl.value = youtubeUrl.value
    isProcessing.value = false
    return
  }

  if (task.status === 'failed') {
    const message = typeof task?.extras?.error === 'string' ? task.extras.error : 'Le traitement a échoué'
    addErrorMessage({ title: 'Échec du traitement', description: message })
    isProcessing.value = false
    return
  }

  await new Promise(resolve => setTimeout(resolve, intervalMs))
  await pollYoutubeTask(taskId, intervalMs)
}

async function processMedia() {
  if (!canProcess.value) return

  isProcessing.value = true
  resetResult()

  try {
    const task = await store.createYoutubeTask(youtubeUrl.value)
    await pollYoutubeTask(task.id)
  }
  catch (err) {
    isProcessing.value = false
    addErrorMessage({ title: 'Erreur', description: `Impossible de lancer l'analyse : ${err}` })
  }
}
</script>

<template>
  <div class="media-viewer">
    <div class="my-4 flex flex-wrap gap-2">
      <span title="Fonctionnalité à venir : l'import de vidéo ou de fichier audio sera bientôt disponible.">
        <DsfrButton
          size="sm"
          label="Importer un fichier"
          secondary
          disabled
        />
      </span>
      <DsfrButton
        size="sm"
        label="URL YouTube"
      />
      <span class="fr-badge fr-badge--sm fr-badge--info self-center">Transcription YouTube via yt-dlp — piste description à venir</span>
    </div>

    <div class="mb-4">
      <DsfrInputGroup
        v-model="youtubeUrl"
        label="Lien de la vidéo YouTube"
        hint="Ex : https://www.youtube.com/watch?v=XXXXXXXXXXX"
        placeholder="https://www.youtube.com/watch?v=..."
        @update:model-value="resetResult"
      />
    </div>

    <DsfrButton
      label="Lancer l'analyse"
      size="lg"
      :disabled="!canProcess || isProcessing"
      @click="processMedia"
    />

    <div v-if="isProcessing" class="mt-4 text-sm text-gray-500">
      Récupération de la transcription en cours...
    </div>

    <MediaResultViewer
      v-if="resultOutput"
      :source-url="resultSourceUrl"
      :output="resultOutput"
      class="mt-6"
    />
  </div>
</template>
