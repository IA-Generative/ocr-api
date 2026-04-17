<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center p-4"
    style="background: rgba(15,23,42,0.35); backdrop-filter: blur(3px);"
    @click.self="$emit('close')"
  >
    <div
      class="w-full max-w-md rounded-2xl bg-white shadow-2xl flex flex-col"
      @click.stop
    >
      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-slate-100">
        <h2 class="text-base font-semibold text-slate-800">
          {{ isEdit ? 'Modifier le type' : 'Ajouter un type de document' }}
        </h2>
        <button
          class="text-slate-400 hover:text-slate-600 transition-colors"
          aria-label="Fermer"
          @click="$emit('close')"
        >
          <span class="fr-icon-close-line" aria-hidden="true" />
        </button>
      </div>

      <!-- Body -->
      <div class="px-6 py-5 flex flex-col gap-5">

        <!-- Nom -->
        <div>
          <label for="doctype-name" class="block text-xs font-medium text-slate-600 mb-1">
            Nom <span class="text-red-500">*</span>
          </label>
          <input
            id="doctype-name"
            v-model="form.name"
            type="text"
            class="fr-input fr-input--sm w-full"
            :class="{ 'fr-input--error': submitted && !isValidName(form.name) }"
            placeholder="ex: cni, facture, passeport"
          />
          <p v-if="submitted && !form.name.trim()" class="text-xs text-red-500 mt-1">
            Le nom est obligatoire
          </p>
          <p v-else-if="submitted && !isValidName(form.name)" class="text-xs text-red-500 mt-1">
            Uniquement minuscules, chiffres et underscore
          </p>
        </div>

        <!-- Description -->
        <div>
          <label for="doctype-description" class="block text-xs font-medium text-slate-600 mb-1">
            Description <span class="text-red-500">*</span>
          </label>
          <textarea
            id="doctype-description"
            v-model="form.description"
            rows="4"
            class="fr-input w-full resize-none text-sm"
            :class="{ 'fr-input--error': submitted && !form.description.trim() }"
            placeholder="Ex : Carte nationale d'identité française recto ou verso, avec photo et numéro de document"
          />
          <p v-if="submitted && !form.description.trim()" class="text-xs text-red-500 mt-1">
            La description est obligatoire
          </p>
        </div>

      </div>

      <!-- Footer -->
      <div class="flex justify-end gap-2 px-6 py-4 border-t border-slate-100">
        <DsfrButton
          label="Annuler"
          priority="tertiary"
          size="sm"
          @click="$emit('close')"
        />
        <DsfrButton
          :label="isEdit ? 'Enregistrer' : 'Ajouter'"
          size="sm"
          @click="submit"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'

export type DocumentType = {
  name: string
  description: string
}

const props = defineProps<{
  initial?: DocumentType
}>()

const emit = defineEmits<{
  close: []
  save: [docType: DocumentType]
}>()

const isEdit = !!props.initial
const submitted = ref(false)

const form = reactive<DocumentType>({
  name: props.initial?.name ?? '',
  description: props.initial?.description ?? '',
})

function isValidName (name: string) {
  return /^[a-z0-9_]+$/.test(name)
}

function submit () {
  submitted.value = true
  if (!isValidName(form.name) || !form.description.trim()) return
  emit('save', { ...form })
}
</script>
