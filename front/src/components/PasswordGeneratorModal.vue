<template>
  <Dialog
    v-model:visible="visible"
    header="Генератор надежных паролей"
    :modal="true"
    :style="{ width: '440px' }"
  >
    <div class="flex flex-col gap-4 py-2">
      <!-- Generated Password Box -->
      <div class="relative flex items-center bg-slate-100 dark:bg-slate-900 p-3 rounded-lg border border-slate-300 dark:border-slate-700">
        <input
          type="text"
          readonly
          :value="password"
          class="w-full bg-transparent font-mono text-lg font-semibold text-slate-800 dark:text-slate-100 outline-none pr-10 cursor-pointer select-all"
          @click="$event.target.select()"
          title="Нажмите, чтобы выделить"
        />
        <Button
          :icon="isCopied ? 'pi pi-check' : 'pi pi-copy'"
          text
          rounded
          :class="['!absolute right-2 transition-colors', isCopied ? '!text-green-600 dark:!text-green-400' : '']"
          @click="copyPassword"
          :title="isCopied ? 'Скопировано!' : 'Скопировать пароль'"
        />
      </div>

      <!-- Length Slider -->
      <div>
        <div class="flex justify-between items-center mb-1 text-sm font-medium text-slate-700 dark:text-slate-300">
          <span>Длина пароля:</span>
          <span class="font-mono text-blue-600 dark:text-blue-400 font-bold">{{ length }}</span>
        </div>
        <Slider v-model="length" :min="6" :max="32" class="w-full" @change="generate" />
      </div>

      <!-- Character Options -->
      <div class="grid grid-cols-2 gap-2 text-sm text-slate-700 dark:text-slate-300">
        <label class="flex items-center gap-2 cursor-pointer">
          <Checkbox v-model="useUpper" :binary="true" @change="generate" />
          <span>Заглавные (A-Z)</span>
        </label>
        <label class="flex items-center gap-2 cursor-pointer">
          <Checkbox v-model="useLower" :binary="true" @change="generate" />
          <span>Строчные (a-z)</span>
        </label>
        <label class="flex items-center gap-2 cursor-pointer">
          <Checkbox v-model="useDigits" :binary="true" @change="generate" />
          <span>Цифры (0-9)</span>
        </label>
        <label class="flex items-center gap-2 cursor-pointer">
          <Checkbox v-model="useSymbols" :binary="true" @change="generate" />
          <span>Спецсимволы (!@#$)</span>
        </label>
      </div>
    </div>

    <template #footer>
      <div class="flex items-center justify-between w-full gap-2 pt-2">
        <Button
          label="Обновить"
          icon="pi pi-refresh"
          severity="secondary"
          text
          size="small"
          @click="generate"
          title="Сгенерировать другой пароль"
        />

        <div class="flex items-center gap-2">
          <Button
            label="Скопировать"
            :icon="isCopied ? 'pi pi-check' : 'pi pi-copy'"
            severity="secondary"
            outlined
            size="small"
            @click="copyPassword"
          />

          <Button
            v-if="canSelect"
            label="Использовать пароль"
            icon="pi pi-check"
            severity="primary"
            size="small"
            @click="usePassword"
          />

          <Button
            v-else
            label="Скопировать и закрыть"
            icon="pi pi-check"
            severity="primary"
            size="small"
            @click="copyAndClose"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import Slider from 'primevue/slider'
import Checkbox from 'primevue/checkbox'
import { useToast } from 'primevue/usetoast'
import { toolsApi } from '../api/tools'

const props = defineProps({
  modelValue: Boolean,
  canSelect: {
    type: Boolean,
    default: false,
  },
})
const emit = defineEmits(['update:modelValue', 'selected'])

const visible = ref(props.modelValue)
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) generate()
})
watch(visible, (val) => emit('update:modelValue', val))

const length = ref(12)
const useUpper = ref(true)
const useLower = ref(true)
const useDigits = ref(true)
const useSymbols = ref(true)
const password = ref('')
const isCopied = ref(false)
const toast = useToast()

const generate = async () => {
  try {
    const res = await toolsApi.generatePassword({
      length: length.value,
      upper: useUpper.value,
      lower: useLower.value,
      digits: useDigits.value,
      symbols: useSymbols.value,
    })
    password.value = res.data.password
  } catch (e) {
    // Client-side fallback (safe symbols without & to prevent URL/cmd issues)
    let chars = ''
    if (useUpper.value) chars += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if (useLower.value) chars += 'abcdefghijklmnopqrstuvwxyz'
    if (useDigits.value) chars += '0123456789'
    if (useSymbols.value) chars += '!@#$%*()-_=+'
    if (!chars) chars = 'abcdefghijklmnopqrstuvwxyz0123456789'

    let res = ''
    for (let i = 0; i < length.value; i++) {
      res += chars.charAt(Math.floor(Math.random() * chars.length))
    }
    password.value = res
  }
}

/**
 * Robust clipboard copy supporting modern Clipboard API with execCommand fallback.
 */
const copyToClipboard = async (text) => {
  if (!text) return false
  let ok = false

  if (navigator?.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(text)
      ok = true
    } catch (e) {
      console.warn('navigator.clipboard.writeText failed, using execCommand fallback', e)
    }
  }

  if (!ok) {
    try {
      const textArea = document.createElement('textarea')
      textArea.value = text
      textArea.style.position = 'fixed'
      textArea.style.top = '0'
      textArea.style.left = '0'
      textArea.style.width = '2em'
      textArea.style.height = '2em'
      textArea.style.padding = '0'
      textArea.style.border = 'none'
      textArea.style.outline = 'none'
      textArea.style.boxShadow = 'none'
      textArea.style.background = 'transparent'
      document.body.appendChild(textArea)
      textArea.focus()
      textArea.select()
      ok = document.execCommand('copy')
      document.body.removeChild(textArea)
    } catch (err) {
      console.error('Fallback execCommand failed:', err)
      ok = false
    }
  }

  return ok
}

const copyPassword = async () => {
  if (!password.value) return
  const ok = await copyToClipboard(password.value)
  if (ok) {
    isCopied.value = true
    setTimeout(() => {
      isCopied.value = false
    }, 2000)
    toast.add({
      severity: 'success',
      summary: 'Скопировано',
      detail: `Пароль скопирован в буфер обмена`,
      life: 2500,
    })
  } else {
    toast.add({
      severity: 'warn',
      summary: 'Внимание',
      detail: 'Не удалось скопировать автоматически. Выделите пароль и нажмите Ctrl+C',
      life: 4000,
    })
  }
}

const usePassword = async () => {
  if (!password.value) return
  await copyToClipboard(password.value)
  emit('selected', password.value)
  visible.value = false
  toast.add({
    severity: 'success',
    summary: 'Пароль применен',
    detail: 'Пароль подставлен в форму и скопирован в буфер',
    life: 2500,
  })
}

const copyAndClose = async () => {
  await copyPassword()
  emit('selected', password.value)
  visible.value = false
}
</script>
