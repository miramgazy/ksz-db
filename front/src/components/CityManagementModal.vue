<template>
  <Dialog
    v-model:visible="visible"
    header="Управление списком городов"
    :modal="true"
    :style="{ width: '480px' }"
  >
    <div class="flex flex-col gap-4 py-2">
      <!-- Add New City Form -->
      <div class="flex items-center gap-2 p-3 bg-slate-50 border border-slate-200 rounded-xl">
        <InputText
          v-model="newCityName"
          placeholder="Название нового города (например: Шымкент)"
          class="w-full text-sm"
          @keyup.enter="addCity"
        />
        <Button
          label="Добавить"
          icon="pi pi-plus"
          size="small"
          :loading="adding"
          @click="addCity"
        />
      </div>

      <!-- City List -->
      <div class="flex flex-col gap-1 max-h-72 overflow-y-auto pr-1">
        <div v-if="loading" class="text-center py-6 text-slate-400">
          <i class="pi pi-spin pi-spinner text-2xl"></i>
        </div>

        <div v-else-if="!cities.length" class="text-center py-6 text-slate-400 text-sm">
          Список городов пуст. Добавьте первый город выше.
        </div>

        <div
          v-for="city in cities"
          :key="city.id"
          class="flex items-center justify-between p-2.5 rounded-lg border border-slate-200 hover:bg-slate-50 transition"
        >
          <!-- Editing Mode -->
          <div v-if="editingId === city.id" class="flex items-center gap-2 w-full">
            <InputText v-model="editCityName" class="w-full text-xs" @keyup.enter="saveEditCity(city.id)" />
            <Button icon="pi pi-check" size="small" severity="success" text @click="saveEditCity(city.id)" />
            <Button icon="pi pi-times" size="small" severity="secondary" text @click="editingId = null" />
          </div>

          <!-- Normal Display Mode -->
          <div v-else class="flex items-center justify-between w-full">
            <div class="flex items-center gap-2">
              <i class="pi pi-map-marker text-blue-500 text-xs"></i>
              <span class="text-sm font-semibold text-slate-800">{{ city.name }}</span>
            </div>

            <div class="flex items-center gap-1">
              <Button
                icon="pi pi-pencil"
                size="small"
                severity="secondary"
                text
                rounded
                title="Редактировать название"
                @click="startEditCity(city)"
              />
              <Button
                icon="pi pi-trash"
                size="small"
                severity="danger"
                text
                rounded
                title="Удалить город"
                @click="deleteCity(city)"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="flex justify-end">
        <Button label="Закрыть" severity="secondary" text @click="visible = false" />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { citiesApi } from '../api/cities'

const props = defineProps({
  modelValue: Boolean,
})
const emit = defineEmits(['update:modelValue', 'updated'])

const toast = useToast()
const confirm = useConfirm()

const visible = ref(props.modelValue)
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) loadCities()
})
watch(visible, (val) => emit('update:modelValue', val))

const loading = ref(false)
const adding = ref(false)
const cities = ref([])
const newCityName = ref('')

const editingId = ref(null)
const editCityName = ref('')

const loadCities = async () => {
  loading.value = true
  try {
    const res = await citiesApi.getCities({ page_size: 200 })
    cities.value = res.data.results || res.data
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Ошибка', detail: 'Не удалось загрузить города', life: 2500 })
  } finally {
    loading.value = false
  }
}

const addCity = async () => {
  const name = newCityName.value.trim()
  if (!name) return

  adding.value = true
  try {
    await citiesApi.createCity(name)
    toast.add({ severity: 'success', summary: 'Успешно', detail: `Город '${name}' добавлен`, life: 2500 })
    newCityName.value = ''
    await loadCities()
    emit('updated')
  } catch (err) {
    const detail = err.response?.data?.name?.[0] || err.message || 'Ошибка добавления города'
    toast.add({ severity: 'error', summary: 'Ошибка', detail, life: 3000 })
  } finally {
    adding.value = false
  }
}

const startEditCity = (city) => {
  editingId.value = city.id
  editCityName.value = city.name
}

const saveEditCity = async (id) => {
  const name = editCityName.value.trim()
  if (!name) return

  try {
    await citiesApi.updateCity(id, name)
    toast.add({ severity: 'success', summary: 'Успешно', detail: 'Название города обновлено', life: 2500 })
    editingId.value = null
    await loadCities()
    emit('updated')
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Ошибка', detail: err.message, life: 3000 })
  }
}

const deleteCity = (city) => {
  confirm.require({
    message: `Удалить город '${city.name}'?`,
    header: 'Подтверждение',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Удалить',
    rejectLabel: 'Отмена',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await citiesApi.deleteCity(city.id)
        toast.add({ severity: 'success', summary: 'Успешно', detail: 'Город удален', life: 2500 })
        await loadCities()
        emit('updated')
      } catch (err) {
        toast.add({ severity: 'error', summary: 'Ошибка', detail: err.message, life: 3000 })
      }
    },
  })
}
</script>
