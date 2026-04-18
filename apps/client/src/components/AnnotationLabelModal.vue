<template>
  <Teleport to="body">
    <div
      class="fixed inset-0 z-50 flex items-center justify-center"
      @click.self="emit('close')"
    >
      <div class="w-80 rounded-2xl bg-white shadow-2xl flex flex-col overflow-hidden border border-slate-100">

        <!-- Header -->
        <div
          class="flex items-center justify-between px-4 py-3 border-b"
          :class="label.predefined ? 'bg-blue-50 border-blue-100' : 'bg-violet-50 border-violet-100'"
        >
          <div class="flex items-center gap-2">
            <span
              class="fr-icon-price-tag-3-line"
              style="font-size:14px"
              :class="label.predefined ? 'text-blue-500' : 'text-violet-500'"
              aria-hidden="true"
            />
            <span
              class="text-[11px] font-bold tracking-wide uppercase"
              :class="label.predefined ? 'text-blue-700' : 'text-violet-700'"
            >Annotation manuelle</span>
          </div>
          <button
            class="w-7 h-7 flex items-center justify-center rounded-lg text-slate-400 hover:bg-black/5 transition-colors"
            aria-label="Fermer"
            @click="emit('close')"
          >
            <span class="fr-icon-close-line" style="font-size:12px" aria-hidden="true" />
          </button>
        </div>

        <div class="p-4 flex flex-col gap-3">

          <!-- Label -->
          <div class="flex flex-col gap-1.5">
            <label for="annotation-label-key" class="text-xs text-slate-400">Label</label>
            <input
              id="annotation-label-key"
              v-model="editKey"
              type="text"
              class="w-full rounded-xl border border-slate-200 px-3 py-2 text-xs outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100 transition"
              placeholder="ex: facture_energie"
            />
          </div>

          <!-- Définition -->
          <div class="flex flex-col gap-1.5">
            <label for="annotation-label-definition" class="text-xs text-slate-400">Définition</label>
            <textarea
              id="annotation-label-definition"
              v-model="editDefinition"
              rows="3"
              class="w-full resize-none rounded-xl border border-slate-200 px-3 py-2 text-xs leading-relaxed outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100 transition"
              placeholder="Description du type de document…"
            />
          </div>

          <!-- Actions -->
          <div class="flex items-center gap-2 pt-1">
            <button
              class="flex-1 flex items-center justify-center gap-1.5 rounded-xl px-3 py-2 text-[11px] font-bold transition-colors"
              :class="canSave ? 'bg-blue-600 text-white hover:bg-blue-700' : 'bg-slate-100 text-slate-300 cursor-default'"
              :disabled="!canSave"
              @click="onSave"
            >
              <span class="fr-icon-save-line" style="font-size:11px" aria-hidden="true" />
              Enregistrer
            </button>
            <button
              class="w-9 flex items-center justify-center rounded-xl border border-red-100 text-red-300 hover:bg-red-50 hover:border-red-300 hover:text-red-500 py-2 transition-all"
              title="Supprimer"
              @click="emit('delete', label.key)"
            >
              <span class="fr-icon-delete-line" style="font-size:12px" aria-hidden="true" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { PageLabel } from '@/interfaces/classification'
import { toSlug, isValidSlug } from '@/interfaces/classification'

const props = defineProps<{
  label: PageLabel
}>()

const emit = defineEmits<{
  close: []
  save: [oldKey: string, updated: PageLabel]
  delete: [key: string]
}>()

const editKey = ref(props.label.key)
const editDefinition = ref(props.label.definition)

const slugPreview = computed(() => toSlug(editKey.value))

const canSave = computed(() =>
  editKey.value.trim().length > 0
  && editDefinition.value.trim().length > 0
  && isValidSlug(slugPreview.value),
)

function onSave () {
  if (!canSave.value) return
  emit('save', props.label.key, {
    key: slugPreview.value,
    definition: editDefinition.value.trim(),
    predefined: props.label.predefined,
  })
}
</script>
