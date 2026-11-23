<template>
  <Dialog
    v-model:visible="visible"
    header="Выбор профиля запуска AnyDesk"
    :modal="true"
    :style="{ width: '540px' }"
  >
    <div class="flex flex-col gap-4 py-2">
      <!-- Target Station Info Box -->
      <div v-if="station" class="p-3 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl flex items-center justify-between">
        <div>
          <div class="text-xs text-slate-500 dark:text-slate-400 font-medium">Подключение к рабочей станции:</div>
          <div class="font-bold text-slate-900 dark:text-slate-100 text-sm mt-0.5 flex items-center gap-2">
            <span>{{ station.description || 'Рабочее место' }}</span>
            <span class="font-mono text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/60 px-2 py-0.5 rounded text-xs border border-blue-200 dark:border-blue-800">
              {{ station.anydesk_id }}
            </span>
          </div>
        </div>
        <div v-if="station.any_pass" class="text-right">
          <span class="text-[11px] text-emerald-700 dark:text-emerald-400 font-semibold flex items-center justify-end gap-1">
            <i class="pi pi-check-circle text-[10px]"></i> Пароль задан
          </span>
          <span class="text-xs font-mono font-medium text-slate-500 dark:text-slate-400">
            скопируется в буфер при запуске
          </span>
        </div>
      </div>

      <!-- Profiles List Header & Manage button -->
      <div class="flex items-center justify-between pt-1">
        <span class="text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-300">
          Доступные профили запуска ({{ companionStore.profiles.length }})
        </span>
        <Button
          v-if="authStore.canEdit"
          label="Настройка профилей"
          icon="pi pi-cog"
          text
          size="small"
          class="!p-0 !text-xs text-blue-600 dark:text-blue-400"
          @click="openManagement"
        />
      </div>

      <!-- Profiles List -->
      <div class="flex flex-col gap-2 max-h-72 overflow-y-auto pr-1">
        <div v-if="loading" class="text-center py-8 text-slate-400 dark:text-slate-500">
          <i class="pi pi-spin pi-spinner text-2xl"></i>
        </div>

        <div v-else-if="!companionStore.profiles.length" class="text-center py-8 text-slate-400 dark:text-slate-500 text-sm">
          Нет настроенных профилей AnyDesk.
        </div>

        <div
          v-for="prof in companionStore.profiles"
          :key="prof.id"
          class="p-3 rounded-xl border transition cursor-pointer flex items-center justify-between"
          :class="selectedProfileId === prof.id
            ? 'border-blue-500 bg-blue-50/50 dark:bg-blue-950/40 ring-1 ring-blue-500'
            : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600 hover:bg-slate-50/70 dark:hover:bg-slate-800/60'"
          @click="selectedProfileId = prof.id"
          @dblclick="selectAndLaunch(prof.id)"
          title="Нажмите для выбора, дважды кликните или нажмите Enter для запуска"
        >
          <div class="flex items-center gap-3">
            <!-- Radio Selector -->
            <RadioButton
              v-model="selectedProfileId"
              :inputId="`prof_${prof.id}`"
              :value="prof.id"
            />

            <div class="flex flex-col">
              <div class="flex items-center gap-2">
                <span class="font-bold text-slate-900 dark:text-slate-100 text-sm">{{ prof.name }}</span>
                <!-- Sandbox Badge -->
                <Tag
                  v-if="prof.is_sandbox"
                  :value="`Песочница: ${prof.sandbox_params || 'Default'}`"
                  severity="help"
                  class="!text-[10px] !px-1.5 !py-0.2"
                />
                <!-- Direct Badge -->
                <Tag
                  v-else
                  value="Обычный запуск"
                  severity="info"
                  class="!text-[10px] !px-1.5 !py-0.2"
                />
                <!-- Default Tag -->
                <span
                  v-if="companionStore.preferredProfileId === prof.id"
                  class="text-[10px] font-semibold bg-emerald-100 dark:bg-emerald-950/80 text-emerald-800 dark:text-emerald-300 px-1.5 py-0.2 rounded"
                >
                  Мой выбор
                </span>
              </div>
              <span class="text-[11px] text-slate-400 dark:text-slate-500 truncate max-w-sm font-mono mt-0.5">
                {{ prof.exe_path || 'C:\\Program Files (x86)\\AnyDesk\\AnyDesk.exe' }}
              </span>
            </div>
          </div>

          <i
            class="pi pi-play text-slate-400 hover:text-blue-600 transition"
            title="Выбрать и запустить"
          ></i>
        </div>
      </div>

      <!-- Remember as default checkbox -->
      <div class="flex items-center gap-2 pt-2 border-t border-slate-100">
        <Checkbox v-model="rememberAsDefault" :binary="true" inputId="remember_prof" />
        <label for="remember_prof" class="text-xs text-slate-600 cursor-pointer select-none">
          Запомнить этот профиль как мой выбор по умолчанию (для быстрого запуска в 1 клик)
        </label>
      </div>
    </div>

    <template #footer>
      <div class="flex justify-between items-center w-full">
        <Button label="Отмена (Esc)" severity="secondary" text size="small" @click="visible = false" />
        <Button
          label="Запустить AnyDesk (Enter)"
          icon="pi pi-play"
          severity="primary"
          size="small"
          :loading="launching"
          @click="confirmLaunch"
        />
      </div>
    </template>
  </Dialog>

  <!-- Management Modal Component -->
  <AnydeskVersionManagementModal
    v-model="showManagement"
    @updated="loadProfiles"
  />
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import RadioButton from 'primevue/radiobutton'
import Checkbox from 'primevue/checkbox'
import Tag from 'primevue/tag'
import { useToast } from 'primevue/usetoast'
import { useAuthStore } from '../stores/auth'
import { useCompanionStore } from '../stores/companion'
import AnydeskVersionManagementModal from './AnydeskVersionManagementModal.vue'

const props = defineProps({
  modelValue: Boolean,
  station: Object,
})
const emit = defineEmits(['update:modelValue', 'launched'])

const toast = useToast()
const authStore = useAuthStore()
const companionStore = useCompanionStore()

const visible = ref(props.modelValue)
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    initSelection()
    setTimeout(() => {
      if (visible.value) {
        window.addEventListener('keydown', handleKeydown)
      }
    }, 150)
  } else {
    window.removeEventListener('keydown', handleKeydown)
  }
})
watch(visible, (val) => emit('update:modelValue', val))

const loading = ref(false)
const launching = ref(false)
const selectedProfileId = ref(null)
const rememberAsDefault = ref(false)
const showManagement = ref(false)

const handleKeydown = (e) => {
  if (!visible.value) return
  if (showManagement.value) return
  if (e.key === 'Enter') {
    e.preventDefault()
    confirmLaunch()
  } else if (e.key === 'ArrowDown') {
    e.preventDefault()
    const profiles = companionStore.profiles
    if (!profiles || !profiles.length) return
    const idx = profiles.findIndex(p => p.id === selectedProfileId.value)
    if (idx === -1 || idx === profiles.length - 1) {
      selectedProfileId.value = profiles[0].id
    } else {
      selectedProfileId.value = profiles[idx + 1].id
    }
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    const profiles = companionStore.profiles
    if (!profiles || !profiles.length) return
    const idx = profiles.findIndex(p => p.id === selectedProfileId.value)
    if (idx <= 0) {
      selectedProfileId.value = profiles[profiles.length - 1].id
    } else {
      selectedProfileId.value = profiles[idx - 1].id
    }
  }
}

const initSelection = async () => {
  if (!companionStore.profiles.length) {
    loading.value = true
    await companionStore.loadProfiles()
    loading.value = false
  }
  selectedProfileId.value = companionStore.preferredProfileId || companionStore.preferredProfile?.id || (companionStore.profiles[0]?.id ?? null)
}

const loadProfiles = async () => {
  await companionStore.loadProfiles()
}

const openManagement = () => {
  showManagement.value = true
}

const selectAndLaunch = async (profId) => {
  selectedProfileId.value = profId
  await confirmLaunch()
}

const copyPasswordToClipboard = async (pass) => {
  if (!pass) return
  try {
    if (navigator?.clipboard?.writeText) {
      await navigator.clipboard.writeText(pass)
    } else {
      const textArea = document.createElement('textarea')
      textArea.value = pass
      document.body.appendChild(textArea)
      textArea.select()
      document.execCommand('copy')
      document.body.removeChild(textArea)
    }
    toast.add({
      severity: 'info',
      summary: 'Пароль скопирован',
      detail: 'Пароль AnyDesk скопирован в буфер обмена',
      life: 2500,
    })
  } catch (e) {
    console.error('Password copy error:', e)
  }
}

const confirmLaunch = async () => {
  if (launching.value) return
  if (!props.station?.anydesk_id) {
    toast.add({ severity: 'error', summary: 'Ошибка', detail: 'ID AnyDesk не указан', life: 2500 })
    return
  }

  // Copy password to clipboard if station has a password
  if (props.station?.any_pass) {
    await copyPasswordToClipboard(props.station.any_pass)
  }

  const chosenProfile = companionStore.profiles.find(p => p.id === selectedProfileId.value) || companionStore.preferredProfile

  if (rememberAsDefault.value && chosenProfile) {
    companionStore.setPreferredProfile(chosenProfile.id)
  }

  launching.value = true
  try {
    const res = await companionStore.launchAnydesk({
      anydesk_id: props.station.anydesk_id,
      any_pass: props.station.any_pass || '',
      profile: chosenProfile,
    })

    toast.add({
      severity: res.success ? 'success' : 'warn',
      summary: 'AnyDesk',
      detail: res.message,
      life: 3500,
    })
    visible.value = false
    emit('launched', chosenProfile)
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Ошибка запуска', detail: err.message, life: 3000 })
  } finally {
    launching.value = false
  }
}

onMounted(() => {
  companionStore.loadProfiles()
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>
