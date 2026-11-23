<template>
  <div class="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950 transition-colors">
    <Navbar />

    <main class="flex-1 w-full px-4 sm:px-6 lg:px-8 2xl:px-10 py-6 flex flex-col gap-5">
      <!-- Top Action & Search Bar -->
      <div class="bg-white dark:bg-slate-900 rounded-xl shadow-xs border border-slate-200 dark:border-slate-800 p-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 class="text-xl font-bold text-slate-900 dark:text-slate-100 tracking-tight flex items-center gap-2">
            <span>Реестр подключений AnyDesk</span>
            <span class="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-mono">
              {{ totalCount }} станций
            </span>
          </h1>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Единая база удаленных рабочих мест инженеров по всем заведениям</p>
        </div>

        <div class="flex items-center gap-3 w-full sm:w-auto">
          <!-- Search Bar -->
          <div class="w-full sm:w-72">
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
            class="whitespace-nowrap"
            title="Управление песочницами и версиями AnyDesk"
            @click="showManagementModal = true"
          />
        </div>
      </div>

      <!-- Main AnyDesk Table -->
      <div class="bg-white dark:bg-slate-900 rounded-xl shadow-xs border border-slate-200 dark:border-slate-800 overflow-hidden">
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
            <div class="text-center py-12 text-slate-400">
              <i class="pi pi-desktop text-4xl mb-2"></i>
              <p>Подключения AnyDesk не найдены.</p>
            </div>
          </template>

          <!-- 1. Establishment / City -->
          <Column header="Заведение / Город" style="min-width: 240px">
            <template #body="{ data }">
              <div class="flex flex-col">
                <button
                  type="button"
                  class="text-left font-bold text-blue-600 hover:underline hover:text-blue-800 transition cursor-pointer text-sm"
                  @click="openCompany(data.company)"
                >
                  {{ data.company_place_name || `Заведение #${data.company}` }}
                </button>
                <span class="text-xs text-slate-500 font-medium mt-0.5 flex items-center gap-1">
                  <i class="pi pi-map-marker text-[10px] text-slate-400"></i>
                  {{ data.company_city || 'Город не указан' }}
                </span>
              </div>
            </template>
          </Column>

          <!-- 2. System (iiko or Rosta) -->
          <Column header="Система" style="min-width: 105px">
            <template #body="{ data }">
              <Tag
                :value="data.company_software_type === 'ROSTA' ? 'Rosta' : 'iiko'"
                :severity="data.company_software_type === 'ROSTA' ? 'success' : 'info'"
                class="!text-xs font-bold font-mono !px-2 !py-0.5"
              />
            </template>
          </Column>

          <!-- 3. Workstation Description -->
          <Column field="description" header="Рабочее место" style="min-width: 180px">
            <template #body="{ data }">
              <div class="flex items-center gap-1.5 font-medium text-slate-800 text-sm">
                <i class="pi pi-desktop text-xs text-slate-400 shrink-0"></i>
                <span>{{ data.description || 'Рабочее место' }}</span>
              </div>
            </template>
          </Column>

          <!-- 4. AnyDesk ID -->
          <Column field="anydesk_id" header="AnyDesk ID" style="min-width: 140px">
            <template #body="{ data }">
              <QuickCopyBtn :text="data.anydesk_id" label="AnyDesk ID">
                <span class="font-mono font-bold text-slate-900 text-sm tracking-wide">{{ data.anydesk_id }}</span>
              </QuickCopyBtn>
            </template>
          </Column>

          <!-- 5. Password -->
          <Column field="any_pass" header="Пароль" style="min-width: 130px">
            <template #body="{ data }">
              <QuickCopyBtn v-if="data.any_pass" :text="data.any_pass" label="Пароль AnyDesk">
                <span class="font-mono text-xs">••••••••</span>
              </QuickCopyBtn>
              <span v-else class="text-xs text-slate-400 font-mono italic">без пароля</span>
            </template>
          </Column>

          <!-- 6. Actions -->
          <Column header="Действие" style="min-width: 160px; text-align: right">
            <template #body="{ data }">
              <div class="flex items-center justify-end gap-1">
                <!-- Launch with profile selector modal -->
                <Button
                  icon="pi pi-play"
                  label="Запустить"
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
        <div class="p-3 border-t border-slate-200 flex flex-col md:flex-row justify-between items-center gap-3 text-xs text-slate-600 bg-slate-50">
          <div class="flex items-center gap-3 flex-wrap">
            <span class="whitespace-nowrap font-medium">Показано {{ stations.length }} из {{ totalCount }} подключений</span>
            <div class="flex items-center gap-1.5 border-l border-slate-200 pl-3">
              <span class="text-slate-500 whitespace-nowrap">Показывать по:</span>
              <Select
                v-model="pageSize"
                :options="pageSizeOptions"
                optionLabel="label"
                optionValue="value"
                size="small"
                class="w-24 text-xs bg-white font-medium"
                @change="onPageSizeChange"
              />
            </div>
          </div>

          <!-- Page Navigation with Numbers (1, 2, 3, 4 ... 19) -->
          <div class="flex items-center gap-1 flex-wrap justify-center">
            <!-- First Page Button -->
            <button
              type="button"
              class="w-8 h-8 flex items-center justify-center rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-200 disabled:opacity-30 disabled:pointer-events-none transition cursor-pointer"
              :disabled="currentPage <= 1"
              @click="changePage(1)"
              title="Первая страница"
            >
              <i class="pi pi-angle-double-left text-xs"></i>
            </button>

            <!-- Previous Page Button -->
            <button
              type="button"
              class="w-8 h-8 flex items-center justify-center rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-200 disabled:opacity-30 disabled:pointer-events-none transition cursor-pointer"
              :disabled="currentPage <= 1"
              @click="changePage(currentPage - 1)"
              title="Предыдущая страница"
            >
              <i class="pi pi-chevron-left text-xs"></i>
            </button>

            <!-- Numbered Pages -->
            <template v-for="(p, idx) in visiblePages" :key="idx">
              <span
                v-if="p === '...'"
                class="w-6 h-8 flex items-center justify-center text-slate-400 font-mono select-none"
              >
                ...
              </span>
              <button
                v-else
                type="button"
                @click="changePage(p)"
                class="min-w-8 h-8 px-2 flex items-center justify-center rounded-lg text-xs font-mono font-medium transition cursor-pointer"
                :class="p === currentPage
                  ? 'bg-blue-600 text-white font-bold shadow-xs'
                  : 'text-slate-700 hover:bg-slate-200 hover:text-blue-600'"
              >
                {{ p }}
              </button>
            </template>

            <!-- Next Page Button -->
            <button
              type="button"
              class="w-8 h-8 flex items-center justify-center rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-200 disabled:opacity-30 disabled:pointer-events-none transition cursor-pointer"
              :disabled="currentPage >= totalPages"
              @click="changePage(currentPage + 1)"
              title="Следующая страница"
            >
              <i class="pi pi-chevron-right text-xs"></i>
            </button>

            <!-- Last Page Button -->
            <button
              type="button"
              class="w-8 h-8 flex items-center justify-center rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-200 disabled:opacity-30 disabled:pointer-events-none transition cursor-pointer"
              :disabled="currentPage >= totalPages"
              @click="changePage(totalPages)"
              title="Последняя страница"
            >
              <i class="pi pi-angle-double-right text-xs"></i>
            </button>
          </div>
        </div>
      </div>
    </main>

    <!-- Company Detail Drawer -->
    <CompanyDetailDrawer
      v-model="showCompanyDrawer"
      :company-id="selectedCompanyId"
      @updated="loadStations"
    />

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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
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
import Navbar from '../components/Navbar.vue'
import QuickCopyBtn from '../components/QuickCopyBtn.vue'
import CompanyDetailDrawer from '../components/CompanyDetailDrawer.vue'
import AnydeskVersionSelectModal from '../components/AnydeskVersionSelectModal.vue'
import AnydeskVersionManagementModal from '../components/AnydeskVersionManagementModal.vue'
import AnydeskStationModal from '../components/AnydeskStationModal.vue'

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

const showCompanyDrawer = ref(false)
const selectedCompanyId = ref(null)

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

const openCompany = (companyId) => {
  selectedCompanyId.value = companyId
  showCompanyDrawer.value = true
}

const quickLaunchAnydesk = async (station) => {
  const res = await companionStore.launchAnydesk({
    anydesk_id: station.anydesk_id,
    any_pass: station.any_pass,
  })
  toast.add({
    severity: res.success ? 'success' : 'warn',
    summary: 'AnyDesk',
    detail: res.message,
    life: 3500,
  })
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

onMounted(() => {
  loadStations()
  companionStore.loadProfiles()
})
</script>
