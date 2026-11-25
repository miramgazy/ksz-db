import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import Aura from '@primevue/themes/aura'
import ToastService from 'primevue/toastservice'
import ConfirmationService from 'primevue/confirmationservice'
import { FilterService } from 'primevue/api'
import { matchesSmartSearch, getSearchVariants, normalizeKazakh } from './utils/keyboard'

import 'primeicons/primeicons.css'
import './style.css'

import App from './App.vue'
import router from './router'

// Enhance PrimeVue FilterService globally for all Select, MultiSelect, and DataTable filters
// Enables bilingual search (QWERTY <-> JCUKEN) and Kazakh letter normalization
if (FilterService && FilterService.methods) {
  const originalContains = FilterService.methods.contains
  FilterService.methods.contains = (value, filter, filterLocale) => {
    if (originalContains && originalContains(value, filter, filterLocale)) {
      return true
    }
    return matchesSmartSearch(value, filter)
  }

  const originalStartsWith = FilterService.methods.startsWith
  FilterService.methods.startsWith = (value, filter, filterLocale) => {
    if (originalStartsWith && originalStartsWith(value, filter, filterLocale)) {
      return true
    }
    if (!filter || !value) return false
    const variants = getSearchVariants(filter)
    const valLower = String(value).toLowerCase()
    const valNorm = normalizeKazakh(valLower)
    return variants.some(v => valLower.startsWith(v) || valNorm.startsWith(v))
  }
}

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
      prefix: 'p',
      darkModeSelector: '.dark',
      cssLayer: false
    }
  }
})

app.use(ToastService)
app.use(ConfirmationService)

app.mount('#app')
