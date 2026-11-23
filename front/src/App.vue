<template>
  <div class="app-root min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950 text-slate-800 dark:text-slate-100 transition-colors">
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
import { useThemeStore } from './stores/theme'

const companionStore = useCompanionStore()
const themeStore = useThemeStore()

onMounted(() => {
  themeStore.initTheme()
  // Check local companion helper availability once on startup if authenticated
  if (localStorage.getItem('access_token')) {
    companionStore.checkStatus()
  }
})
</script>
