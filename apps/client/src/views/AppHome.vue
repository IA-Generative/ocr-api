<script setup lang="ts">
import DocumentDownload from '@gouvfr/dsfr/dist/artwork/pictograms/document/document-download.svg'
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Media from '@/assets/ocr-card.svg'
import ComminitySVG from '@/assets/pictograms/community.svg'
import PenSVG from '@/assets/pictograms/pen.svg'
import CustomCard from '@/components/CustomCard.vue'
import InfoBulle from '@/components/InfoBulle.vue'
import ProgressBar from '@/components/ProgressBar.vue'
import SideBar from '@/components/SideBar.vue'
import TasksTab from '@/components/TasksTab.vue'
import { useOcrStore } from '@/stores/ocr'

const store = useOcrStore()
const router = useRouter()
const route = useRoute()
const currentTab = ref<'ocr' | 'tasks'>(route.name === 'Tasks' ? 'tasks' : 'ocr')
const selectedFile = ref<File | null>(null)
const pdfUrl = ref<string | null>(null)
const uploadError = computed(() => store.error)
const progressPercent = computed(() => Math.round(store.percentage * 100))
const isPolling = computed(() => store.isPolling)
const taskData = computed(() => store.taskData)
const status = computed(() => store.status)
const isLoading = ref(false)

function selectFile (files: FileList | File[]) {
  const file = Array.isArray(files) ? files[0] : files[0] || null
  if (file) {
    pdfUrl.value = URL.createObjectURL(file)
    selectedFile.value = file
    store.reset()
  }
}

async function startOcr () {
  if (!selectedFile.value) {
    return
  }

  isLoading.value = true

  try {
    const form = new FormData()
    form.append('file', selectedFile.value)
    await store.sendFileAndPoll(form)
  }
  finally {
    isLoading.value = false
  }
}

watch(() => store.taskData, (task) => {
  if (task?.id && store.status === 'completed') {
    router.push(`/${task.id}`)
  }
})

const myOtherTools = ref([
  {
    title: 'Converser avec le Chatbot',
    to: '/outils-mirai/chat',
    imgSrc: ComminitySVG,
  },
  {
    title: 'Résumer un texte',
    to: '/outils-mirai/resume',
    imgSrc: PenSVG,
  },
  {
    title: 'Faire un compte rendu',
    to: '/outils-mirai/compte-rendu',
    imgSrc: DocumentDownload,
  },
])

const uploadHint = 'Taille maximale : 200 Mo. Formats supportés : jpg, png, pdf. Plus la qualité du fichier sera élevée, plus l’outil de reconnaissance de texte sera performant.'
const uploadLabel = 'Ajouter un fichier'
const uploadAccept = 'image/jpeg,image/png,application/pdf'

onBeforeUnmount(() => {
  if (pdfUrl.value) {
    URL.revokeObjectURL(pdfUrl.value)
  }
})
</script>

<template>
  <div class="main-page">
    <SideBar :other-tools="myOtherTools" />
    <div class="main-page__container">
      <div class="mt-[35px]">
        <h1 class="flex items-center gap-3">
          <!--
          <img
            class="hidden md:block"
            src="@/assets/pictograms/document-search.svg"
            alt="Document Search Pictogram"
          >
          -->

          <span>Reconnaître un texte scanné </span>
        </h1>
      </div>

      <div class="tabs flex gap-2 mt-4">
        <DsfrButton
          label="OCR"
          :priority="currentTab === 'ocr' ? 'primary' : 'tertiary'"
          size="sm"
          @click="currentTab = 'ocr'"
        />
        <DsfrButton
          label="Mes tâches"
          :priority="currentTab === 'tasks' ? 'primary' : 'tertiary'"
          size="sm"
          @click="currentTab = 'tasks'"
        />
      </div>

      <div class="flex flex-col gap-[2rem] p-[24px] bg-[var(--background-default-grey)] border border-[var(--border-default-grey)] mt-10">
        <InfoBulle />

        <div class="page-container">
          <div v-if="currentTab === 'ocr'">
            <!-- File Upload -->
            <div class="file-upload-container flex flex-col">
              <DsfrFileUpload
                :label="uploadLabel"
                :hint="uploadHint"
                :error="uploadError"
                :accept="uploadAccept"
                @change="selectFile"
              />

              <div class="mt-4">
                <DsfrButton
                  label="Extraire le texte"
                  size="lg"
                  :disabled="!selectedFile || isPolling || isLoading"
                  @click="startOcr"
                />
              </div>

              <ProgressBar
                :visible="isPolling && status === 'in_progress'"
                :progress="progressPercent"
              />

              <div class="flex justify-center">
                <OcrViewer
                  v-if="taskData?.output && !isPolling"
                  :data="{ id: taskData.id, pages: taskData.output.pages }"
                />
              </div>
            </div>
          </div>

          <div v-else>
            <TasksTab />
          </div>
        </div>
      </div>

      <CustomCard
        :img-src="Media"
        img-alt="image de stylo sur feuille de papier"
        title="Comment utiliser “Extraire un texte” ?"
        description=""
        infos="
            <ol>
              <li>
                Ajoutez un PDF avec un texte scanné (texte numérisé, photo d’un texte imprimé, formulaire, ...)
              </li>
              <li>
                Cliquez sur “Extraire le texte”
              </li>
            </ol>
            <p>Les textes scannés apparaissent en rouge. Vous pouvez  extraire et télécharger le contenu du fichier en fichier .txt.</p>
          "
        hint="💡 Les textes scannés apparaissent en rouge. Vous pouvez  extraire et télécharger le contenu du fichier en fichier .txt."
      />
    </div>
  </div>
</template>
