<template>
  <!-- Overlay -->
  <div
    class="fixed inset-0 z-50 flex items-center justify-center p-4"
    style="background: rgba(15,23,42,0.35); backdrop-filter: blur(3px);"
    @click.self="$emit('close')"
  >
    <div
      class="w-full max-w-lg rounded-2xl bg-white shadow-2xl flex flex-col max-h-[90vh]"
      @click.stop
    >
      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-slate-100">
        <h2 class="text-base font-semibold text-slate-800">
          {{ isEdit ? 'Modifier l\'entité' : 'Ajouter une entité' }}
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
      <div class="flex-1 overflow-y-auto px-6 py-5 flex flex-col gap-5">

        <!-- Nom + Type -->
        <div class="flex gap-3">
          <div class="flex-1">
            <label for="entity-name" class="block text-xs font-medium text-slate-600 mb-1">
              Nom <span class="text-red-500">*</span>
            </label>
            <input
              id="entity-name"
              v-model="form.name"
              type="text"
              class="fr-input fr-input--sm w-full"
              :class="{ 'fr-input--error': submitted && !isValidName(form.name) }"
              placeholder="ex: date_naissance"
            />
            <p v-if="submitted && !isValidName(form.name)" class="text-xs text-red-500 mt-1">
              Uniquement minuscules, chiffres et underscore
            </p>
          </div>
          <div class="w-36 shrink-0">
            <label for="entity-type" class="block text-xs font-medium text-slate-600 mb-1">Type</label>
            <select id="entity-type" v-model="form.entity_type" class="fr-select fr-select--sm w-full">
              <option v-for="t in ENTITY_TYPES" :key="t.value" :value="t.value">
                {{ t.label }}
              </option>
            </select>
          </div>
        </div>

        <!-- Définition -->
        <div>
          <label for="entity-definition" class="block text-xs font-medium text-slate-600 mb-1">
            Définition <span class="text-red-500">*</span>
          </label>
          <textarea
            id="entity-definition"
            v-model="form.definition"
            rows="3"
            class="fr-input w-full resize-none text-sm"
            :class="{ 'fr-input--error': submitted && !form.definition.trim() }"
            :placeholder="placeholderFor(form.entity_type)"
          />
          <p v-if="submitted && !form.definition.trim()" class="text-xs text-red-500 mt-1">
            La définition est obligatoire
          </p>
        </div>

        <!-- Formats (optionnel) -->
        <div>
          <p class="text-xs font-medium text-slate-600 mb-1">Formats attendus <span class="font-normal text-slate-400">(optionnel)</span></p>
          <p class="text-xs text-slate-400 mb-2">Ex&nbsp;: <code>JJ/MM/AAAA</code>, <code>+33XXXXXXXXX</code>, <code>FR76…</code></p>
          <div class="flex flex-col gap-2">
            <div
              v-for="(fmt, i) in form.formats"
              :key="i"
              class="flex items-center gap-2"
            >
              <input
                v-model="form.formats[i]"
                type="text"
                class="fr-input fr-input--sm flex-1"
                placeholder="ex: JJ/MM/AAAA"
              />
              <button
                class="text-slate-400 hover:text-red-500 transition-colors shrink-0"
                type="button"
                @click="form.formats.splice(i, 1)"
              >
                <span class="fr-icon-delete-line" style="font-size: 14px;" aria-hidden="true" />
              </button>
            </div>
            <button
              class="fr-btn fr-btn--tertiary fr-btn--sm fr-icon-add-line self-start"
              type="button"
              @click="form.formats.push('')"
            >
              Ajouter un format
            </button>
          </div>
        </div>

        <!-- Exemples (optionnel) -->
        <div>
          <p class="text-xs font-medium text-slate-600 mb-1">Exemples de valeurs <span class="font-normal text-slate-400">(optionnel)</span></p>
          <p class="text-xs text-slate-400 mb-2">Quelques valeurs représentatives pour guider le modèle.</p>
          <div class="flex flex-col gap-2">
            <div
              v-for="(ex, i) in form.exemples"
              :key="i"
              class="flex items-center gap-2"
            >
              <input
                v-model="form.exemples[i]"
                type="text"
                class="fr-input fr-input--sm flex-1"
                placeholder="ex: 01/01/1990"
              />
              <button
                class="text-slate-400 hover:text-red-500 transition-colors shrink-0"
                type="button"
                @click="form.exemples.splice(i, 1)"
              >
                <span class="fr-icon-delete-line" style="font-size: 14px;" aria-hidden="true" />
              </button>
            </div>
            <button
              class="fr-btn fr-btn--tertiary fr-btn--sm fr-icon-add-line self-start"
              type="button"
              @click="form.exemples.push('')"
            >
              Ajouter un exemple
            </button>
          </div>
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

type EntityType = 'string' | 'int' | 'float' | 'date' | 'boolean' | 'email' | 'phone' | 'address' | 'currency' | 'iban'

export type EntityDefinition = {
  name: string
  definition: string
  entity_type: EntityType
  formats: string[]
  exemples: string[]
}

const props = defineProps<{
  initial?: EntityDefinition
}>()

const emit = defineEmits<{
  close: []
  save: [entity: EntityDefinition]
}>()

const isEdit = !!props.initial
const submitted = ref(false)

const form = reactive<EntityDefinition>({
  name: props.initial?.name ?? '',
  definition: props.initial?.definition ?? '',
  entity_type: props.initial?.entity_type ?? 'string',
  formats: props.initial?.formats ? [...props.initial.formats] : [],
  exemples: props.initial?.exemples ? [...props.initial.exemples] : [],
})

const ENTITY_TYPES: { value: EntityType; label: string; placeholder: string }[] = [
  { value: 'string',   label: 'Texte',      placeholder: 'Ex : Nom complet de la personne' },
  { value: 'int',      label: 'Entier',     placeholder: 'Ex : Âge de la personne en années' },
  { value: 'float',    label: 'Décimal',    placeholder: 'Ex : Taux de TVA appliqué (ex : 20.0)' },
  { value: 'date',     label: 'Date',       placeholder: 'Ex : Date de naissance au format JJ/MM/AAAA' },
  { value: 'boolean',  label: 'Oui / Non',  placeholder: 'Ex : Le document comporte-t-il une signature ?' },
  { value: 'email',    label: 'Email',      placeholder: 'Ex : Adresse email de contact du signataire' },
  { value: 'phone',    label: 'Téléphone',  placeholder: 'Ex : Numéro de téléphone portable ou fixe' },
  { value: 'address',  label: 'Adresse',    placeholder: 'Ex : Adresse postale complète du domicile' },
  { value: 'currency', label: 'Montant',    placeholder: 'Ex : Montant total TTC en euros' },
  { value: 'iban',     label: 'IBAN',       placeholder: 'Ex : IBAN du bénéficiaire du virement' },
]

function placeholderFor (type: EntityType) {
  return ENTITY_TYPES.find(t => t.value === type)?.placeholder ?? ''
}

function isValidName (name: string) {
  return /^[a-z0-9_]+$/.test(name)
}

function submit () {
  submitted.value = true
  if (!isValidName(form.name) || !form.definition.trim()) return
  emit('save', {
    ...form,
    formats: form.formats.filter(f => f.trim()),
    exemples: form.exemples.filter(e => e.trim()),
  })
}
</script>
