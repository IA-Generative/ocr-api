<script setup lang="ts">
import { computed } from 'vue'
import { getKeycloak } from '@/utils/keycloak'
import useToaster from './composables/use-toaster'

const keycloak = getKeycloak()
const isLoggedIn = computed(() => keycloak.authenticated)

const toaster = useToaster()

const serviceTitle = 'Reconnaître un texte scanné'
const serviceDescription = 'Extraire le texte d\'une image ou d\'un document scanné'
const logoText = ['Ministère', 'de l’intérieur']

const quickLinks = computed(() => {
  const items = []
  if (!isLoggedIn.value) {
    items.push(
      { label: 'Se connecter', to: '/login', class: 'fr-icon-user-fill' },
    )
  }
  else {
    items.push(
      { label: 'Se déconnecter', to: '/logout', class: 'fr-icon-logout-box-r-line' }
    )
  }

  return items
})
</script>

<template>
  <DsfrHeader
    :service-title="serviceTitle"
    :service-description="serviceDescription"
    :logo-text="logoText"
    :quick-links="quickLinks"
  />

  <div class="fr-container  fr-mt-3w  fr-mt-md-5w  fr-mb-5w">
    <router-view />
  </div>

  <AppToaster
    :messages="toaster.messages"
    @close-message="toaster.removeMessage($event)"
  />
</template>
