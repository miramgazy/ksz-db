<template>
  <Dialog
    v-model:visible="visible"
    :header="isEdit ? 'Редактировать подключение AnyDesk' : 'Добавить подключение AnyDesk'"
    :modal="true"
    :style="{ width: '480px' }"
  >
    <div class="flex flex-col gap-4 py-2">
      <!-- Description -->
      <div>
        <label class="block text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase mb-1">
          Описание рабочего места / ПК <span class="text-rose-500">*</span>
        </label>
        <InputText
          v-model="form.description"
          placeholder="Например: Сервер, Касса 1, Бар, Ресепшн"
          class="w-full"
        />
      </div>

      <!-- AnyDesk ID with OCR trigger -->
      <div>
        <div class="flex justify-between items-center mb-1">
          <label class="block text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase">
            AnyDesk ID <span class="text-rose-500">*</span>
          </label>
          <Button
            label="Распознать из скриншота (OCR)"
            icon="pi pi-camera"
            text
            size="small"
            class="!p-0 !text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800"
            @click="showOcr = true"
          />
        </div>
        <InputText
          v-model="form.anydesk_id"
          placeholder="9 или 10 цифр (например: 794855272)"
          class="w-full font-mono text-base"
        />
      </div>

      <!-- AnyDesk Password with generator trigger -->
      <div>
        <div class="flex justify-between items-center mb-1">
          <label class="block text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase">
            Пароль неконтролируемого доступа
          </label>
          <Button
            label="Сгенерировать пароль"
            icon="pi pi-key"
            text
            size="small"
            class="!p-0 !text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800"
            @click="showPassGen = true"
          />
        </div>
        <InputText
          v-model="form.any_pass"
          placeholder="Пароль для прямого подключения"
          class="w-full font-mono text-base"
        />
      </div>
    </div>

    <template #footer>
      <div class="flex justify-end gap-2">
        <Button label="Отмена" severity="secondary" text @click="visible = false" />
        <Button
          :label="isEdit ? 'Сохранить' : 'Добавить'"
          icon="pi pi-check"
          :loading="saving"
          @click="save"
        />
      </div>
    </template>

    <!-- Sub-modals -->
    <OcrModal v-model="showOcr" @recognized="(id) => form.anydesk_id = id" />
    <PasswordGeneratorModal v-model="showPassGen" :can-select="true" @selected="(p) => form.any_pass = p" />
  </Dialog>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import { useToast } from 'primevue/usetoast'
import OcrModal from './OcrModal.vue'
import PasswordGeneratorModal from './PasswordGeneratorModal.vue'
import { anydeskApi } from '../api/anydesk'

const props = defineProps({
  modelValue: Boolean,
  companyId: [Number, String],
  station: Object,
})
const emit = defineEmits(['update:modelValue', 'saved'])

const toast = useToast()
const visible = ref(props.modelValue)
watch(() => props.modelValue, (val) => visible.value = val)
watch(visible, (val) => emit('update:modelValue', val))

const isEdit = computed(() => !!props.station?.id)
const saving = ref(false)
const showOcr = ref(false)
const showPassGen = ref(false)

const form = ref({
  description: '',
  anydesk_id: '',
  any_pass: '',
})

watch(() => props.station, (st) => {
  if (st) {
    form.value = {
      description: st.description || '',
      anydesk_id: st.anydesk_id || '',
      any_pass: st.any_pass || '',
    }
  } else {
    form.value = {
      description: '',
      anydesk_id: '',
      any_pass: '',
    }
  }
}, { immediate: true })

const save = async () => {
  if (!form.value.description.trim()) {
    toast.add({ severity: 'warn', summary: 'Ошибка', detail: 'Укажите описание рабочего места.', life: 3000 })
    return
  }
  if (!form.value.anydesk_id.trim()) {
    toast.add({ severity: 'warn', summary: 'Ошибка', detail: 'Укажите AnyDesk ID.', life: 3000 })
    return
  }

  saving.value = true
  try {
    const payload = {
      ...form.value,
      company: props.companyId,
    }

    if (isEdit.value) {
      await anydeskApi.updateAnydeskStation(props.station.id, payload)
      toast.add({ severity: 'success', summary: 'Успешно', detail: 'Подключение AnyDesk обновлено.', life: 3000 })
    } else {
      await anydeskApi.createAnydeskStation(payload)
      toast.add({ severity: 'success', summary: 'Успешно', detail: 'Подключение AnyDesk добавлено.', life: 3000 })
    }
    emit('saved')
    visible.value = false
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Ошибка сохранения', detail: err.message, life: 4000 })
  } finally {
    saving.value = false
  }
}
</script>
