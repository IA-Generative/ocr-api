<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const emit = defineEmits<{ close: [] }>()

interface Step {
  selector: string
  title: string
  description: string
  position?: 'top' | 'bottom' | 'left' | 'right'
}

const steps: Step[] = [
  {
    selector: '[data-tour="toolbar"]',
    title: 'Barre d\'outils',
    description: 'Cette barre regroupe tous les outils de navigation et d\'annotation du document.',
    position: 'bottom',
  },
  {
    selector: '[data-tour="toggle-image"]',
    title: 'Afficher / Masquer l\'image',
    description: 'Basculez entre l\'image originale et le texte OCR extrait pour comparer facilement les résultats.',
    position: 'bottom',
  },
  {
    selector: '[data-tour="drawing-mode"]',
    title: 'Annoter une zone',
    description: 'Activez ce mode pour dessiner manuellement de nouvelles zones de texte sur la page (zones manquées par l\'OCR).',
    position: 'bottom',
  },
  {
    selector: '[data-tour="metrics"]',
    title: 'Métriques OCR',
    description: 'Visualisez les statistiques de qualité de l\'extraction : taux de confiance, nombre de zones, couverture, etc.',
    position: 'bottom',
  },
  {
    selector: '[data-tour="progress-bar"]',
    title: 'Progression de la révision',
    description: 'Suivez en temps réel le nombre de zones déjà révisées par rapport au total. L\'objectif est d\'atteindre 100 %.',
    position: 'bottom',
  },
  {
    selector: '[data-tour="image-viewer"]',
    title: 'Visualiseur OCR',
    description: 'Chaque cadre coloré correspond à une zone détectée. Cliquez sur un cadre pour l\'éditer : corriger le texte, valider ou invalider la détection, marquer comme privé.',
    position: 'right',
  },
  {
    selector: '[data-tour="classification"]',
    title: 'Classification de la page',
    description: 'Ajoutez des étiquettes thématiques à cette page et indiquez votre consentement pour l\'utilisation de ces données dans le réentraînement du modèle.',
    position: 'top',
  },
  {
    selector: '[data-tour="pagination"]',
    title: 'Navigation entre pages',
    description: 'Parcourez les différentes pages du document. Vos annotations sont conservées lors du changement de page.',
    position: 'top',
  },
]

const currentStep = ref(0)
const step = computed(() => steps[currentStep.value])
const isFirst = computed(() => currentStep.value === 0)
const isLast = computed(() => currentStep.value === steps.length - 1)

// Bounding rect of the highlighted element
const spotRect = ref({ top: 0, left: 0, width: 0, height: 0 })
const PAD = 10
const TOOLTIP_W = 320

function updateSpot () {
  const el = document.querySelector(step.value.selector)
  if (!el) {
    spotRect.value = { top: 0, left: 0, width: 0, height: 0 }
    return
  }
  const r = el.getBoundingClientRect()
  // Use viewport coords — tooltip and overlay are both fixed/absolute within viewport
  spotRect.value = {
    top: r.top - PAD,
    left: r.left - PAD,
    width: r.width + PAD * 2,
    height: r.height + PAD * 2,
  }
  el.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
}

watch(currentStep, () => { setTimeout(updateSpot, 80) })

onMounted(() => {
  setTimeout(updateSpot, 80)
  window.addEventListener('resize', updateSpot)
  window.addEventListener('scroll', updateSpot)
})
onBeforeUnmount(() => {
  window.removeEventListener('resize', updateSpot)
  window.removeEventListener('scroll', updateSpot)
})

// Tooltip position
const tooltipStyle = computed(() => {
  const { top, left, width, height } = spotRect.value
  const pos = step.value.position ?? 'bottom'
  const gap = 14
  const vw = typeof window !== 'undefined' ? window.innerWidth : 1200

  function clampLeft (x: number) {
    return Math.min(Math.max(8, x), vw - TOOLTIP_W - 8)
  }

  if (pos === 'bottom') {
    return {
      top: `${top + height + gap}px`,
      left: `${clampLeft(left + width / 2 - TOOLTIP_W / 2)}px`,
      width: `${TOOLTIP_W}px`,
    }
  }
  if (pos === 'top') {
    return {
      top: `${top - gap - 160}px`,
      left: `${clampLeft(left + width / 2 - TOOLTIP_W / 2)}px`,
      width: `${TOOLTIP_W}px`,
    }
  }
  if (pos === 'right') {
    const rightSpace = vw - (left + width + gap)
    // fallback to left if not enough space on the right
    const finalLeft = rightSpace >= TOOLTIP_W + 8 ? left + width + gap : left - TOOLTIP_W - gap
    return {
      top: `${top + height / 2 - 80}px`,
      left: `${clampLeft(finalLeft)}px`,
      width: `${TOOLTIP_W}px`,
    }
  }
  // left
  return {
    top: `${top + height / 2 - 80}px`,
    left: `${left - TOOLTIP_W - gap}px`,
    width: `${TOOLTIP_W}px`,
  }
})

// SVG clip path for spotlight (viewport coords, 100vw × 100vh)
const svgClip = computed(() => {
  const { top, left, width, height } = spotRect.value
  const r = 10
  return `M 0 0 H 10000 V 10000 H 0 Z
    M ${left + r} ${top}
    Q ${left} ${top} ${left} ${top + r}
    V ${top + height - r}
    Q ${left} ${top + height} ${left + r} ${top + height}
    H ${left + width - r}
    Q ${left + width} ${top + height} ${left + width} ${top + height - r}
    V ${top + r}
    Q ${left + width} ${top} ${left + width - r} ${top}
    Z`
})

function prev () {
  if (!isFirst.value) currentStep.value--
}
function next () {
  if (!isLast.value) currentStep.value++
  else emit('close')
}
</script>

<template>
  <Teleport to="body">
    <!-- Overlay with spotlight cutout -->
    <div class="fixed inset-0 z-[9998] pointer-events-none">
      <svg
        class="fixed inset-0 w-full h-full"
        style="fill-rule: evenodd"
      >
        <path
          :d="svgClip"
          fill="rgba(0,0,0,0.55)"
        />
      </svg>
    </div>

    <!-- Backdrop click to close -->
    <div
      class="fixed inset-0 z-[9998]"
      @click="emit('close')"
    />

    <!-- Tooltip card -->
    <div
      class="fixed z-[9999] rounded-2xl bg-white shadow-2xl border border-slate-200 p-4 flex flex-col gap-3"
      :style="tooltipStyle"
      @click.stop
    >
      <!-- Header -->
      <div class="flex items-start justify-between gap-2">
        <div class="flex items-center gap-2">
          <span class="inline-flex items-center justify-center rounded-full bg-blue-600 text-white text-xs font-bold w-6 h-6 shrink-0">
            {{ currentStep + 1 }}
          </span>
          <p class="font-semibold text-slate-800 text-sm leading-snug">{{ step.title }}</p>
        </div>
        <button
          class="text-slate-400 hover:text-slate-600 transition-colors shrink-0"
          @click="emit('close')"
        >
          <span class="fr-icon-close-line" style="font-size:13px" aria-hidden="true" />
        </button>
      </div>

      <!-- Description -->
      <p class="text-xs text-slate-600 leading-relaxed">{{ step.description }}</p>

      <!-- Progress dots + nav -->
      <div class="flex items-center justify-between gap-2">
        <div class="flex gap-1">
          <div
            v-for="(_, i) in steps"
            :key="i"
            class="rounded-full transition-all duration-200"
            :class="i === currentStep ? 'w-4 h-2 bg-blue-600' : 'w-2 h-2 bg-slate-200'"
          />
        </div>
        <div class="flex gap-2">
          <button
            v-if="!isFirst"
            class="rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-50 transition-colors"
            @click="prev"
          >
            Précédent
          </button>
          <button
            class="rounded-lg px-3 py-1.5 text-xs font-bold transition-colors"
            :class="isLast ? 'bg-emerald-500 text-white hover:bg-emerald-600' : 'bg-blue-600 text-white hover:bg-blue-700'"
            @click="next"
          >
            {{ isLast ? 'Terminer' : 'Suivant' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
