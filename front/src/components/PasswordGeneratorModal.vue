<template>
  <Dialog
    v-model:visible="visible"
    header="Генератор надежных паролей"
    :modal="true"
    :style="{ width: '420px' }"
  >
    <div class="flex flex-col gap-4 py-2">
      <!-- Generated Password Box -->
      <div class="relative flex items-center bg-slate-100 p-3 rounded-lg border border-slate-300">
        <input
          type="text"
          readonly
          :value="password"
          class="w-full bg-transparent font-mono text-lg font-semibold text-slate-800 outline-none pr-10"
        />
        <Button
          icon="pi pi-copy"
          text
          rounded
          class="!absolute right-2"
          @click="copyPassword"
          title="Скопировать пароль"
        />
      </div>

      <!-- Length Slider -->
      <div>
        <div class="flex justify-between items-center mb-1 text-sm font-medium text-slate-700">
          <span>Длина пароля:</span>
          <span class="font-mono text-blue-600 font-bold">{{ length }}</span>
        </div>
        <Slider v-model="length" :min="6" :max="32" class="w-full" @change="generate" />
      </div>

      <!-- Character Options -->
      <div class="grid grid-cols-2 gap-2 text-sm text-slate-700">
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
      <div class="flex justify-between w-full">
        <Button
          label="Сгенерировать новый"
          icon="pi pi-refresh"
          severity="secondary"
          @click="generate"
        />
        <Button
          label="Скопировать и закрыть"
          icon="pi pi-check"
          @click="copyAndClose"
        />
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
    // Client-side fallback
    let chars = ''
    if (useUpper.value) chars += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if (useLower.value) chars += 'abcdefghijklmnopqrstuvwxyz'
    if (useDigits.value) chars += '0123456789'
    if (useSymbols.value) chars += '!@#$%^&*()'
    if (!chars) chars = 'abcdefghijklmnopqrstuvwxyz0123456789'

    let res = ''
    for (let i = 0; i < length.value; i++) {
      res += chars.charAt(Math.floor(Math.random() * chars.length))
    }
    password.value = res
  }
}

const copyPassword = async () => {
  if (!password.value) return
  await navigator.clipboard.writeText(password.value)
  toast.add({
    severity: 'success',
    summary: 'Пароль скопирован',
    detail: `'${password.value}'`,
    life: 2500,
  })
}

const copyAndClose = async () => {
  await copyPassword()
  emit('selected', password.value)
  visible.value = false
}
</script>
