<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center p-4"
    style="background: rgba(15,23,42,0.35); backdrop-filter: blur(3px);"
    @click.self="$emit('close')"
  >
    <div
      class="w-full max-w-2xl rounded-2xl bg-white shadow-2xl flex flex-col max-h-[90vh]"
      @click.stop
    >
      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-slate-100">
        <div>
          <h2 class="text-base font-semibold text-slate-800">Lancer l'extraction</h2>
          <p class="text-xs text-slate-400 mt-0.5">Template : {{ template.name }}</p>
        </div>
        <button
          class="text-slate-400 hover:text-slate-600 transition-colors"
          aria-label="Fermer"
          @click="$emit('close')"
        >
          <span class="fr-icon-close-line" aria-hidden="true" />
        </button>
      </div>

      <!-- Body -->
      <div class="flex-1 overflow-y-auto px-6 py-5">
        <p class="text-sm text-slate-500 mb-4">
          Sélectionnez les fichiers sur lesquels appliquer le template
          <span class="font-medium text-slate-700">{{ template.name }}</span>.
        </p>

        <!-- Drop zone -->
        <div
          class="border-2 border-dashed rounded-lg p-6 text-center transition-colors cursor-pointer"
          :class="isDragging ? 'border-blue-france bg-blue-50' : 'border-slate-300 hover:border-slate-400'"
          @dragover.prevent="isDragging = true"
          @dragleave="isDragging = false"
          @drop.prevent="onDrop"
          @click="fileInputRef?.click()"
        >
          <span class="fr-icon-upload-2-line text-slate-400" style="font-size: 2rem;" aria-hidden="true" />
          <p class="text-sm text-slate-500 mt-2">
            Glissez-déposez vos fichiers ici ou
            <span class="text-blue-france font-medium">parcourir</span>
          </p>
          <p class="text-xs text-slate-400 mt-1">PDF, images (PNG, JPG, TIFF)</p>
          <input
            ref="fileInputRef"
            type="file"
            multiple
            accept=".pdf,.png,.jpg,.jpeg,.tiff,.tif"
            class="hidden"
            @change="onFileInput"
          />
        </div>

        <!-- File list -->
        <div v-if="files.length > 0" class="mt-4">
          <p class="text-xs font-medium text-slate-600 mb-2">
            {{ files.length }} fichier{{ files.length > 1 ? 's' : '' }} sélectionné{{ files.length > 1 ? 's' : '' }}
          </p>
          <div class="flex flex-col gap-1.5 max-h-48 overflow-y-auto">
            <div
              v-for="(file, i) in files"
              :key="i"
              class="flex items-center justify-between px-3 py-2 bg-slate-50 rounded-lg text-sm"
            >
              <div class="flex items-center gap-2 min-w-0">
                <span class="fr-icon-file-line text-slate-400 shrink-0" aria-hidden="true" />
                <span class="truncate text-slate-700">{{ file.name }}</span>
                <span class="text-xs text-slate-400 shrink-0">
                  {{ formatSize(file.size) }}
                </span>
              </div>
              <button
                class="text-slate-400 hover:text-red-500 transition-colors shrink-0 ml-2"
                @click="files.splice(i, 1)"
              >
                <span class="fr-icon-close-line" style="font-size: 14px;" aria-hidden="true" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="flex justify-end gap-2 px-6 py-4 border-t border-slate-100">
        <button class="fr-btn fr-btn--tertiary fr-btn--sm" @click="$emit('close')">
          Annuler
        </button>
        <button
          class="fr-btn fr-btn--sm"
          :disabled="files.length === 0"
          @click="submit"
        >
          <span class="fr-icon-play-line fr-mr-1w" aria-hidden="true" />
          Lancer ({{ files.length }})
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { TemplatingModel } from '@/stores/templating'

defineProps<{
  template: TemplatingModel
}>()

const emit = defineEmits<{
  close: []
  submit: [files: File[]]
}>()

const files = ref<File[]>([])
const isDragging = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)

function onDrop (e: DragEvent) {
  isDragging.value = false
  if (e.dataTransfer?.files) {
    addFiles(e.dataTransfer.files)
  }
}

function onFileInput (e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files) {
    addFiles(input.files)
    input.value = ''
  }
}

function addFiles (fileList: FileList) {
  const newFiles = Array.from(fileList)
  // deduplicate by name+size
  for (const f of newFiles) {
    const exists = files.value.some(existing => existing.name === f.name && existing.size === f.size)
    if (!exists) {
      files.value.push(f)
    }
  }
}

function formatSize (bytes: number): string {
  if (bytes < 1024) return `${bytes} o`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} Ko`
  return `${(bytes / (1024 * 1024)).toFixed(1)} Mo`
}

function submit () {
  emit('submit', [...files.value])
  emit('close')
}
</script>
