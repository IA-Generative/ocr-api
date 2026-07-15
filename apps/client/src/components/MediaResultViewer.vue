<script setup lang="ts">
import { computed, ref } from 'vue'

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

const props = defineProps<{
  sourceUrl: string
  output: AudioTranscriptionResult
}>()

const currentTime = ref(0)

const duration = computed(() => {
  const backendDuration = props.output.extras?.duration
  return typeof backendDuration === 'number' ? backendDuration : 0
})

const transcripts = computed(() => props.output.transcripts ?? [])

const defaultLanguage = computed(() => {
  const preferred = props.output.extras?.default_language
  if (preferred && transcripts.value.some(t => t.language === preferred)) return preferred
  return transcripts.value[0]?.language ?? null
})

const selectedLanguage = ref<string | null>(null)
const effectiveLanguage = computed(() => selectedLanguage.value ?? defaultLanguage.value)

const transcription = computed<TranscriptionSegment[]>(() => {
  const current = transcripts.value.find(t => t.language === effectiveLanguage.value)
  return current?.segmentations ?? []
})

const currentTranscriptText = computed(() => {
  const current = transcripts.value.find(t => t.language === effectiveLanguage.value)
  return current?.text ?? ''
})

const languageDisplayNames = typeof Intl !== 'undefined' && 'DisplayNames' in Intl
  ? new Intl.DisplayNames(['fr'], { type: 'language' })
  : null

function languageLabel(transcript: LanguageTranscript): string {
  let label = transcript.language
  try {
    label = languageDisplayNames?.of(transcript.language) ?? transcript.language
  }
  catch {
    label = transcript.language
  }
  return transcript.is_original ? `${label} (langue d'origine)` : label
}

const youtubeEmbedUrl = computed(() => {
  const match = props.sourceUrl.match(/(?:youtu\.be\/|[?&]v=|embed\/)([a-zA-Z0-9_-]{11})/)
  return match ? `https://www.youtube.com/embed/${match[1]}` : null
})

function seekTo(time: number) {
  currentTime.value = time
}

function onTimelineInput(e: Event) {
  seekTo(Number((e.target as HTMLInputElement).value))
}

function formatTime(seconds: number): string {
  if (!Number.isFinite(seconds) || seconds < 0) return '00:00'
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}

function segmentStyle(seg: { start_time: number, end_time: number }) {
  const total = duration.value || 1
  const left = (seg.start_time / total) * 100
  const width = ((seg.end_time - seg.start_time) / total) * 100
  return { left: `${left}%`, width: `${Math.max(width, 0.5)}%` }
}

function isActiveSegment(seg: { start_time: number, end_time: number }) {
  return currentTime.value >= seg.start_time && currentTime.value < seg.end_time
}

const playheadStyle = computed(() => ({ left: `${(currentTime.value / (duration.value || 1)) * 100}%` }))

const activeTranscriptionSegment = computed(() => transcription.value.find(isActiveSegment))

function downloadTranscription() {
  if (!currentTranscriptText.value) return
  const blob = new Blob([currentTranscriptText.value], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `transcription-${effectiveLanguage.value ?? 'texte'}.txt`
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}
</script>

<template>
  <div class="media-result-viewer">
    <div v-if="youtubeEmbedUrl" class="media-player">
      <iframe
        :src="youtubeEmbedUrl"
        class="w-full aspect-video"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen
      />
      <p class="text-xs text-gray-500 mt-1">
        La lecture YouTube n'est pas synchronisée avec la timeline dans cet aperçu : utilisez le curseur ci-dessous pour simuler la position de lecture.
      </p>
    </div>

    <div class="mt-6 timeline">
      <div class="flex items-center justify-between text-sm mb-1">
        <span>{{ formatTime(currentTime) }}</span>
        <span>{{ formatTime(duration) }}</span>
      </div>

      <input
        type="range"
        class="w-full"
        min="0"
        :max="duration"
        step="0.1"
        :value="currentTime"
        @input="onTimelineInput"
      >

      <div class="track-group mt-4">
        <div class="flex flex-wrap items-center justify-between gap-2 mb-1">
          <div class="track-label mb-0">
            Transcription
          </div>
          <div v-if="transcripts.length" class="flex flex-wrap items-center gap-2">
            <div class="flex gap-1">
              <button
                v-for="t in transcripts"
                :key="t.language"
                type="button"
                class="lang-chip"
                :class="{ 'lang-chip--active': t.language === effectiveLanguage }"
                @click="selectedLanguage = t.language"
              >
                {{ languageLabel(t) }}
              </button>
            </div>
            <DsfrButton
              size="sm"
              label="Télécharger"
              secondary
              @click="downloadTranscription"
            />
          </div>
        </div>
        <div class="track">
          <div class="playhead" :style="playheadStyle" />
          <button
            v-for="(seg, idx) in transcription"
            :key="idx"
            class="segment"
            :class="{ 'segment--active': isActiveSegment(seg) }"
            :style="segmentStyle(seg)"
            :title="seg.text"
            @click="seekTo(seg.start_time)"
          />
        </div>
        <p class="caption">
          {{ activeTranscriptionSegment?.text ?? '—' }}
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.media-player iframe {
  border-radius: 4px;
}

.track-label {
  font-weight: 700;
  font-size: 0.85rem;
  margin-bottom: 4px;
}

.track {
  position: relative;
  height: 28px;
  background-color: var(--info-950-100, #eee);
  border-radius: 4px;
  overflow: hidden;
}

.segment {
  position: absolute;
  top: 2px;
  bottom: 2px;
  border: none;
  border-radius: 3px;
  background-color: var(--background-flat-info, #b8d6ff);
  cursor: pointer;
  padding: 0;
}

.segment--active {
  background-color: var(--artwork-major-blue-france, #0063cb);
}

.playhead {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 2px;
  background-color: #d00;
  z-index: 5;
  pointer-events: none;
}

.caption {
  margin-top: 6px;
  font-size: 0.9rem;
  min-height: 1.2em;
}

.lang-chip {
  border: 1px solid var(--border-default-grey, #929292);
  background: transparent;
  border-radius: 999px;
  padding: 2px 10px;
  font-size: 0.8rem;
  cursor: pointer;
}

.lang-chip--active {
  background-color: var(--artwork-major-blue-france, #0063cb);
  border-color: var(--artwork-major-blue-france, #0063cb);
  color: white;
}
</style>
