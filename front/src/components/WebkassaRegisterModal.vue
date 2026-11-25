<template>
  <Dialog
    :visible="visible"
    modal
    dismissableMask
    :style="{ width: '600px', maxWidth: '95vw' }"
    :header="register?.serial_number ? `Касса ${register.serial_number}` : 'Информация о кассе'"
    @update:visible="emit('update:visible', $event)"
  >
    <div v-if="register" class="flex flex-col gap-4 text-xs">
      <!-- Top info block -->
      <div class="grid grid-cols-2 gap-2.5 p-3 bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 rounded-lg">
        <div>
          <span class="text-slate-400 dark:text-slate-500 font-medium">Название кассы:</span>
          <div class="font-bold text-slate-800 dark:text-slate-100 text-sm mt-0.5">{{ register.name || '—' }}</div>
        </div>

        <div>
          <span class="text-slate-400 dark:text-slate-500 font-medium">SWK Номер:</span>
          <div class="font-mono font-bold text-blue-600 dark:text-blue-400 text-sm mt-0.5 flex items-center gap-1.5">
            <span>{{ register.serial_number }}</span>
            <QuickCopyBtn :text="register.serial_number" label="SWK Номер" />
          </div>
        </div>

        <div>
          <span class="text-slate-400 dark:text-slate-500 font-medium">ЦТО:</span>
          <div class="font-semibold text-slate-700 dark:text-slate-300 mt-0.5">{{ register.cto || 'Не указано' }}</div>
        </div>

        <div>
          <span class="text-slate-400 dark:text-slate-500 font-medium">Статус:</span>
          <div class="mt-0.5">
            <Tag
              :value="register.status || 'Неизвестно'"
              :severity="register.status === 'Готова к работе' ? 'success' : 'danger'"
              class="!text-[11px] !px-2 !py-0.5 font-bold"
            />
          </div>
        </div>

        <div>
          <span class="text-slate-400 dark:text-slate-500 font-medium">ОФД:</span>
          <div class="font-medium text-slate-700 dark:text-slate-300 mt-0.5">{{ register.ofd || '—' }}</div>
        </div>

        <div>
          <span class="text-slate-400 dark:text-slate-500 font-medium">Срок действия:</span>
          <div class="font-bold mt-0.5 flex items-center gap-1.5" :class="expirationColorClass">
            <i class="pi pi-calendar text-xs"></i>
            <span>{{ formatDate(register.expires_at) }}</span>
            <span class="text-[10px] font-mono font-normal">({{ formatDaysRemaining(register.days_remaining) }})</span>
          </div>
        </div>

        <div class="col-span-2 pt-1 border-t border-slate-200 dark:border-slate-800">
          <span class="text-slate-400 dark:text-slate-500 font-medium">Организация (БИН):</span>
          <div class="font-medium text-slate-800 dark:text-slate-200 mt-0.5 flex items-center justify-between gap-2">
            <span>{{ register.organization || '—' }}</span>
            <span v-if="register.bin_iin" class="font-mono text-xs font-bold text-slate-600 dark:text-slate-300 bg-slate-200 dark:bg-slate-800 px-1.5 py-0.5 rounded">
              БИН: {{ register.bin_iin }}
            </span>
          </div>
        </div>

        <!-- Active / Inactive Status Toggle -->
        <div class="col-span-2 pt-2 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between">
          <div class="flex items-center gap-2">
            <Checkbox v-model="editIsActive" :binary="true" inputId="reg_is_active_cb" />
            <label for="reg_is_active_cb" class="font-bold text-slate-800 dark:text-slate-200 cursor-pointer text-xs select-none">
              Активная касса
            </label>
          </div>
          <Tag
            :value="editIsActive ? 'Активна' : 'Не активна'"
            :severity="editIsActive ? 'success' : 'secondary'"
            class="!text-[11px] !px-2 !py-0.5 font-bold"
          />
        </div>
      </div>

      <!-- Company Assignment Section -->
      <div class="p-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg flex flex-col gap-3">
        <div class="flex items-center justify-between">
          <span class="font-bold text-slate-800 dark:text-slate-200 text-xs uppercase tracking-wide flex items-center gap-1.5">
            <i class="pi pi-building text-blue-600 dark:text-blue-400"></i>
            Привязка к заведению / сети
          </span>
          <span
            v-if="register.auto_matched && register.company"
            class="text-[10px] font-semibold text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-200 dark:border-emerald-800"
          >
            Автоматически по БИН
          </span>
        </div>

        <!-- Currently linked company preview -->
        <div v-if="selectedCompany" class="p-2.5 bg-blue-50/60 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-900 rounded-lg flex items-center justify-between gap-3">
          <div class="flex flex-col min-w-0">
            <div class="font-bold text-blue-700 dark:text-blue-300 text-sm truncate flex items-center gap-1.5">
              <span>{{ selectedCompany.place_name }}</span>
              <Tag
                v-if="selectedCompany.node_type === 'CHAIN'"
                value="Сеть (Chain)"
                severity="warn"
                class="!text-[9px] !px-1.5 font-bold"
              />
            </div>
            <div class="text-[11px] text-slate-600 dark:text-slate-400 mt-0.5">
              {{ selectedCompany.company_name || 'Без юр. лица' }} • {{ selectedCompany.city || 'Город не указан' }}
              <span v-if="selectedCompany.bin" class="font-mono ml-1 font-semibold text-slate-700 dark:text-slate-300">(БИН: {{ selectedCompany.bin }})</span>
            </div>
          </div>

          <Button
            icon="pi pi-times"
            severity="danger"
            text
            rounded
            size="small"
            title="Отвязать заведение"
            @click="unlinkCompany"
          />
        </div>

        <div v-else class="text-slate-400 italic text-[11px]">
          Касса не привязана ни к одному заведению. Выберите заведение ниже для привязки.
        </div>

        <!-- Company Search / Selection -->
        <div class="flex flex-col gap-1.5">
          <label class="font-semibold text-slate-700 dark:text-slate-300 text-[11px]">
            {{ selectedCompany ? 'Сменить заведение:' : 'Найти и привязать заведение:' }}
          </label>
          <div class="relative">
            <IconField iconPosition="left" class="w-full">
              <InputIcon class="pi pi-search text-xs text-slate-400" />
              <InputText
                v-model="companySearchQuery"
                placeholder="Поиск заведения по названию, юр. лицу, БИН или городу..."
                class="w-full text-xs"
                @input="onSearchCompanies"
              />
            </IconField>
          </div>

          <!-- Search Results List -->
          <div
            v-if="companyResults.length > 0"
            class="max-h-40 overflow-y-auto border border-slate-200 dark:border-slate-700 rounded-lg divide-y divide-slate-100 dark:divide-slate-800 bg-white dark:bg-slate-900 shadow-sm mt-1"
          >
            <div
              v-for="c in companyResults"
              :key="c.id"
              class="p-2 hover:bg-slate-100 dark:hover:bg-slate-800/80 cursor-pointer transition flex items-center justify-between gap-2"
              @click="selectCompany(c)"
            >
              <div class="flex flex-col min-w-0">
                <span class="font-bold text-slate-800 dark:text-slate-100 truncate flex items-center gap-1.5">
                  {{ c.place_name }}
                  <span v-if="c.node_type === 'CHAIN'" class="text-[9px] bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300 px-1 rounded font-bold">Сеть</span>
                </span>
                <span class="text-[10px] text-slate-500 truncate">
                  {{ c.company_name || '—' }} • {{ c.city || '—' }} <span v-if="c.bin" class="font-mono font-semibold">(БИН: {{ c.bin }})</span>
                </span>
              </div>
              <Button
                label="Выбрать"
                icon="pi pi-check"
                size="small"
                severity="primary"
                text
                class="!text-xs !py-1 !px-2 shrink-0"
              />
            </div>
          </div>

          <!-- Save BIN to Company Checkbox -->
          <div v-if="selectedCompany && register.bin_iin && selectedCompany.bin !== register.bin_iin" class="flex items-center gap-2 mt-1 p-2 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 rounded">
            <input
              type="checkbox"
              id="syncBinCheckbox"
              v-model="syncBinToCompany"
              class="rounded border-amber-400 text-blue-600 focus:ring-blue-500 cursor-pointer"
            />
            <label for="syncBinCheckbox" class="text-[11px] text-amber-900 dark:text-amber-300 cursor-pointer">
              Записать БИН кассы (<strong>{{ register.bin_iin }}</strong>) в карточку заведения <strong>«{{ selectedCompany.place_name }}»</strong>
            </label>
          </div>
        </div>
      </div>

      <!-- Comment Section -->
      <div>
        <label class="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase mb-1">
          Примечание инженера
        </label>
        <textarea
          v-model="editComment"
          rows="2"
          placeholder="Произвольный комментарий к кассе..."
          class="w-full text-xs p-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-100 focus:outline-hidden focus:ring-1 focus:ring-blue-500"
        ></textarea>
      </div>
    </div>

    <template #footer>
      <div class="flex justify-between items-center w-full">
        <Button
          label="Отмена"
          severity="secondary"
          text
          size="small"
          :disabled="saving"
          @click="emit('update:visible', false)"
        />

        <Button
          label="Сохранить изменения"
          icon="pi pi-check"
          severity="primary"
          size="small"
          :loading="saving"
          @click="saveChanges"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import Tag from 'primevue/tag'
import Checkbox from 'primevue/checkbox'
import { useToast } from 'primevue/usetoast'
import QuickCopyBtn from './QuickCopyBtn.vue'
import { webkassaApi } from '../api/webkassa'
import { companiesApi } from '../api/companies'
import { formatDate, formatDaysRemaining } from '../utils/expiration'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
  register: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['update:visible', 'saved'])

const toast = useToast()

const saving = ref(false)
const selectedCompany = ref(null)
const editComment = ref('')
const editIsActive = ref(true)
const syncBinToCompany = ref(true)

const companySearchQuery = ref('')
const companyResults = ref([])
let searchTimeout = null

const expirationColorClass = computed(() => {
  const days = props.register?.days_remaining
  if (days === null || days === undefined) return 'text-slate-500'
  if (days < 0) return 'text-rose-600 dark:text-rose-400 font-bold'
  if (days <= 3) return 'text-orange-600 dark:text-orange-400 font-bold'
  if (days <= 7) return 'text-amber-600 dark:text-amber-400 font-semibold'
  if (days <= 30) return 'text-blue-600 dark:text-blue-400'
  return 'text-emerald-600 dark:text-emerald-400'
})

const onSearchCompanies = () => {
  clearTimeout(searchTimeout)
  const q = companySearchQuery.value.trim()
  if (!q) {
    companyResults.value = []
    return
  }
  searchTimeout = setTimeout(async () => {
    try {
      const res = await companiesApi.getCompanies({ search: q, page_size: 10 })
      companyResults.value = res.data?.results || res.data || []
    } catch (e) {
      console.error('Ошибка поиска заведений:', e)
    }
  }, 300)
}

const selectCompany = (c) => {
  selectedCompany.value = c
  companySearchQuery.value = ''
  companyResults.value = []
}

const unlinkCompany = () => {
  selectedCompany.value = null
}

const saveChanges = async () => {
  if (!props.register?.id) return

  saving.value = true
  try {
    const payload = {
      company: selectedCompany.value ? selectedCompany.value.id : null,
      comment: editComment.value.trim(),
      is_active: editIsActive.value,
    }

    await webkassaApi.updateRegister(props.register.id, payload)

    // Если запрошена синхронизация БИН в карточку заведения
    if (
      syncBinToCompany.value &&
      selectedCompany.value &&
      props.register.bin_iin &&
      selectedCompany.value.bin !== props.register.bin_iin
    ) {
      try {
        await companiesApi.updateCompany(selectedCompany.value.id, {
          bin: props.register.bin_iin,
        })
      } catch (e) {
        console.warn('Не удалось обновить БИН в компании:', e)
      }
    }

    toast.add({
      severity: 'success',
      summary: 'Сохранено',
      detail: 'Данные кассы успешно обновлены',
      life: 2500,
    })

    emit('saved')
    emit('update:visible', false)
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Ошибка сохранения',
      detail: err.message || 'Не удалось сохранить изменения',
      life: 3500,
    })
  } finally {
    saving.value = false
  }
}

watch(
  () => props.register,
  (reg) => {
    if (reg) {
      editComment.value = reg.comment || ''
      editIsActive.value = reg.is_active !== undefined ? reg.is_active : true
      companySearchQuery.value = ''
      companyResults.value = []
      syncBinToCompany.value = true

      if (reg.company) {
        selectedCompany.value = {
          id: reg.company,
          place_name: reg.company_place_name,
          company_name: reg.company_name,
          city: reg.company_city,
          software_type: reg.company_software_type,
          node_type: reg.company_node_type,
          bin: reg.company_bin,
        }
      } else {
        selectedCompany.value = null
      }
    }
  },
  { immediate: true }
)
</script>
