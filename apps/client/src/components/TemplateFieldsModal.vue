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
          <h2 class="text-base font-semibold text-slate-800">Configurer les champs</h2>
          <p class="text-xs text-slate-400 mt-0.5">{{ template.name }}</p>
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

        <!-- Invalid fields warning -->
        <div v-if="invalidFields.length > 0" class="mb-4 p-3 rounded-lg bg-orange-50 border border-orange-200">
          <div class="flex items-start gap-2">
            <span class="fr-icon-warning-line text-orange-500 shrink-0 mt-0.5" aria-hidden="true" />
            <div>
              <p class="text-sm font-medium text-orange-800">Champs mal détectés</p>
              <p class="text-xs text-orange-600 mt-1">
                Les placeholders suivants n'ont pas un format valide et n'ont pas été importés :
              </p>
              <div class="flex flex-wrap gap-1 mt-2">
                <span
                  v-for="name in invalidFields"
                  :key="name"
                  class="inline-flex items-center px-2 py-0.5 rounded text-xs font-mono bg-orange-100 text-orange-700"
                >
                  {{ name }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <p class="text-sm text-slate-500 mb-4">
          Les champs suivants ont été détectés dans le template.
          Cliquez sur un champ pour modifier son type, sa description, ses formats et exemples.
        </p>

        <!-- Entity list -->
        <div v-if="entities.length === 0" class="text-sm text-slate-400 italic py-4 text-center">
          Aucun champ détecté dans ce template.
        </div>

        <div class="flex flex-col gap-2">
          <div
            v-for="entity in entities"
            :key="entity.name"
            class="flex items-center justify-between p-3 rounded-lg border transition-colors"
            :class="entity.definition ? 'border-green-200 bg-green-50' : 'border-slate-200 bg-slate-50'"
          >
            <div class="flex items-center gap-3 min-w-0">
              <span
                class="shrink-0 w-2 h-2 rounded-full"
                :class="entity.definition ? 'bg-green-500' : 'bg-slate-300'"
              />
              <div class="min-w-0">
                <p class="text-sm font-medium text-slate-800 font-mono">{{ entity.name }}</p>
                <p v-if="entity.definition" class="text-xs text-slate-500 truncate">
                  <span class="fr-badge fr-badge--sm fr-badge--green-emeraude mr-1">{{ entity.entity_type }}</span>
                  {{ entity.definition }}
                </p>
                <p v-else class="text-xs text-slate-400 italic">Non défini</p>
              </div>
            </div>
            <button
              class="fr-btn fr-btn--tertiary fr-btn--sm shrink-0 ml-3"
              @click="openEntityModal(entity)"
            >
              {{ entity.definition ? 'Modifier' : 'Définir' }}
            </button>
          </div>
        </div>

        <!-- Progress -->
        <div v-if="entities.length > 0" class="mt-4 flex items-center gap-2 text-xs text-slate-500">
          <span>{{ definedCount }}/{{ entities.length }} champs définis</span>
          <div class="flex-1 h-1.5 bg-slate-200 rounded-full overflow-hidden">
            <div
              class="h-full bg-blue-france transition-all duration-300"
              :style="{ width: `${(definedCount / entities.length) * 100}%` }"
            />
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="flex justify-end gap-2 px-6 py-4 border-t border-slate-100">
        <button class="fr-btn fr-btn--tertiary fr-btn--sm" @click="$emit('close')">
          Annuler
        </button>
        <button class="fr-btn fr-btn--sm" :disabled="isSaving" @click="save">
          <span v-if="isSaving" class="fr-icon-loader-line fr-mr-1w" aria-hidden="true" />
          Enregistrer
        </button>
      </div>
    </div>
  </div>

  <!-- EntityDefinitionModal -->
  <EntityDefinitionModal
    v-if="editingEntity"
    :initial="editingEntity.definition ? editingEntity : undefined"
    :forced-name="editingEntity.name"
    @close="editingEntity = null"
    @save="onEntitySaved"
  />
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import EntityDefinitionModal, { type EntityDefinition } from './EntityDefinitionModal.vue'
import { useTemplatingStore, type TemplatingModel, type EntityZoneData } from '@/stores/templating'

type EntityField = EntityDefinition & { defined: boolean }

const props = defineProps<{
  template: TemplatingModel
}>()

const emit = defineEmits<{
  close: []
  save: [fields: EntityDefinition[]]
}>()

const store = useTemplatingStore()
const isSaving = ref(false)

// Build entity list from template.entity_zone
const entities = reactive<EntityField[]>(
  (props.template.entity_zone ?? []).map((ez: EntityZoneData) => {
    const ed = ez.entity_definition
    return {
      name: ed.name,
      definition: ed.definition ?? '',
      entity_type: ed.entity_type ?? 'text',
      formats: ed.formats ? [...ed.formats] : [],
      exemples: ed.exemples ? [...ed.exemples] : [],
      defined: !!ed.definition,
    }
  })
)

// Invalid fields from entity_names
const invalidFields = computed(() => props.template.entity_names?.invalid_fields ?? [])

const editingEntity = ref<EntityField | null>(null)
const definedCount = computed(() => entities.filter((e: EntityField) => e.defined).length)

function openEntityModal (entity: EntityField) {
  editingEntity.value = entity
}

function onEntitySaved (saved: EntityDefinition) {
  const target = entities.find((e: EntityField) => e.name === editingEntity.value?.name)
  if (target) {
    Object.assign(target, saved)
    target.defined = true
  }
  editingEntity.value = null
}

async function save () {
  isSaving.value = true
  try {
    const entityZone = entities.map((e: EntityField) => ({
      entity_definition: {
        name: e.name,
        definition: e.definition || null,
        entity_type: e.entity_type,
        formats: e.formats,
        exemples: e.exemples,
      },
      boxes: null,
    }))
    await store.updateTemplating(props.template.id, { entity_zone: entityZone })
    emit('save', entities.filter((e: EntityField) => e.definition))
    emit('close')
  }
  finally {
    isSaving.value = false
  }
}
</script>
