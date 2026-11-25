<template>
  <Dialog
    :visible="visible"
    modal
    dismissableMask
    :style="{ width: '94vw', maxWidth: '1500px' }"
    :header="'Реестр подключений AnyDesk'"
    class="p-dialog-maximized-mobile"
    @update:visible="emit('update:visible', $event)"
  >
    <div class="flex flex-col gap-4">
      <!-- Top Action & Search Bar inside Dialog -->
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 pb-2 border-b border-slate-200 dark:border-slate-800">
        <div>
          <div class="flex items-center gap-2">
            <span class="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 font-mono border border-blue-200 dark:border-blue-800">
              {{ totalCount }} станций
            </span>
            <span class="text-xs text-slate-500 dark:text-slate-400">Единая база удаленных рабочих мест инженеров</span>
          </div>
        </div>

        <div class="flex items-center gap-2.5 w-full sm:w-auto">
          <!-- Search Bar -->
          <div class="w-full sm:w-80">
            <IconField iconPosition="left">
              <InputIcon class="pi pi-search" />
              <InputText
                v-model="searchQuery"
                placeholder="Поиск по ID, описанию, заведению..."
                class="w-full text-xs"
                @input="onSearchInput"
              />
            </IconField>
          </div>

          <!-- Manage AnyDesk Profiles Button -->
          <Button
            label="Профили / Sandbox"
            icon="pi pi-shield"
            severity="secondary"
            outlined
            size="small"
            class="whitespace-nowrap text-xs"
            title="Управление песочницами и версиями AnyDesk"
            @click="showManagementModal = true"
          />
        </div>
      </div>

      <!-- Main AnyDesk Table -->
      <div class="rounded-lg border border-slate-200 dark:border-slate-800 overflow-hidden">
        <DataTable
          :value="stations"
          :loading="loading"
          dataKey="id"
          class="p-datatable-sm"
          stripedRows
          hoverableRows
          responsiveLayout="scroll"
        >
          <template #empty>
            <div class="text-center py-10 text-slate-400">
              <i class="pi pi-desktop text-3xl mb-2 text-slate-300 dark:text-slate-600"></i>
              <p class="text-sm">Подключения AnyDesk не найдены.</p>
            </div>
          </template>

          <!-- 1. Establishment / City -->
          <Column header="Заведение / Город" style="min-width: 220px">
            <template #body="{ data }">
              <div class="flex flex-col">
                <button
                  type="button"
                  class="text-left font-bold text-blue-600 dark:text-blue-400 hover:underline hover:text-blue-800 dark:hover:text-blue-300 transition cursor-pointer text-sm"
                  @click="handleOpenCompany(data.company)"
                >
                  {{ data.company_place_name || `Заведение #${data.company}` }}
                </button>
                <span class="text-xs text-slate-500 dark:text-slate-400 font-medium mt-0.5 flex items-center gap-1">
                  <i class="pi pi-map-marker text-[10px] text-slate-400 dark:text-slate-500"></i>
                  {{ data.company_city || 'Город не указан' }}
                </span>
              </div>
            </template>
          </Column>

          <!-- 2. System (iiko or Rosta) -->
          <Column header="Система" style="min-width: 95px">
            <template #body="{ data }">
              <Tag
                :value="data.company_software_type === 'ROSTA' ? 'Rosta' : 'iiko'"
                :severity="data.company_software_type === 'ROSTA' ? 'success' : 'info'"
                class="!text-xs font-bold font-mono !px-2 !py-0.5"
              />
            </template>
          </Column>

          <!-- 3. Workstation Description -->
          <Column field="description" header="Рабочее место" style="min-width: 170px">
            <template #body="{ data }">
              <div class="flex items-center gap-1.5 font-medium text-slate-800 dark:text-slate-200 text-sm">
                <i class="pi pi-desktop text-xs text-slate-400 dark:text-slate-500 shrink-0"></i>
                <span>{{ data.description || 'Рабочее место' }}</span>
              </div>
            </template>
          </Column>

          <!-- 4. AnyDesk ID -->
          <Column field="anydesk_id" header="AnyDesk ID" style="min-width: 140px">
            <template #body="{ data }">
              <QuickCopyBtn :text="data.anydesk_id" label="AnyDesk ID">
                <span class="font-mono font-bold text-slate-900 dark:text-white text-sm tracking-wide">{{ data.anydesk_id }}</span>
              </QuickCopyBtn>
            </template>
          </Column>

          <!-- 5. Password -->
          <Column field="any_pass" header="Пароль" style="min-width: 120px">
            <template #body="{ data }">
              <QuickCopyBtn v-if="data.any_pass" :text="data.any_pass" label="Пароль AnyDesk">
                <span class="font-mono text-xs">••••••••</span>
              </QuickCopyBtn>
              <span v-else class="text-xs text-slate-400 dark:text-slate-500 font-mono italic">без пароля</span>
            </template>
          </Column>

          <!-- 6. Actions -->
          <Column header="Действие" style="min-width: 150px; text-align: right">
            <template #body="{ data }">
              <div class="flex items-center justify-end gap-1">
                <Button
                  icon="pi pi-play"
                  label="Запуск"
                  size="small"
                  severity="success"
                  text
                  @click="openVersionSelect(data)"
                  title="Выбрать профиль и запустить AnyDesk"
                />
                <Button
                  icon="pi pi-chevron-down"
                  size="small"
                  severity="secondary"
                  text
                  rounded
                  @click="openVersionSelect(data)"
                  title="Выбрать профиль AnyDesk"
                />
                <Button
                  v-if="authStore.canEdit"
                  icon="pi pi-pencil"
                  size="small"
                  severity="secondary"
                  text
                  rounded
                  @click="openEditStation(data)"
                  title="Редактировать рабочее место"
                />
                <Button
                  v-if="authStore.canEdit"
                  icon="pi pi-trash"
                  size="small"
                  severity="danger"
                  text
                  rounded
                  @click="deleteStation(data)"
                  title="Удалить рабочее место"
                />
              </div>
            </template>
          </Column>
        </DataTable>

        <!-- Pagination -->
        <div class="p-3 border-t border-slate-200 dark:border-slate-800 flex flex-col md:flex-row justify-between items-center gap-3 text-xs text-slate-600 dark:text-slate-400 bg-slate-50 dark:bg-slate-900/60">
          <div class="flex items-center gap-3 flex-wrap">
            <span class="whitespace-nowrap font-medium text-slate-600 dark:text-slate-300">Показано {{ stations.length }} из {{ totalCount }}</span>
            <div class="flex items-center gap-1.5 border-l border-slate-200 dark:border-slate-700 pl-3">
              <span class="text-slate-500 dark:text-slate-400 whitespace-nowrap">Показывать по:</span>
              <Select
                v-model="pageSize"
                :options="pageSizeOptions"
                optionLabel="label"
                optionValue="value"
                size="small"
                class="w-20 text-xs font-medium"
                @change="onPageSizeChange"
              />
            </div>
          </div>

          <!-- Page Navigation -->
          <div class="flex items-center gap-1 flex-wrap justify-center">
            <button
              type="button"
              class="w-7 h-7 flex items-center justify-center rounded-lg text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-100 hover:bg-slate-200 dark:hover:bg-slate-800 disabled:opacity-30 disabled:pointer-events-none transition cursor-pointer"
              :disabled="currentPage <= 1"
              @click="changePage(1)"
              title="Первая страница"
            >
              <i class="pi pi-angle-double-left text-xs"></i>
            </button>

            <button
              type="button"
              class="w-7 h-7 flex items-center justify-center rounded-lg text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-100 hover:bg-slate-200 dark:hover:bg-slate-800 disabled:opacity-30 disabled:pointer-events-none transition cursor-pointer"
              :disabled="currentPage <= 1"
              @click="changePage(currentPage - 1)"
              title="Предыдущая страница"
            >
              <i class="pi pi-chevron-left text-xs"></i>
            </button>

            <template v-for="(p, idx) in visiblePages" :key="idx">
              <span
                v-if="p === '...'"
                class="w-6 h-7 flex items-center justify-center text-slate-400 dark:text-slate-500 font-mono select-none text-xs"
              >
                ...
              </span>
              <button
                v-else
                type="button"
                @click="changePage(p)"
                class="min-w-7 h-7 px-1.5 flex items-center justify-center rounded-lg text-xs font-mono font-medium transition cursor-pointer"
                :class="p === currentPage
                  ? 'bg-blue-600 text-white font-bold shadow-xs'
                  : 'text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-800 hover:text-blue-600 dark:hover:text-blue-400'"
              >
                {{ p }}
              </button>
            </template>

            <button
              type="button"
              class="w-7 h-7 flex items-center justify-center rounded-lg text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-100 hover:bg-slate-200 dark:hover:bg-slate-800 disabled:opacity-30 disabled:pointer-events-none transition cursor-pointer"
              :disabled="currentPage >= totalPages"
              @click="changePage(currentPage + 1)"
              title="Следующая страница"
            >
              <i class="pi pi-chevron-right text-xs"></i>
            </button>

            <button
              type="button"
              class="w-7 h-7 flex items-center justify-center rounded-lg text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-100 hover:bg-slate-200 dark:hover:bg-slate-800 disabled:opacity-30 disabled:pointer-events-none transition cursor-pointer"
              :disabled="currentPage >= totalPages"
              @click="changePage(totalPages)"
              title="Последняя страница"
            >
              <i class="pi pi-angle-double-right text-xs"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Anydesk Version Select Modal -->
    <AnydeskVersionSelectModal
      v-model="showVersionSelectModal"
      :station="selectedStationForLaunch"
    />

    <!-- Anydesk Version Management Modal -->
    <AnydeskVersionManagementModal
      v-model="showManagementModal"
      @updated="onManagementUpdated"
    />

    <!-- Edit Station Modal -->
    <AnydeskStationModal
      v-model="showEditStationModal"
      :company-id="selectedStationToEdit?.company"
      :station="selectedStationToEdit"
      @saved="loadStations"
    />
  </Dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import Dialog from 'primevue/dialog'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import Tag from 'primevue/tag'
import Select from 'primevue/select'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { useAuthStore } from '../stores/auth'
import { useCompanionStore } from '../stores/companion'
import { anydeskApi } from '../api/anydesk'
import QuickCopyBtn from './QuickCopyBtn.vue'
import AnydeskVersionSelectModal from './AnydeskVersionSelectModal.vue'
import AnydeskVersionManagementModal from './AnydeskVersionManagementModal.vue'
import AnydeskStationModal from './AnydeskStationModal.vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:visible', 'open-company'])

const toast = useToast()
const confirm = useConfirm()
const authStore = useAuthStore()
const companionStore = useCompanionStore()

const loading = ref(false)
const stations = ref([])
const totalCount = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const pageSizeOptions = [
  { label: '20', value: 20 },
  { label: '50', value: 50 },
  { label: '100', value: 100 },
]
const totalPages = ref(1)

const visiblePages = computed(() => {
  const total = totalPages.value || 1
  const current = currentPage.value

  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1)
  }

  const pages = []

  if (current <= 4) {
    for (let i = 1; i <= 5; i++) pages.push(i)
    pages.push('...')
    pages.push(total)
  } else if (current >= total - 3) {
    pages.push(1)
    pages.push('...')
    for (let i = total - 4; i <= total; i++) pages.push(i)
  } else {
    pages.push(1)
    pages.push('...')
    pages.push(current - 1)
    pages.push(current)
    pages.push(current + 1)
    pages.push('...')
    pages.push(total)
  }

  return pages
})

const searchQuery = ref('')

const showVersionSelectModal = ref(false)
const showManagementModal = ref(false)
const selectedStationForLaunch = ref(null)

const showEditStationModal = ref(false)
const selectedStationToEdit = ref(null)

const onPageSizeChange = () => {
  currentPage.value = 1
  loadStations()
}

let searchTimeout = null
const onSearchInput = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    loadStations()
  }, 350)
}

const loadStations = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (searchQuery.value.trim()) params.search = searchQuery.value.trim()

    const res = await anydeskApi.getAnydeskStations(params)
    stations.value = res.data.results || res.data
    totalCount.value = res.data.count || stations.value.length
    totalPages.value = Math.ceil(totalCount.value / pageSize.value) || 1
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Ошибка', detail: 'Не удалось загрузить реестр AnyDesk', life: 3000 })
  } finally {
    loading.value = false
  }
}

const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  loadStations()
}

const handleOpenCompany = (companyId) => {
  emit('open-company', companyId)
}

const openVersionSelect = (station) => {
  selectedStationForLaunch.value = station
  showVersionSelectModal.value = true
}

const openEditStation = (station) => {
  selectedStationToEdit.value = station
  showEditStationModal.value = true
}

const deleteStation = (station) => {
  confirm.require({
    message: `Удалить рабочее место AnyDesk '${station.anydesk_id}' (${station.description || 'Рабочее место'})?`,
    header: 'Подтверждение удаления',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Удалить',
    rejectLabel: 'Отмена',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await anydeskApi.deleteAnydeskStation(station.id)
        toast.add({ severity: 'success', summary: 'Успешно', detail: 'Рабочее место удалено', life: 2500 })
        loadStations()
      } catch (err) {
        toast.add({ severity: 'error', summary: 'Ошибка удаления', detail: err.message, life: 3000 })
      }
    },
  })
}

const onManagementUpdated = () => {
  companionStore.loadProfiles()
}

watch(
  () => props.visible,
  (newVal) => {
    if (newVal) {
      loadStations()
      companionStore.loadProfiles()
    }
  }
)
</script>
