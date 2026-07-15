<script setup lang="ts">
import { computed, ref } from 'vue'

interface TabData {
  label: string
  slot?: string
}

const props = defineProps<{
  tabsData: TabData[]
  modelValue?: number
}>()

const emit = defineEmits<{
  'update:modelValue': [index: number]
}>()

const tabListId = 'dynamic-tabs'
const internalActiveTab = ref(0)
const activeTab = computed(() => props.modelValue ?? internalActiveTab.value)

const tabs = computed(() =>
  props.tabsData.map((tab, index) => ({
    id: `tab-${index}`,
    panelId: `panel-${index}`,
    label: tab.label,
    slot: tab.slot || `tab-${index}-content`,
  })),
)

function activateTab (index: number) {
  internalActiveTab.value = index
  emit('update:modelValue', index)
}
</script>

<template>
  <div class="tabs">
    <div
      role="tablist"
      class="tabs__list"
      :aria-labelledby="tabListId"
    >
      <button
        v-for="(tab, index) in tabs"
        :id="tab.id"
        :key="tab.id"
        role="tab"
        :aria-controls="tab.panelId"
        :aria-selected="activeTab === index"
        :tabindex="activeTab === index ? 0 : -1"
        class="fr-tabs__tab"
        @click="activateTab(index)"
        @keydown.enter="activateTab(index)"
        @keydown.space.prevent="activateTab(index)"
        @keydown.arrow-right.prevent="activateTab((index + 1) % tabs.length)"
        @keydown.arrow-left.prevent="activateTab((index - 1 + tabs.length) % tabs.length)"
      >
        {{ tab.label }}
      </button>
    </div>

    <div
      v-for="(tab, index) in tabs"
      v-show="activeTab === index"
      :id="tab.panelId"
      :key="tab.panelId"
      role="tabpanel"
      :aria-labelledby="tab.id"
      class="tabs__panel"
    >
      <slot
        :name="tab.slot"
        :is-active="activeTab === index"
      />
    </div>
  </div>
</template>

<style scoped>
.tabs {
  display: flex;
  flex-direction: column;
}
.tabs__list {
  display: flex;
  padding-left: 1rem;
  overflow: auto;
}
.tabs__panel {
  display: block;
  padding: 1.5rem;
  border: 1px solid var(--border-default-grey);
}
</style>
