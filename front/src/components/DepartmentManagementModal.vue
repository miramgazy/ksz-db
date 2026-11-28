<template>
  <Dialog
    v-model:visible="visible"
    header="Управление департаментами"
    :modal="true"
    :style="{ width: '500px' }"
  >
    <div class="flex flex-col gap-4 py-2">
      <!-- Add New Department Form -->
      <div class="flex items-center gap-2 p-3 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl">
        <InputText
          v-model="newDepartmentName"
          placeholder="Название нового департамента (например: Восток)"
          class="w-full text-sm"
          @keyup.enter="addDepartment"
        />
        <Button
          label="Добавить"
          icon="pi pi-plus"
          size="small"
          :loading="adding"
          @click="addDepartment"
        />
      </div>

      <!-- Departments List -->
      <div class="flex flex-col gap-1 max-h-72 overflow-y-auto pr-1">
        <div v-if="loading" class="text-center py-6 text-slate-400 dark:text-slate-500">
          <i class="pi pi-spin pi-spinner text-2xl"></i>
        </div>

        <div v-else-if="!departments.length" class="text-center py-6 text-slate-400 dark:text-slate-500 text-sm">
          Список департаментов пуст. Добавьте первый департамент выше.
        </div>

        <div
          v-for="item in departments"
          :key="item.id"
          class="flex items-center justify-between p-2.5 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800/60 transition"
        >
          <!-- Editing Mode -->
          <div v-if="editingId === item.id" class="flex items-center gap-2 w-full">
            <InputText v-model="editDepartmentName" class="w-full text-xs" @keyup.enter="saveEditDepartment(item.id)" />
            <Button icon="pi pi-check" size="small" severity="success" text @click="saveEditDepartment(item.id)" />
            <Button icon="pi pi-times" size="small" severity="secondary" text @click="editingId = null" />
          </div>

          <!-- Normal Display Mode -->
          <div v-else class="flex items-center justify-between w-full">
            <div class="flex items-center gap-2">
              <i class="pi pi-compass text-blue-500 dark:text-blue-400 text-xs"></i>
              <span class="text-sm font-semibold text-slate-800 dark:text-slate-100">{{ item.name }}</span>
            </div>

            <div class="flex items-center gap-1">
              <Button
                icon="pi pi-pencil"
                size="small"
                severity="secondary"
                text
                rounded
                title="Редактировать название"
                @click="startEditDepartment(item)"
              />
              <Button
                icon="pi pi-trash"
                size="small"
                severity="danger"
                text
                rounded
                title="Удалить департамент"
                @click="deleteDepartment(item)"
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
import { departmentsApi } from '../api/departments'

const props = defineProps({
  modelValue: Boolean,
})
const emit = defineEmits(['update:modelValue', 'updated'])

const toast = useToast()
const confirm = useConfirm()

const visible = ref(props.modelValue)
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) loadDepartments()
})
watch(visible, (val) => emit('update:modelValue', val))

const loading = ref(false)
const adding = ref(false)
const departments = ref([])
const newDepartmentName = ref('')

const editingId = ref(null)
const editDepartmentName = ref('')

const loadDepartments = async () => {
  loading.value = true
  try {
    const res = await departmentsApi.getDepartments({ page_size: 200 })
    departments.value = res.data.results || res.data
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Ошибка', detail: 'Не удалось загрузить департаменты', life: 2500 })
  } finally {
    loading.value = false
  }
}

const addDepartment = async () => {
  const name = newDepartmentName.value.trim()
  if (!name) return

  adding.value = true
  try {
    await departmentsApi.createDepartment({ name })
    toast.add({ severity: 'success', summary: 'Успешно', detail: `Департамент '${name}' добавлен`, life: 2500 })
    newDepartmentName.value = ''
    await loadDepartments()
    emit('updated')
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Ошибка', detail: err.message, life: 3000 })
  } finally {
    adding.value = false
  }
}

const startEditDepartment = (item) => {
  editingId.value = item.id
  editDepartmentName.value = item.name
}

const saveEditDepartment = async (id) => {
  const name = editDepartmentName.value.trim()
  if (!name) return

  try {
    await departmentsApi.updateDepartment(id, { name })
    toast.add({ severity: 'success', summary: 'Успешно', detail: 'Департамент обновлен', life: 2000 })
    editingId.value = null
    await loadDepartments()
    emit('updated')
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Ошибка', detail: err.message, life: 3000 })
  }
}

const deleteDepartment = (item) => {
  confirm.require({
    message: `Удалить департамент '${item.name}'?`,
    header: 'Подтверждение удаления',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Удалить',
    rejectLabel: 'Отмена',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await departmentsApi.deleteDepartment(item.id)
        toast.add({ severity: 'success', summary: 'Успешно', detail: 'Департамент удален', life: 2000 })
        await loadDepartments()
        emit('updated')
      } catch (err) {
        toast.add({ severity: 'error', summary: 'Ошибка', detail: err.message, life: 3000 })
      }
    },
  })
}
</script>
