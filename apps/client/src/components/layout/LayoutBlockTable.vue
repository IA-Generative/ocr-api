<script setup lang="ts">
import { computed, ref } from 'vue'
import type { TableBlock, TableHeader, TableCell } from './types'

const props = defineProps<{
  block: TableBlock
}>()

// ---- View toggle ----
const view = ref<'table' | 'json'>('table')
const copied = ref(false)

const tableJson = computed(() => JSON.stringify(props.block.content, null, 2))

async function copyJson() {
  await navigator.clipboard.writeText(tableJson.value)
  copied.value = true
  setTimeout(() => (copied.value = false), 1800)
}

// ---- Header flattening for <thead> ----
interface HeaderCell {
  name: string
  colspan: number
  rowspan: number
}

function countLeaves(header: TableHeader): number {
  if (!header.children?.length) return 1
  return header.children.reduce((sum, c) => sum + countLeaves(c), 0)
}

function getDepth(headers: TableHeader[]): number {
  return 1 + Math.max(0, ...headers.map(h =>
    h.children?.length ? getDepth(h.children) : 0,
  ))
}

function buildHeaderRows(headers: TableHeader[]): HeaderCell[][] {
  const depth = getDepth(headers)
  const rows: HeaderCell[][] = Array.from({ length: depth }, () => [])

  function fill(node: TableHeader, level: number) {
    const leaves = countLeaves(node)
    const hasChildren = !!node.children?.length
    rows[level].push({
      name: node.name,
      colspan: leaves,
      rowspan: hasChildren ? 1 : depth - level,
    })
    if (node.children?.length) {
      for (const child of node.children) fill(child, level + 1)
    }
  }

  for (const h of headers) fill(h, 0)
  return rows
}

const headerRows = computed<HeaderCell[][]>(() => {
  const headers = props.block.content.headers
  if (!headers?.length) return []
  return buildHeaderRows(headers)
})

const rows = computed(() => props.block.content.rows)

function cellStringValue(cell: TableCell): string {
  if (typeof cell.value === 'string') return cell.value
  return JSON.stringify(cell.value, null, 2)
}
</script>

<template>
  <div class="flex flex-col gap-2">
    <!-- Toolbar -->
    <div class="flex items-center justify-between">
      <div class="flex rounded-lg border border-slate-200 overflow-hidden text-xs">
        <button
          class="px-3 py-1 transition-colors"
          :class="view === 'table' ? 'bg-emerald-500 text-white font-semibold' : 'text-slate-500 hover:bg-slate-50'"
          @click="view = 'table'"
        >Tableau</button>
        <button
          class="px-3 py-1 transition-colors border-l border-slate-200"
          :class="view === 'json' ? 'bg-emerald-500 text-white font-semibold' : 'text-slate-500 hover:bg-slate-50'"
          @click="view = 'json'"
        >JSON</button>
      </div>
      <button
        class="flex items-center gap-1 text-xs px-2 py-0.5 rounded-lg border transition-colors"
        :class="copied
          ? 'border-emerald-300 text-emerald-600 bg-emerald-50'
          : 'border-slate-200 text-slate-500 hover:text-slate-700 hover:bg-slate-50'"
        @click="copyJson"
      >
        <span
          :class="copied ? 'fr-icon-checkbox-circle-line' : 'fr-icon-file-copy-line'"
          style="font-size:13px"
          aria-hidden="true"
        />
        {{ copied ? 'Copié !' : 'Copier JSON' }}
      </button>
    </div>

    <!-- Table view -->
    <div v-if="view === 'table'" class="overflow-auto max-h-72 rounded-xl border border-emerald-100">
      <table class="min-w-full text-xs border-collapse">
        <thead v-if="headerRows.length" class="bg-emerald-50 sticky top-0">
          <tr v-for="(row, ri) in headerRows" :key="ri">
            <th
              v-for="(cell, ci) in row"
              :key="ci"
              :colspan="cell.colspan"
              :rowspan="cell.rowspan"
              class="px-3 py-2 text-left font-semibold text-emerald-800 border border-emerald-200 whitespace-nowrap"
            >{{ cell.name }}</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(row, ri) in rows"
            :key="ri"
            class="even:bg-slate-50 hover:bg-emerald-50/50 transition-colors"
          >
            <td
              v-for="(cell, ci) in row.cells"
              :key="ci"
              :rowspan="cell.rowspan > 1 ? cell.rowspan : undefined"
              :colspan="cell.colspan > 1 ? cell.colspan : undefined"
              class="px-3 py-2 text-slate-700 border border-slate-100 align-top"
            >{{ cellStringValue(cell) }}</td>
          </tr>
        </tbody>
      </table>
      <p v-if="!rows.length" class="text-xs text-slate-400 italic text-center py-4">Aucune ligne dans ce tableau.</p>
    </div>

    <!-- JSON view -->
    <pre
      v-else
      class="rounded-xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-xs text-emerald-900 font-mono leading-relaxed max-h-72 overflow-auto"
    >{{ tableJson }}</pre>
  </div>
</template>
