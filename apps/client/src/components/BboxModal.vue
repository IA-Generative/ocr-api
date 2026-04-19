<script setup lang="ts">
import type { components } from '@/api/types/api.schema'
import type { BboxReview } from '@/interfaces/review'
import type { DrawnBox } from '@/composables/use-box-drawing'
import BboxDetailPanel from '@/components/BboxDetailPanel.vue'

type Bbox = components['schemas']['Bbox']

defineProps<{
  box: Bbox | DrawnBox
  savedState?: BboxReview
  isHidden?: boolean
  imageUrl?: string
}>()

const emit = defineEmits<{
  close: []
  save: [review: BboxReview]
  delete: []
  toggleVisibility: []
}>()
</script>

<template>
  <Transition name="modal-fade">
    <div
      class="fixed inset-0 z-50 flex items-center justify-center"
      style="background: rgba(15, 23, 42, 0.18);"
      @click.self="emit('close')"
    >
      <!-- Panneau vitré -->
      <div
        class="relative rounded-2xl shadow-2xl"
        style="backdrop-filter: blur(12px) saturate(180%); background: rgba(255,255,255,0.72); border: 1px solid rgba(255,255,255,0.5);"
      >
        <BboxDetailPanel
          :box="box"
          :saved-state="savedState"
          :is-hidden="isHidden"
          :image-url="imageUrl"
          class="!bg-transparent !shadow-none !border-0"
          @close="emit('close')"
          @save="(review) => emit('save', review)"
          @delete="emit('delete')"
          @toggle-visibility="emit('toggleVisibility')"
        />
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.18s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
.modal-fade-enter-active > div,
.modal-fade-leave-active > div {
  transition: opacity 0.18s ease, transform 0.18s ease;
}
.modal-fade-enter-from > div,
.modal-fade-leave-to > div {
  opacity: 0;
  transform: scale(0.96) translateY(6px);
}
</style>
