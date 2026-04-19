<script setup lang="ts">
import { computed, ref } from 'vue'
import type { ImageBlock } from './types'

const props = defineProps<{
  block: ImageBlock
}>()

const description = computed(() => (props.block.content as any)?.description as string | null)

interface Tab {
  key: string
  label: string
  visible: boolean
}

const tabs = computed<Tab[]>(() => [
  { key: 'description', label: 'Description', visible: true },
  { key: 'layout', label: 'Mise en page', visible: !!props.block.content.layout },
  { key: 'objects', label: `Objets (${props.block.content.objects?.length ?? 0})`, visible: !!props.block.content.objects?.length },
  { key: 'text', label: `Texte (${props.block.content.text?.length ?? 0})`, visible: !!props.block.content.text?.length },
  { key: 'relationships', label: `Relations (${props.block.content.relationships?.length ?? 0})`, visible: !!props.block.content.relationships?.length },
].filter(t => t.visible))

const activeTab = ref('description')

// Ensure activeTab is valid
const currentTab = computed(() => {
  if (tabs.value.find(t => t.key === activeTab.value)) return activeTab.value
  return tabs.value[0]?.key ?? ''
})
</script>

<template>
  <div class="flex flex-col gap-2">
    <!-- Tabs -->
    <div v-if="tabs.length" class="flex rounded-lg border border-slate-200 overflow-hidden text-xs">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="px-3 py-1.5 transition-colors border-r border-slate-200 last:border-r-0"
        :class="currentTab === tab.key
          ? 'bg-orange-500 text-white font-semibold'
          : 'text-slate-500 hover:bg-slate-50'"
        @click="activeTab = tab.key"
      >{{ tab.label }}</button>
    </div>

    <!-- Description -->
    <div v-if="currentTab === 'description'" class="flex flex-col gap-1.5">
      <p v-if="description" class="text-sm text-slate-700 leading-relaxed bg-orange-50 border border-orange-100 rounded-xl px-4 py-3">
        {{ description }}
      </p>
      <p v-else class="text-xs text-slate-400 italic">Aucune description disponible.</p>
    </div>

    <!-- Mise en page -->
    <div v-if="currentTab === 'layout'" class="flex flex-col gap-1.5">
      <p class="text-sm text-slate-700 leading-relaxed bg-slate-50 border border-slate-100 rounded-xl px-4 py-3">
        {{ block.content.layout }}
      </p>
    </div>

    <!-- Objets détectés -->
    <div v-if="currentTab === 'objects'" class="overflow-auto max-h-52 rounded-xl border border-orange-100">
      <table class="min-w-full text-xs border-collapse">
        <thead class="bg-orange-50 sticky top-0">
          <tr>
            <th class="px-3 py-2 text-left font-semibold text-orange-800 border-b border-orange-200 w-12">#</th>
            <th class="px-3 py-2 text-left font-semibold text-orange-800 border-b border-orange-200">Objet</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(obj, idx) in block.content.objects"
            :key="idx"
            class="even:bg-slate-50 hover:bg-orange-50/50 transition-colors"
          >
            <td class="px-3 py-1.5 text-slate-400 border-b border-slate-100 font-mono">{{ idx + 1 }}</td>
            <td class="px-3 py-1.5 text-slate-700 border-b border-slate-100">{{ obj }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Texte visible -->
    <div v-if="currentTab === 'text'" class="overflow-auto max-h-52 rounded-xl border border-slate-100">
      <table class="min-w-full text-xs border-collapse">
        <thead class="bg-slate-50 sticky top-0">
          <tr>
            <th class="px-3 py-2 text-left font-semibold text-slate-600 border-b border-slate-200 w-12">#</th>
            <th class="px-3 py-2 text-left font-semibold text-slate-600 border-b border-slate-200">Texte</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(t, idx) in block.content.text"
            :key="idx"
            class="even:bg-slate-50 hover:bg-blue-50/50 transition-colors"
          >
            <td class="px-3 py-1.5 text-slate-400 border-b border-slate-100 font-mono">{{ idx + 1 }}</td>
            <td class="px-3 py-1.5 text-slate-700 border-b border-slate-100">{{ t }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Relations -->
    <div v-if="currentTab === 'relationships'" class="overflow-auto max-h-52 rounded-xl border border-slate-100">
      <table class="min-w-full text-xs border-collapse">
        <thead class="bg-slate-50 sticky top-0">
          <tr>
            <th class="px-3 py-2 text-left font-semibold text-slate-600 border-b border-slate-200 w-12">#</th>
            <th class="px-3 py-2 text-left font-semibold text-slate-600 border-b border-slate-200">Relation</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(rel, idx) in block.content.relationships"
            :key="idx"
            class="even:bg-slate-50 hover:bg-orange-50/50 transition-colors"
          >
            <td class="px-3 py-1.5 text-slate-400 border-b border-slate-100 font-mono">{{ idx + 1 }}</td>
            <td class="px-3 py-1.5 text-slate-700 border-b border-slate-100">{{ rel }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Fallback -->
    <p
      v-if="!tabs.length"
      class="text-xs text-slate-400 italic"
    >
      Aucun contenu extrait pour cette figure.
    </p>
  </div>
</template>
