<script setup lang="ts">
import { computed, ref } from 'vue'
import type { PageLabel } from '@/interfaces/classification'
import { isValidSlug, toSlug } from '@/interfaces/classification'

const props = defineProps<{
  modelValue: PageLabel[]
  predefinedLabels?: PageLabel[]
  consentForTraining: boolean | null
}>()

const emit = defineEmits<{
  'update:modelValue': [labels: PageLabel[]]
  'update:consentForTraining': [value: boolean | null]
  'save': []
}>()

// --- Free-form form state ---
const freeKey = ref('')
const freeDefinition = ref('')
const showFreeForm = ref(false)

const slugPreview = computed(() => toSlug(freeKey.value))

const keyError = computed(() => {
  if (!freeKey.value) return null
  if (!isValidSlug(slugPreview.value)) return 'Le label doit commencer par une lettre ou un chiffre.'
  if (props.modelValue.some(l => l.key === slugPreview.value)) return 'Ce label est déjà ajouté.'
  return null
})

const canAddFree = computed(() =>
  freeKey.value.trim().length > 0
  && freeDefinition.value.trim().length > 0
  && isValidSlug(slugPreview.value)
  && !props.modelValue.some(l => l.key === slugPreview.value),
)

function isSelected (key: string) {
  return props.modelValue.some(l => l.key === key)
}

function togglePredefined (label: PageLabel) {
  if (isSelected(label.key)) {
    emit('update:modelValue', props.modelValue.filter(l => l.key !== label.key))
  }
  else {
    emit('update:modelValue', [...props.modelValue, label])
  }
}

function removeLabel (key: string) {
  emit('update:modelValue', props.modelValue.filter(l => l.key !== key))
}

function addFreeLabel () {
  if (!canAddFree.value) return
  emit('update:modelValue', [
    ...props.modelValue,
    { key: slugPreview.value, definition: freeDefinition.value.trim(), predefined: false },
  ])
  freeKey.value = ''
  freeDefinition.value = ''
  showFreeForm.value = false
}
</script>

<template>
  <div class="rounded-2xl border border-slate-200 bg-white shadow-sm text-sm">
    <!-- Header -->
    <div class="flex items-center gap-2 px-4 py-3 border-b border-slate-100">
      <span class="fr-icon-price-tag-3-line text-slate-400" style="font-size:14px" aria-hidden="true" />
      <span class="font-semibold text-slate-700 text-sm">Classification de la page</span>
      <span
        v-if="modelValue.length"
        class="ml-auto text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-100 text-blue-700"
      >{{ modelValue.length }}</span>
    </div>

    <!-- Experimental banner -->
    <div class="fr-alert fr-alert--warning fr-alert--sm" role="alert">
      <p>Fonctionnalité expérimentale — les résultats peuvent être inexacts et sont susceptibles d'évoluer.</p>
    </div>

    <div class="p-3 flex flex-col gap-3">

      <!-- Consentement : toggle -->
      <div class="rounded-xl border border-slate-100 bg-slate-50 px-3 py-2.5 flex items-center justify-between gap-3">
        <div class="min-w-0">
          <p class="text-xs font-semibold text-slate-700">
            {{ consentForTraining === true ? '✅ Partage autorisé' : consentForTraining === false ? '🚫 Page exclue' : '⏳ Consentement non défini' }}
          </p>
          <p class="text-xs text-slate-400 mt-0.5">
            {{ consentForTraining === true
              ? 'Utilisée pour améliorer le modèle'
              : consentForTraining === false
                ? 'Exclue du réentraînement'
                : 'Indiquez si cette page peut être partagée' }}
          </p>
        </div>
        <div
          class="relative shrink-0 cursor-pointer rounded-full transition-colors duration-200"
          style="width:40px;height:22px"
          :style="{ backgroundColor: consentForTraining === true ? '#10b981' : consentForTraining === false ? '#f43f5e' : '#cbd5e1' }"
          @click.stop="emit('update:consentForTraining', consentForTraining === true ? false : true)"
        >
          <div
            class="absolute rounded-full bg-white shadow transition-transform duration-200"
            style="width:18px;height:18px;top:2px"
            :style="{ transform: consentForTraining === true ? 'translateX(20px)' : 'translateX(2px)' }"
          />
        </div>
      </div>

      <!-- Labels actifs -->
      <div v-if="modelValue.length" class="flex flex-wrap gap-1.5">
        <div
          v-for="label in modelValue"
          :key="label.key"
          class="group flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-medium"
          :class="label.predefined ? 'bg-blue-50 border-blue-200 text-blue-700' : 'bg-violet-50 border-violet-200 text-violet-700'"
          :title="label.definition"
        >
          <span>{{ label.key }}</span>
          <button
            class="opacity-40 group-hover:opacity-100 hover:text-red-500 transition-opacity"
            aria-label="Retirer"
            @click="removeLabel(label.key)"
          >
            <span class="fr-icon-close-line" style="font-size:9px" aria-hidden="true" />
          </button>
        </div>
      </div>
      <p v-else class="text-slate-400 italic text-xs text-center py-1">Aucune classification</p>

      <!-- Labels prédéfinis -->
      <div v-if="predefinedLabels?.length" class="flex flex-wrap gap-1.5">
        <button
          v-for="label in predefinedLabels"
          :key="label.key"
          class="flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-medium transition-all"
          :class="isSelected(label.key)
            ? 'bg-blue-500 border-blue-500 text-white'
            : 'border-slate-200 text-slate-500 hover:border-blue-300 hover:bg-blue-50 hover:text-blue-600'"
          :title="label.definition"
          @click="togglePredefined(label)"
        >
          <span v-if="isSelected(label.key)" class="fr-icon-checkbox-line" style="font-size:9px" aria-hidden="true" />
          {{ label.key }}
        </button>
      </div>

      <!-- Label libre -->
      <div>
        <button
          class="flex items-center gap-1 text-xs font-medium text-slate-400 hover:text-violet-600 transition-colors"
          @click="showFreeForm = !showFreeForm"
        >
          <span :class="showFreeForm ? 'fr-icon-subtract-line' : 'fr-icon-add-line'" style="font-size:10px" aria-hidden="true" />
          Label libre
        </button>
        <Transition name="expand">
          <div v-if="showFreeForm" class="mt-2 flex flex-col gap-2">
            <input
              v-model="freeKey"
              type="text"
              placeholder="ex: facture_energie"
              class="w-full rounded-lg border px-2.5 py-1.5 text-xs outline-none transition"
              :class="freeKey && keyError ? 'border-red-300 focus:ring-red-100' : 'border-slate-200 focus:border-violet-400 focus:ring-2 focus:ring-violet-100'"
            >
            <span v-if="freeKey && !keyError" class="text-violet-500 text-xs">→ <code>{{ slugPreview }}</code></span>
            <span v-if="keyError" class="text-red-500 text-xs">{{ keyError }}</span>
            <textarea
              v-model="freeDefinition"
              rows="2"
              placeholder="Définition..."
              class="w-full resize-none rounded-lg border border-slate-200 px-2.5 py-1.5 text-xs outline-none focus:border-violet-400 focus:ring-2 focus:ring-violet-100 transition"
            />
            <button
              class="flex items-center justify-center gap-1 rounded-lg px-3 py-1.5 text-xs font-semibold transition-all"
              :class="canAddFree ? 'bg-violet-600 text-white hover:bg-violet-700' : 'bg-slate-100 text-slate-400 cursor-default'"
              :disabled="!canAddFree"
              @click="addFreeLabel"
            >
              <span class="fr-icon-add-line" style="font-size:10px" aria-hidden="true" />
              Ajouter
            </button>
          </div>
        </Transition>
      </div>

      <!-- Enregistrer -->
      <button
        class="w-full flex items-center justify-center gap-1.5 rounded-xl bg-blue-600 px-3 py-2 text-xs font-bold text-white hover:bg-blue-700 transition-colors"
        @click="emit('save')"
      >
        <span class="fr-icon-save-line" style="font-size:12px" aria-hidden="true" />
        Enregistrer
      </button>
    </div>
  </div>
</template>

<style scoped>
.expand-enter-active,
.expand-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>


