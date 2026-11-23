<template>
  <div class="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950 transition-colors">
    <Navbar />

    <main class="flex-1 w-full px-4 sm:px-6 lg:px-8 2xl:px-10 py-6 flex flex-col gap-5">
      <!-- Top Action & Search Bar -->
      <div class="bg-white dark:bg-slate-900 rounded-xl shadow-xs border border-slate-200 dark:border-slate-800 p-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 class="text-xl font-bold text-slate-900 dark:text-slate-100 tracking-tight flex items-center gap-2">
            <span>Дистрибутивы iiko Office</span>
            <span class="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-mono">
              {{ distributions.length }} версий
            </span>
          </h1>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Ссылки на скачивание установочных пакетов iiko Office с Яндекс.Диска</p>
        </div>

        <div class="flex flex-wrap items-center gap-3 w-full sm:w-auto">
          <Select
            v-model="selectedType"
            :options="typeFilterOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Все типы"
            class="w-36 text-xs"
            @change="loadDistributions"
          />

          <IconField iconPosition="left" class="w-full sm:w-64">
            <InputIcon class="pi pi-search" />
            <InputText
              v-model="searchQuery"
              placeholder="Поиск по версии (например: 8.4)..."
              class="w-full text-xs"
              @input="onSearchInput"
            />
          </IconField>

          <Button
            v-if="authStore.canEdit"
            label="Добавить версию"
            icon="pi pi-plus"
            severity="primary"
            size="small"
            @click="openAddModal"
          />
        </div>
      </div>

      <!-- Main Table -->
      <div class="bg-white dark:bg-slate-900 rounded-xl shadow-xs border border-slate-200 dark:border-slate-800 overflow-hidden">
        <DataTable
          :value="distributions"
          :loading="loading"
          dataKey="id"
          class="p-datatable-sm"
          stripedRows
          hoverableRows
          responsiveLayout="scroll"
        >
          <template #empty>
            <div class="text-center py-12 text-slate-400 dark:text-slate-500">
              <i class="pi pi-inbox text-4xl mb-2"></i>
              <p>Дистрибутивы не найдены.</p>
            </div>
          </template>

          <Column field="iiko_version" header="Версия iiko" :sortable="true" style="min-width: 160px">
            <template #body="{ data }">
              <div class="flex items-center gap-2">
                <i class="pi pi-box text-blue-600 dark:text-blue-400"></i>
                <span class="font-bold font-mono text-slate-800 dark:text-slate-200 text-sm">{{ data.iiko_version }}</span>
              </div>
            </template>
          </Column>

          <Column field="type" header="Тип" :sortable="true" style="min-width: 120px">
            <template #body="{ data }">
              <Tag
                :value="data.type || 'RMS'"
                :severity="data.type === 'Chain' ? 'help' : (data.type === 'Front' ? 'warn' : 'info')"
                class="!text-[11px]"
              />
            </template>
          </Column>

          <Column field="link_ya" header="Ссылка на Яндекс.Диск" style="min-width: 320px">
            <template #body="{ data }">
              <div class="flex items-center gap-2 font-mono text-xs">
                <QuickCopyBtn :text="data.link_ya" label="Ссылка на Яндекс.Диск">
                  <span class="truncate max-w-xs text-blue-600">{{ data.link_ya }}</span>
                </QuickCopyBtn>
              </div>
            </template>
          </Column>

          <Column header="Действия" style="min-width: 170px; text-align: right">
            <template #body="{ data }">
              <div class="flex items-center justify-end gap-1">
                <Button
                  icon="pi pi-download"
                  label="Скачать"
                  size="small"
                  severity="primary"
                  text
                  @click="downloadLink(data.link_ya)"
                  title="Открыть ссылку на Яндекс.Диск"
                />
                <Button
                  v-if="authStore.canEdit"
                  icon="pi pi-pencil"
                  size="small"
                  severity="secondary"
                  text
                  rounded
                  @click="openEditModal(data)"
                  title="Редактировать дистрибутив"
                />
                <Button
                  v-if="authStore.canEdit"
                  icon="pi pi-trash"
                  size="small"
                  severity="danger"
                  text
                  rounded
                  @click="deleteDist(data)"
                  title="Удалить"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </div>
    </main>

    <!-- Modal to Add / Edit Distribution -->
    <Dialog
      v-model:visible="showModal"
      :header="editingId ? 'Редактировать дистрибутив iiko' : 'Добавить дистрибутив iiko'"
      :modal="true"
      :style="{ width: '480px' }"
    >
      <div class="flex flex-col gap-4 py-2">
        <div>
          <label class="block text-xs font-semibold uppercase text-slate-600 dark:text-slate-300 mb-1">Версия iiko *</label>
          <InputText
            v-model="form.iiko_version"
            placeholder="Например: 8.4.7 или 9.5.8"
            class="w-full font-mono text-sm"
          />
        </div>

        <div>
          <label class="block text-xs font-semibold uppercase text-slate-600 dark:text-slate-300 mb-1">Тип дистрибутива</label>
          <Select
            v-model="form.type"
            :options="typeOptions"
            placeholder="Выберите тип"
            editable
            class="w-full text-sm"
          />
        </div>

        <div>
          <label class="block text-xs font-semibold uppercase text-slate-600 dark:text-slate-300 mb-1">Ссылка на Яндекс.Диск *</label>
          <InputText
            v-model="form.link_ya"
            placeholder="https://disk.yandex.kz/d/..."
            class="w-full font-mono text-sm"
          />
        </div>
      </div>

      <template #footer>
        <div class="flex justify-end gap-2">
          <Button label="Отмена" severity="secondary" text @click="showModal = false" />
          <Button label="Сохранить" icon="pi pi-check" :loading="saving" @click="saveDist" />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import Tag from 'primevue/tag'
import Dialog from 'primevue/dialog'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { useAuthStore } from '../stores/auth'
import { distributionsApi } from '../api/distributions'
import Navbar from '../components/Navbar.vue'
import QuickCopyBtn from '../components/QuickCopyBtn.vue'

const toast = useToast()
const confirm = useConfirm()
const authStore = useAuthStore()

const loading = ref(false)
const distributions = ref([])
const searchQuery = ref('')

const showModal = ref(false)
const saving = ref(false)
const editingId = ref(null)

const selectedType = ref('')
const typeFilterOptions = [
  { label: 'Все типы', value: '' },
  { label: 'RMS', value: 'RMS' },
  { label: 'Chain', value: 'Chain' },
  { label: 'Front', value: 'Front' },
]

const typeOptions = ['RMS', 'Chain', 'Front']

const form = ref({
  iiko_version: '',
  type: 'RMS',
  link_ya: '',
})

let searchTimeout = null
const onSearchInput = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(loadDistributions, 300)
}

const loadDistributions = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchQuery.value.trim()) params.search = searchQuery.value.trim()
    if (selectedType.value) params.type = selectedType.value
    const res = await distributionsApi.getDistributions(params)
    distributions.value = res.data.results || res.data
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Ошибка', detail: 'Не удалось загрузить дистрибутивы', life: 3000 })
  } finally {
    loading.value = false
  }
}

const downloadLink = (link) => {
  if (link) window.open(link, '_blank')
}

const openAddModal = () => {
  editingId.value = null
  form.value = { iiko_version: '', type: 'RMS', link_ya: '' }
  showModal.value = true
}

const openEditModal = (item) => {
  editingId.value = item.id
  form.value = {
    iiko_version: item.iiko_version || '',
    type: item.type || 'RMS',
    link_ya: item.link_ya || '',
  }
  showModal.value = true
}

const saveDist = async () => {
  if (!form.value.iiko_version.trim() || !form.value.link_ya.trim()) {
    toast.add({ severity: 'warn', summary: 'Внимание', detail: 'Заполните обязательные поля', life: 2500 })
    return
  }

  saving.value = true
  try {
    if (editingId.value) {
      await distributionsApi.updateDistribution(editingId.value, form.value)
      toast.add({ severity: 'success', summary: 'Успешно', detail: 'Дистрибутив обновлен', life: 2500 })
    } else {
      await distributionsApi.createDistribution(form.value)
      toast.add({ severity: 'success', summary: 'Успешно', detail: 'Дистрибутив добавлен', life: 2500 })
    }
    showModal.value = false
    loadDistributions()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Ошибка', detail: err.message, life: 3000 })
  } finally {
    saving.value = false
  }
}

const deleteDist = (item) => {
  confirm.require({
    message: `Удалить версию '${item.iiko_version}'?`,
    header: 'Подтверждение удаления',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Удалить',
    rejectLabel: 'Отмена',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await distributionsApi.deleteDistribution(item.id)
        toast.add({ severity: 'success', summary: 'Успешно', detail: 'Версия удалена', life: 2500 })
        loadDistributions()
      } catch (err) {
        toast.add({ severity: 'error', summary: 'Ошибка', detail: err.message, life: 3000 })
      }
    },
  })
}

onMounted(() => {
  loadDistributions()
})
</script>
