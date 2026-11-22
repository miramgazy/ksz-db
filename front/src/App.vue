<template>
  <div class="app-root min-h-screen flex flex-col bg-slate-50">
    <Toast position="top-right" :baseZIndex="9999" />
    <ConfirmDialog />
    <router-view />
  </div>
</template>

<script setup>
import Toast from 'primevue/toast'
import ConfirmDialog from 'primevue/confirmdialog'
import { onMounted } from 'vue'
import { useCompanionStore } from './stores/companion'

const companionStore = useCompanionStore()

onMounted(() => {
  // Check local companion helper availability once on startup if authenticated
  if (localStorage.getItem('access_token')) {
    companionStore.checkStatus()
  }
})
</script>
