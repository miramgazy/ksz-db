<template>
  <Dialog
    :visible="visible"
    modal
    dismissableMask
    :style="{ width: '520px', maxWidth: '95vw' }"
    :header="'Загрузка данных WebKassa (CSV)'"
    @update:visible="emit('update:visible', $event)"
  >
    <div class="flex flex-col gap-4 pt-1">
      <!-- Info notice -->
      <div class="p-3 bg-blue-50 dark:bg-blue-950/50 border border-blue-200 dark:border-blue-900 rounded-lg text-xs text-blue-800 dark:text-blue-300 flex items-start gap-2.5">
        <i class="pi pi-info-circle text-base text-blue-600 dark:text-blue-400 mt-0.5 shrink-0"></i>
        <div class="leading-relaxed">
          Загрузите CSV-выгрузку касс. Кассы обновляются по <strong>Заводскому номеру</strong>. При совпадении БИН/ИИН касса автоматически связывается с Юр. лицом или Сетью (Chain).
        </div>
      </div>

      <!-- CTO Selection / Input -->
      <div>
        <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase mb-1">
          Обслуживающее ЦТО *
        </label>
        <div class="flex flex-col gap-1.5">
          <div class="flex items-center gap-2">
            <!-- Dropdown from history -->
            <Select
              v-model="selectedCto"
              :options="ctoOptions"
              placeholder="Выберите из истории ЦТО..."
              class="w-full text-xs font-medium"
              :disabled="loading"
              @change="onCtoSelectChange"
            />
          </div>

          <!-- Or enter new / custom CTO -->
          <div class="relative mt-1">
            <InputText
              v-model="customCto"
              placeholder="Или введите название нового ЦТО (например, ИП-SoftPos)..."
              class="w-full text-xs"
              :disabled="loading"
            />
          </div>
          <span class="text-[11px] text-slate-500 dark:text-slate-400">
            Например: <code class="bg-slate-100 dark:bg-slate-800 px-1 py-0.5 rounded text-blue-600 dark:text-blue-400 cursor-pointer" @click="customCto = 'ИП-SoftPos'">ИП-SoftPos</code>, 
            <code class="bg-slate-100 dark:bg-slate-800 px-1 py-0.5 rounded text-blue-600 dark:text-blue-400 cursor-pointer" @click="customCto = 'ТОО KafeSoft'">ТОО KafeSoft</code>
          </span>
        </div>
      </div>

      <!-- File Select -->
      <div>
        <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase mb-1">
          Файл таблицы (.csv) *
        </label>
        <div
          class="border-2 border-dashed rounded-xl p-5 text-center transition cursor-pointer flex flex-col items-center justify-center gap-2"
          :class="selectedFile
            ? 'border-emerald-400 dark:border-emerald-600 bg-emerald-50/40 dark:bg-emerald-950/20'
            : 'border-slate-300 dark:border-slate-700 hover:border-blue-400 dark:hover:border-blue-500 bg-slate-50 dark:bg-slate-900/50'"
          @click="triggerFileInput"
          @dragover.prevent
          @drop.prevent="onFileDrop"
        >
          <input
            ref="fileInputRef"
            type="file"
            accept=".csv,text/csv"
            class="hidden"
            @change="onFileSelected"
          />

          <div
            class="w-10 h-10 rounded-full flex items-center justify-center text-lg"
            :class="selectedFile ? 'bg-emerald-100 dark:bg-emerald-900/60 text-emerald-600 dark:text-emerald-400' : 'bg-slate-200 dark:bg-slate-800 text-slate-500'"
          >
            <i :class="selectedFile ? 'pi pi-file-excel' : 'pi pi-upload'"></i>
          </div>

          <div v-if="selectedFile" class="text-xs">
            <span class="font-bold text-slate-800 dark:text-slate-100">{{ selectedFile.name }}</span>
            <div class="text-[11px] text-slate-500 mt-0.5">{{ (selectedFile.size / 1024).toFixed(1) }} КБ</div>
          </div>
          <div v-else class="text-xs text-slate-500 dark:text-slate-400">
            <span class="font-semibold text-blue-600 dark:text-blue-400">Нажмите для выбора файла</span> или перетащите сюда
            <div class="text-[10px] text-slate-400 mt-0.5">Поддерживается разделитель ';' (WebKassa экспорт)</div>
          </div>
        </div>
      </div>

      <!-- Result Summary Box -->
      <div v-if="uploadResult" class="p-3 bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800 rounded-lg text-xs flex flex-col gap-1.5">
        <div class="font-bold text-emerald-800 dark:text-emerald-300 flex items-center gap-1.5">
          <i class="pi pi-check-circle text-emerald-600 dark:text-emerald-400"></i>
          Импорт успешно завершен!
        </div>
        <div class="grid grid-cols-2 gap-2 mt-1 text-slate-700 dark:text-slate-300 font-medium">
          <div>Всего обработано: <span class="font-bold">{{ uploadResult.total }}</span></div>
          <div>Новых касс: <span class="font-bold text-emerald-600 dark:text-emerald-400">+{{ uploadResult.created }}</span></div>
          <div>Обновлено касс: <span class="font-bold text-blue-600 dark:text-blue-400">{{ uploadResult.updated }}</span></div>
          <div>Привязано к заведениям: <span class="font-bold text-indigo-600 dark:text-indigo-400">{{ uploadResult.matched }}</span></div>
        </div>
        <div v-if="uploadResult.unmatched > 0" class="text-amber-700 dark:text-amber-400 text-[11px] mt-1">
          Касс без привязки: {{ uploadResult.unmatched }} (можно привязать вручную в таблице)
        </div>
      </div>
    </div>

    <template #footer>
      <div class="flex justify-between items-center w-full">
        <Button
          label="Отмена"
          severity="secondary"
          text
          size="small"
          :disabled="loading"
          @click="emit('update:visible', false)"
        />

        <Button
          label="Загрузить и обновить"
          icon="pi pi-check"
          severity="primary"
          size="small"
          :loading="loading"
          :disabled="!isFormValid || loading"
          @click="submitUpload"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import Select from 'primevue/select'
import InputText from 'primevue/inputtext'
import { useToast } from 'primevue/usetoast'
import { webkassaApi } from '../api/webkassa'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:visible', 'uploaded'])

const toast = useToast()

const loading = ref(false)
const ctoOptions = ref([])
const selectedCto = ref(null)
const customCto = ref('')
const selectedFile = ref(null)
const fileInputRef = ref(null)
const uploadResult = ref(null)

const effectiveCto = computed(() => {
  return customCto.value.trim() || selectedCto.value || ''
})

const isFormValid = computed(() => {
  return !!effectiveCto.value && !!selectedFile.value
})

const loadCtoList = async () => {
  try {
    const res = await webkassaApi.getCtoList()
    ctoOptions.value = res.data || []
    if (!customCto.value && ctoOptions.value.length > 0 && !selectedCto.value) {
      selectedCto.value = ctoOptions.value[0]
    }
  } catch (e) {
    console.error('Ошибка загрузки списка ЦТО:', e)
  }
}

const onCtoSelectChange = () => {
  if (selectedCto.value) {
    customCto.value = selectedCto.value
  }
}

const triggerFileInput = () => {
  if (fileInputRef.value) {
    fileInputRef.value.click()
  }
}

const onFileSelected = (e) => {
  const file = e.target.files?.[0]
  if (file) {
    selectedFile.value = file
    uploadResult.value = null
  }
}

const onFileDrop = (e) => {
  const file = e.dataTransfer.files?.[0]
  if (file) {
    selectedFile.value = file
    uploadResult.value = null
  }
}

const submitUpload = async () => {
  if (!isFormValid.value) return

  loading.value = true
  uploadResult.value = null

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('cto', effectiveCto.value)

    const res = await webkassaApi.uploadCsv(formData)

    uploadResult.value = res.data.stats || res.data
    toast.add({
      severity: 'success',
      summary: 'Успешно',
      detail: res.data.message || 'Файл успешно обработан',
      life: 4000,
    })

    emit('uploaded', uploadResult.value)
    await loadCtoList()
  } catch (err) {
    const msg = err.response?.data?.error || err.message || 'Ошибка загрузки CSV'
    toast.add({
      severity: 'error',
      summary: 'Ошибка импорта',
      detail: msg,
      life: 5000,
    })
  } finally {
    loading.value = false
  }
}

watch(
  () => props.visible,
  (val) => {
    if (val) {
      uploadResult.value = null
      selectedFile.value = null
      loadCtoList()
    }
  }
)
</script>
