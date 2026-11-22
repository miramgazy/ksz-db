<template>
  <Dialog
    v-model:visible="visible"
    header="Управление профилями AnyDesk и Sandboxie"
    :modal="true"
    :style="{ width: '680px' }"
  >
    <div class="flex flex-col gap-4 py-2">
      <!-- Add / Edit Profile Form Card -->
      <div class="p-3.5 bg-slate-50 border border-slate-200 rounded-xl flex flex-col gap-3">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold uppercase text-slate-700 tracking-wider">
            {{ editingId ? 'Редактирование профиля' : 'Добавить новый профиль AnyDesk' }}
          </span>
          <Button
            v-if="editingId"
            label="Отмена редактирования"
            size="small"
            severity="secondary"
            text
            class="!text-xs !p-0"
            @click="cancelEdit"
          />
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
          <!-- Profile Name -->
          <div>
            <label class="block font-semibold text-slate-600 mb-1">Название профиля *</label>
            <InputText
              v-model="form.name"
              placeholder="Например: Miram - 4 или Портативный"
              class="w-full text-xs"
            />
          </div>

          <!-- Sandbox Toggle -->
          <div>
            <label class="block font-semibold text-slate-600 mb-1">Режим запуска</label>
            <div class="flex items-center gap-3 h-8">
              <Checkbox v-model="form.is_sandbox" :binary="true" inputId="is_sb" />
              <label for="is_sb" class="cursor-pointer select-none font-medium text-slate-800">
                Песочница Sandboxie-Plus
              </label>
            </div>
          </div>

          <!-- Exe Path -->
          <div class="sm:col-span-2">
            <label class="block font-semibold text-slate-600 mb-1">Путь к файлу AnyDesk.exe *</label>
            <InputText
              v-model="form.exe_path"
              placeholder="C:\Program Files (x86)\AnyDesk\AnyDesk.exe или путь к портативной версии"
              class="w-full font-mono text-xs"
            />
          </div>

          <!-- Sandbox Params if IsSandbox -->
          <div v-if="form.is_sandbox" class="sm:col-span-2 bg-purple-50/70 p-2.5 rounded-lg border border-purple-200">
            <label class="block font-semibold text-purple-900 mb-1">
              Параметры бокса Sandboxie (/box:ИмяБокса) *
            </label>
            <InputText
              v-model="form.sandbox_params"
              placeholder="/box:AnyDesk_M4 или /box:AnyDesk_N24"
              class="w-full font-mono text-xs bg-white"
            />
            <span class="text-[11px] text-purple-600 mt-1 block">
              Имя изолированной песочницы в программе Sandboxie-Plus (например: <code>/box:AnyDesk_M1</code>)
            </span>
          </div>
        </div>

        <div class="flex justify-end gap-2 pt-1 border-t border-slate-200/60">
          <Button
            :label="editingId ? 'Сохранить изменения' : 'Добавить профиль'"
            icon="pi pi-check"
            size="small"
            severity="primary"
            :loading="saving"
            @click="saveProfile"
          />
        </div>
      </div>

      <!-- Profiles List -->
      <div class="flex flex-col gap-1 max-h-72 overflow-y-auto pr-1">
        <div v-if="loading" class="text-center py-6 text-slate-400">
          <i class="pi pi-spin pi-spinner text-2xl"></i>
        </div>

        <div v-else-if="!profiles.length" class="text-center py-6 text-slate-400 text-sm">
          Список профилей пуст. Добавьте первый профиль выше.
        </div>

        <div
          v-for="item in profiles"
          :key="item.id"
          class="flex items-center justify-between p-2.5 rounded-lg border border-slate-200 hover:bg-slate-50 transition"
        >
          <div class="flex items-center gap-3">
            <div
              class="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold"
              :class="item.is_sandbox ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'"
            >
              <i :class="item.is_sandbox ? 'pi pi-shield' : 'pi pi-desktop'"></i>
            </div>

            <div class="flex flex-col">
              <div class="flex items-center gap-2">
                <span class="text-sm font-bold text-slate-800">{{ item.name }}</span>
                <Tag
                  v-if="item.is_sandbox"
                  :value="item.sandbox_params || 'Sandbox'"
                  severity="help"
                  class="!text-[10px] !px-1.5 !py-0.2"
                />
                <Tag
                  v-else
                  value="Direct"
                  severity="info"
                  class="!text-[10px] !px-1.5 !py-0.2"
                />
              </div>
              <span class="text-[11px] text-slate-400 font-mono truncate max-w-md">
                {{ item.exe_path }}
              </span>
            </div>
          </div>

          <div class="flex items-center gap-1">
            <Button
              icon="pi pi-pencil"
              size="small"
              severity="secondary"
              text
              rounded
              title="Редактировать профиль"
              @click="startEdit(item)"
            />
            <Button
              icon="pi pi-trash"
              size="small"
              severity="danger"
              text
              rounded
              title="Удалить профиль"
              @click="deleteProfile(item)"
            />
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
import Checkbox from 'primevue/checkbox'
import Tag from 'primevue/tag'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { anydeskVersionsApi } from '../api/anydeskVersions'

const props = defineProps({
  modelValue: Boolean,
})
const emit = defineEmits(['update:modelValue', 'updated'])

const toast = useToast()
const confirm = useConfirm()

const visible = ref(props.modelValue)
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    cancelEdit()
    loadProfiles()
  }
})
watch(visible, (val) => emit('update:modelValue', val))

const loading = ref(false)
const saving = ref(false)
const profiles = ref([])
const editingId = ref(null)

const defaultForm = () => ({
  name: '',
  exe_path: 'C:\\Program Files (x86)\\AnyDesk\\AnyDesk.exe',
  is_sandbox: false,
  sandbox_params: '',
  is_default: false,
})

const form = ref(defaultForm())

const loadProfiles = async () => {
  loading.value = true
  try {
    const res = await anydeskVersionsApi.getVersions({ page_size: 100 })
    profiles.value = res.data.results || res.data
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Ошибка', detail: 'Не удалось загрузить профили', life: 2500 })
  } finally {
    loading.value = false
  }
}

const startEdit = (item) => {
  editingId.value = item.id
  form.value = {
    name: item.name || '',
    exe_path: item.exe_path || 'C:\\Program Files (x86)\\AnyDesk\\AnyDesk.exe',
    is_sandbox: Boolean(item.is_sandbox),
    sandbox_params: item.sandbox_params || '',
    is_default: Boolean(item.is_default),
  }
}

const cancelEdit = () => {
  editingId.value = null
  form.value = defaultForm()
}

const saveProfile = async () => {
  if (!form.value.name.trim()) {
    toast.add({ severity: 'warn', summary: 'Внимание', detail: 'Укажите название профиля', life: 2500 })
    return
  }

  saving.value = true
  try {
    if (editingId.value) {
      await anydeskVersionsApi.updateVersion(editingId.value, form.value)
      toast.add({ severity: 'success', summary: 'Успешно', detail: 'Профиль обновлен', life: 2000 })
    } else {
      await anydeskVersionsApi.createVersion(form.value)
      toast.add({ severity: 'success', summary: 'Успешно', detail: 'Профиль добавлен', life: 2000 })
    }
    cancelEdit()
    await loadProfiles()
    emit('updated')
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Ошибка', detail: err.message, life: 3000 })
  } finally {
    saving.value = false
  }
}

const deleteProfile = (item) => {
  confirm.require({
    message: `Удалить профиль AnyDesk '${item.name}'?`,
    header: 'Подтверждение удаления',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Удалить',
    rejectLabel: 'Отмена',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await anydeskVersionsApi.deleteVersion(item.id)
        toast.add({ severity: 'success', summary: 'Успешно', detail: 'Профиль удален', life: 2000 })
        if (editingId.value === item.id) cancelEdit()
        await loadProfiles()
        emit('updated')
      } catch (err) {
        toast.add({ severity: 'error', summary: 'Ошибка', detail: err.message, life: 3000 })
      }
    },
  })
}
</script>
