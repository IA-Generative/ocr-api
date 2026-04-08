<script setup lang="ts">
import type { components } from '@/api/types/api.schema'
import type { PageLabel } from '@/interfaces/classification'
import OcrViewer from '@/components/OcrViewer.vue'

type Page = components['schemas']['Page']

// Image placeholder 800x1100 (SVG data URI — aucune dépendance externe)
const placeholderImage = `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="800" height="1100" viewBox="0 0 800 1100"><rect width="800" height="1100" fill="%23f5f5f5"/><text x="400" y="550" font-size="32" text-anchor="middle" fill="%23aaa">Page mock</text></svg>`

const mockPages: Page[] = [
  {
    page: 1,
    page_url: placeholderImage,
    boxes: [
      { x: 0.05, y: 0.04, width: 0.5, height: 0.03, confidence: 0.99, text: 'FORMULAIRE DE DEMANDE' },
      { x: 0.05, y: 0.10, width: 0.35, height: 0.025, confidence: 0.97, text: 'Nom :' },
      { x: 0.05, y: 0.15, width: 0.45, height: 0.025, confidence: 0.96, text: 'Prénom :' },
      { x: 0.05, y: 0.20, width: 0.6,  height: 0.025, confidence: 0.95, text: 'Date de naissance : 01/01/1990' },
      { x: 0.05, y: 0.28, width: 0.8,  height: 0.025, confidence: 0.93, text: 'Adresse : 12 rue de la Paix, 75001 Paris' },
      { x: 0.05, y: 0.35, width: 0.7,  height: 0.025, confidence: 0.91, text: 'Objet de la demande : Renouvellement de carte' },
      { x: 0.05, y: 0.45, width: 0.55, height: 0.025, confidence: 0.88, text: 'Signature :' },
    ],
  },
  {
    page: 2,
    page_url: placeholderImage,
    boxes: [
      { x: 0.05, y: 0.05, width: 0.6,  height: 0.03,  confidence: 0.98, text: 'PIÈCES JUSTIFICATIVES' },
      { x: 0.05, y: 0.12, width: 0.7,  height: 0.025, confidence: 0.95, text: '1. Copie de la pièce d\'identité' },
      { x: 0.05, y: 0.17, width: 0.65, height: 0.025, confidence: 0.94, text: '2. Justificatif de domicile de moins de 3 mois' },
      { x: 0.05, y: 0.22, width: 0.5,  height: 0.025, confidence: 0.92, text: '3. Photo d\'identité récente' },
    ],
  },
]

const mockData = {
  id: 'mock-ocr-result-001',
  pages: mockPages,
}

const predefinedLabels: PageLabel[] = [
  { key: 'facture', definition: 'Document de facturation commerciale', predefined: true },
  { key: 'contrat', definition: 'Document contractuel signé', predefined: true },
  { key: 'identite', definition: 'Pièce d\'identité (CNI, passeport…)', predefined: true },
  { key: 'rib', definition: 'Relevé d\'identité bancaire', predefined: true },
  { key: 'justificatif_domicile', definition: 'Justificatif de domicile de moins de 3 mois', predefined: true },
]
</script>

<template>
  <div class="p-6">
    <div class="mb-6 border border-orange-300 bg-orange-50 rounded px-4 py-2 text-orange-700 text-sm font-medium">
      Mode développement — données mockées
    </div>
    <OcrViewer :data="mockData" :predefined-labels="predefinedLabels" />
  </div>
</template>
