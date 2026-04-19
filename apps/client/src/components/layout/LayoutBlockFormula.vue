<script setup lang="ts">
import { ref, computed } from 'vue'
import katex from 'katex'
import 'katex/dist/katex.min.css'
import type { FormulaBlock } from './types'

const props = defineProps<{
  block: FormulaBlock
}>()

const copied = ref(false)

async function copyLatex(latex: string) {
  await navigator.clipboard.writeText(latex)
  copied.value = true
  setTimeout(() => (copied.value = false), 1800)
}

// Strip surrounding delimiters and fix common LLM artifacts
function cleanLatex(raw: string): string {
  let s = raw.trim()
  // Remove ```latex ... ``` wrapping
  s = s.replace(/^```(?:latex)?\s*([\s\S]*?)\s*```$/, '$1').trim()
  // Remove $$ ... $$ wrapping
  s = s.replace(/^\$\$([\s\S]*)\$\$$/, '$1').trim()
  // Remove $ ... $ wrapping
  s = s.replace(/^\$([\s\S]*)\$$/, '$1').trim()
  // Remove \[ ... \] wrapping
  s = s.replace(/^\\\[([\s\S]*)\\\]$/, '$1').trim()
  // Remove \( ... \) wrapping (inline math delimiters)
  s = s.replace(/^\\\(([\s\S]*)\\\)$/, '$1').trim()
  // Replace stray \( and \) inside expression with \left( and \right)
  s = s.replace(/\\\(/g, '\\left(')
  s = s.replace(/\\\)/g, '\\right)')
  return s
}

const cleanedLatex = computed(() => cleanLatex(props.block.latex))

const rendered = computed(() => {
  if (!cleanedLatex.value) return null
  try {
    return katex.renderToString(cleanedLatex.value, {
      displayMode: true,
      throwOnError: false,
      output: 'html',
      trust: false,
      strict: false,
    })
  }
  catch {
    return null
  }
})

const renderError = computed(() => {
  if (!cleanedLatex.value) return 'LaTeX vide'
  try {
    katex.renderToString(cleanedLatex.value, {
      displayMode: true,
      throwOnError: true,
    })
    return null
  }
  catch (e: any) {
    return e?.message ?? 'Erreur inconnue'
  }
})
</script>

<template>
  <div class="flex flex-col gap-3">
    <!-- Rendu visuel KaTeX -->
    <div class="flex flex-col gap-1.5">
      <p class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Rendu</p>
      <div
        v-if="rendered"
        class="rounded-xl border border-red-100 bg-white px-4 py-4 overflow-x-auto text-center"
        v-html="rendered"
      />
      <div v-else class="rounded-xl border border-amber-100 bg-amber-50 px-3 py-2 text-xs text-amber-700">
        <p class="font-medium">Impossible de rendre la formule.</p>
        <p v-if="renderError" class="mt-1 text-amber-500 font-mono text-[11px]">{{ renderError }}</p>
      </div>
    </div>

    <!-- LaTeX brut + bouton copier -->
    <div class="flex flex-col gap-1.5">
      <div class="flex items-center justify-between">
        <p class="text-xs font-semibold text-slate-500 uppercase tracking-wide">LaTeX</p>
        <button
          class="flex items-center gap-1 text-xs px-2 py-0.5 rounded-lg border transition-colors"
          :class="copied
            ? 'border-emerald-300 text-emerald-600 bg-emerald-50'
            : 'border-slate-200 text-slate-500 hover:text-slate-700 hover:bg-slate-50'"
          @click="copyLatex(block.latex)"
        >
          <span
            :class="copied ? 'fr-icon-checkbox-circle-line' : 'fr-icon-file-copy-line'"
            style="font-size:13px"
            aria-hidden="true"
          />
          {{ copied ? 'Copié !' : 'Copier' }}
        </button>
      </div>
      <pre class="rounded-xl border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-800 font-mono leading-relaxed whitespace-pre-wrap break-all overflow-x-auto">{{ block.latex }}</pre>
      <p v-if="block.confidence != null" class="text-xs text-slate-400 text-right">
        Confiance extraction : {{ Math.round(block.confidence * 100) }}%
      </p>
    </div>
  </div>
</template>
