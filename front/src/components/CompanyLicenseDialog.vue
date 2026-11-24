<template>
  <Dialog
    v-model:visible="visible"
    :modal="true"
    :style="{ width: '920px', maxWidth: '96vw' }"
    :closable="true"
    :dismissable-mask="true"
  >
    <template #header>
      <div class="flex items-center justify-between w-full pr-6">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-amber-500/10 dark:bg-amber-400/10 flex items-center justify-center text-amber-600 dark:text-amber-400">
            <i class="pi pi-id-card text-xl"></i>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h3 class="font-bold text-lg text-slate-800 dark:text-white m-0">
                Лицензии: {{ company?.place_name }}
              </h3>
              <Tag
                v-if="expirationStatus"
                :severity="expirationStatus.severity"
                :value="expirationStatus.label"
                class="text-xs"
              />
            </div>
            <p class="text-xs text-slate-500 dark:text-slate-400 m-0">
              {{ company?.city ? company.city + ' • ' : '' }}CRM ID: {{ crmIdDisplay }} • UID: {{ uidDisplay }}
            </p>
          </div>
        </div>
      </div>
    </template>

    <div class="flex flex-col gap-4 py-1">
      <!-- Error Alert (if last update failed) -->
      <div
        v-if="company?.last_license_error"
        class="flex items-start gap-3 p-3.5 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900/60 text-red-700 dark:text-red-300 text-sm"
      >
        <i class="pi pi-exclamation-triangle text-lg mt-0.5 text-red-500 shrink-0"></i>
        <div class="flex-1">
          <div class="font-semibold text-xs uppercase tracking-wider text-red-800 dark:text-red-200 mb-0.5">
            Ошибка последнего обновления с сервера iiko:
          </div>
          <div class="text-xs break-words">
            {{ company.last_license_error }}
          </div>
        </div>
      </div>

      <!-- Quick Summary Cards -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <!-- Card 1: Expiration -->
        <div class="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/80 flex flex-col justify-between">
          <span class="text-[11px] font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            Срок лицензии
          </span>
          <div class="mt-1">
            <div class="font-bold text-base text-slate-900 dark:text-white">
              {{ expirationFormatted }}
            </div>
            <div class="text-xs text-slate-500 dark:text-slate-400">
              {{ daysRemainingText }}
            </div>
          </div>
        </div>

        <!-- Card 2: Version & Edition -->
        <div class="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/80 flex flex-col justify-between">
          <span class="text-[11px] font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            Версия и Редакция
          </span>
          <div class="mt-1">
            <div class="font-bold text-base text-slate-900 dark:text-white">
              {{ licenseData?.iiko_version || company?.iiko_version || '—' }}
            </div>
            <div class="text-xs text-slate-500 dark:text-slate-400">
              {{ licenseData?.edition || 'IIKO_RMS' }}
            </div>
          </div>
        </div>

        <!-- Card 3: Modules count -->
        <div class="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/80 flex flex-col justify-between">
          <span class="text-[11px] font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            Всего модулей
          </span>
          <div class="mt-1">
            <div class="font-bold text-base text-indigo-600 dark:text-indigo-400">
              {{ modulesList.length }} модулей
            </div>
            <div class="text-xs text-slate-500 dark:text-slate-400">
              {{ permanentCount }} бессрочных
            </div>
          </div>
        </div>

        <!-- Card 4: Last sync -->
        <div class="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/80 flex flex-col justify-between">
          <span class="text-[11px] font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            Синхронизация в базе
          </span>
          <div class="mt-1">
            <div class="font-bold text-sm text-slate-900 dark:text-white">
              {{ lastUpdatedFormatted }}
            </div>
            <div class="text-xs text-slate-500 dark:text-slate-400">
              генерация: {{ licenseData?.generated || '—' }}
            </div>
          </div>
        </div>
      </div>

      <!-- Search & Filters Bar -->
      <div class="flex items-center justify-between gap-3 pt-1">
        <div class="relative flex-1">
          <i class="pi pi-search absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm"></i>
          <InputText
            v-model="searchQuery"
            placeholder="Поиск по названию лицензии/модуля или ID..."
            class="w-full pl-9 text-sm"
          />
        </div>
        <div class="text-xs text-slate-500 dark:text-slate-400 shrink-0">
          Найдено: <strong class="text-slate-800 dark:text-slate-200">{{ filteredModules.length }}</strong> из {{ modulesList.length }}
        </div>
      </div>

      <!-- Modules Table -->
      <div class="border border-slate-200 dark:border-slate-700/80 rounded-xl overflow-hidden bg-white dark:bg-slate-800/50">
        <DataTable
          :value="filteredModules"
          :paginator="true"
          :rows="12"
          :rows-per-page-options="[12, 25, 50, 100]"
          size="small"
          striped-rows
          responsive-layout="scroll"
          class="p-datatable-sm"
        >
          <template #empty>
            <div class="text-center py-10 text-slate-400 dark:text-slate-500">
              <i class="pi pi-id-card text-4xl mb-3 block opacity-40"></i>
              <div v-if="modulesList.length && searchQuery">
                По запросу «{{ searchQuery }}» ничего не найдено.
              </div>
              <div v-else>
                Данные лицензии заведения отсутствуют в базе.<br>
                Нажмите <strong>«Обновить лицензию сейчас»</strong> для получения сведений через ClearBat.
              </div>
            </div>
          </template>

          <Column field="name" header="Название модуля" sortable>
            <template #body="{ data }">
              <span class="font-medium text-slate-800 dark:text-slate-100 text-xs">
                {{ data.name }}
              </span>
            </template>
          </Column>

          <Column field="id" header="ID" sortable style="width: 100px">
            <template #body="{ data }">
              <span class="font-mono text-xs text-slate-500 dark:text-slate-400">
                {{ data.id }}
              </span>
            </template>
          </Column>

          <Column field="count" header="Подключений" sortable style="width: 110px">
            <template #body="{ data }">
              <Tag
                :value="data.count"
                severity="info"
                class="font-mono text-xs px-2"
              />
            </template>
          </Column>

          <Column field="from" header="С даты" sortable style="width: 120px">
            <template #body="{ data }">
              <span class="text-xs text-slate-600 dark:text-slate-400">
                {{ data.from || '—' }}
              </span>
            </template>
          </Column>

          <Column field="to" header="По дату" sortable style="width: 130px">
            <template #body="{ data }">
              <span v-if="!data.to" class="text-xs text-emerald-600 dark:text-emerald-400 font-medium">
                Бессрочно
              </span>
              <span v-else :class="getModuleDateClass(data.to)" class="text-xs">
                {{ data.to }}
              </span>
            </template>
          </Column>

          <Column header="Статус" style="width: 110px">
            <template #body="{ data }">
              <Tag
                v-if="!data.to"
                severity="success"
                value="Бессрочно"
                class="text-[11px]"
              />
              <Tag
                v-else-if="isModuleExpired(data.to)"
                severity="danger"
                value="Истек"
                class="text-[11px]"
              />
              <Tag
                v-else
                severity="success"
                value="Активен"
                class="text-[11px]"
              />
            </template>
          </Column>
        </DataTable>
      </div>
    </div>

    <template #footer>
      <div class="flex items-center justify-between w-full pt-2">
        <div class="text-xs text-slate-500 dark:text-slate-400">
          <span v-if="companionStore.isOnline" class="flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400">
            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            Агент Companion онлайн
          </span>
          <span v-else class="text-slate-400">
            Агент Companion офлайн
          </span>
        </div>
        <div class="flex items-center gap-2">
          <Button
            label="Обновить лицензию сейчас"
            icon="pi pi-sync"
            severity="warning"
            size="small"
            :loading="updating"
            @click="handleRefreshLicense"
          />
          <Button
            label="Закрыть"
            icon="pi pi-times"
            severity="secondary"
            size="small"
            outlined
            @click="visible = false"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Tag from 'primevue/tag'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { useCompanionStore } from '@/stores/companion'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  company: {
    type: Object,
    default: () => ({})
  },
  updating: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'refresh'])

const companionStore = useCompanionStore()
const searchQuery = ref('')

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const licenseData = computed(() => {
  return props.company?.license_data || {}
})

const crmIdDisplay = computed(() => {
  return licenseData.value?.crm_id || props.company?.crm_id || 'Не указан'
})

const uidDisplay = computed(() => {
  return licenseData.value?.uid || props.company?.uid || 'Не указан'
})

const modulesList = computed(() => {
  const mods = licenseData.value?.modules
  if (Array.isArray(mods)) {
    return mods
  }
  return []
})

const permanentCount = computed(() => {
  return modulesList.value.filter(m => !m.to).length
})

const filteredModules = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) {
    return modulesList.value
  }
  return modulesList.value.filter(m => {
    const nameMatch = m.name && m.name.toLowerCase().includes(q)
    const idMatch = m.id && String(m.id).toLowerCase().includes(q)
    const fromMatch = m.from && m.from.includes(q)
    const toMatch = m.to && m.to.includes(q)
    return nameMatch || idMatch || fromMatch || toMatch
  })
})

const expirationFormatted = computed(() => {
  const exp = licenseData.value?.expiration
  if (!exp) return '—'
  try {
    const d = new Date(exp)
    if (!isNaN(d)) {
      return d.toLocaleDateString('ru-RU')
    }
  } catch (e) {}
  return exp
})

const lastUpdatedFormatted = computed(() => {
  const dt = props.company?.license_updated_at || licenseData.value?.parsed_at
  if (!dt) return 'Не обновлялось'
  try {
    const d = new Date(dt)
    if (!isNaN(d)) {
      return d.toLocaleString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  } catch (e) {}
  return dt
})

const daysRemaining = computed(() => {
  const exp = licenseData.value?.expiration
  if (!exp) return null
  const target = new Date(exp)
  if (isNaN(target)) return null
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  target.setHours(0, 0, 0, 0)
  return Math.round((target - today) / (1000 * 60 * 60 * 24))
})

const daysRemainingText = computed(() => {
  const days = daysRemaining.value
  if (days === null) return 'Бессрочная / нет данных'
  if (days < 0) return `Истекла ${Math.abs(days)} дн. назад`
  if (days === 0) return 'Истекает сегодня'
  return `Осталось ${days} дн.`
})

const expirationStatus = computed(() => {
  const days = daysRemaining.value
  if (days === null) {
    if (!modulesList.value.length) return null
    return { severity: 'success', label: 'Бессрочная' }
  }
  if (days < 0) {
    return { severity: 'danger', label: 'Лицензия истекла' }
  }
  if (days <= 14) {
    return { severity: 'warn', label: `Истекает (${days} дн.)` }
  }
  return { severity: 'success', label: 'Лицензия активна' }
})

const isModuleExpired = (toDateStr) => {
  if (!toDateStr) return false
  const target = new Date(toDateStr)
  if (isNaN(target)) return false
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  target.setHours(0, 0, 0, 0)
  return target < today
}

const getModuleDateClass = (toDateStr) => {
  if (isModuleExpired(toDateStr)) {
    return 'text-red-600 dark:text-red-400 font-medium'
  }
  return 'text-slate-800 dark:text-slate-200'
}

const handleRefreshLicense = () => {
  emit('refresh')
}
</script>
