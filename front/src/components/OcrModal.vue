<template>
  <Dialog
    v-model:visible="visible"
    header="Распознавание AnyDesk ID из скриншота (OCR)"
    :modal="true"
    :style="{ width: '520px' }"
  >
    <div class="flex flex-col gap-4 py-2">
      <!-- Dropzone / Paste Area -->
      <div
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="handleDrop"
        @click="triggerFileInput"
        class="border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition flex flex-col items-center justify-center min-h-[160px]"
        :class="isDragging ? 'border-blue-500 bg-blue-50' : 'border-slate-300 hover:border-blue-400 bg-slate-50'"
      >
        <input
          ref="fileInput"
          type="file"
          accept="image/*"
          class="hidden"
          @change="handleFileSelect"
        />

        <div v-if="!imagePreview" class="flex flex-col items-center gap-2 text-slate-500">
          <i class="pi pi-images text-4xl text-slate-400"></i>
          <p class="font-medium text-slate-700">Нажмите для выбора или перетащите скриншот сюда</p>
          <p class="text-xs text-slate-400">Либо сделайте скриншот (Win+Shift+S) и нажмите <kbd class="px-1.5 py-0.5 bg-slate-200 rounded font-mono text-slate-700">Ctrl + V</kbd></p>
        </div>

        <div v-else class="flex flex-col items-center gap-2">
          <img :src="imagePreview" alt="Скриншот" class="max-h-40 rounded shadow-sm object-contain" />
          <Button
            label="Загрузить другой файл"
            icon="pi pi-refresh"
            text
            size="small"
            @click.stop="clearImage"
          />
        </div>
      </div>

      <!-- OCR Progress -->
      <div v-if="isProcessing" class="flex flex-col gap-1 items-center justify-center p-3 bg-blue-50 rounded-lg text-blue-700 text-sm">
        <div class="flex items-center gap-2">
          <i class="pi pi-spin pi-spinner text-lg"></i>
          <span>Распознавание текста (Tesseract.js)... {{ progress }}%</span>
        </div>
        <ProgressBar :value="progress" class="w-full !h-2 mt-1" />
      </div>

      <!-- Extracted Result -->
      <div v-if="recognizedId" class="p-3 bg-emerald-50 border border-emerald-200 rounded-lg flex items-center justify-between">
        <div>
          <div class="text-xs text-emerald-600 font-semibold uppercase">Найден AnyDesk ID:</div>
          <div class="font-mono text-xl font-bold text-emerald-800 tracking-wider">{{ recognizedId }}</div>
        </div>
        <Button
          label="Использовать этот ID"
          icon="pi pi-check"
          severity="success"
          @click="applyId"
        />
      </div>

      <div v-else-if="rawText && !isProcessing" class="p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-800">
        <div class="font-semibold mb-1">Текст распознан, но 9–10 значный AnyDesk ID не найден автоматически:</div>
        <div class="font-mono bg-white p-2 rounded max-h-24 overflow-y-auto whitespace-pre-wrap">{{ rawText }}</div>
      </div>
    </div>

    <template #footer>
      <div class="flex justify-end gap-2">
        <Button label="Отмена" severity="secondary" text @click="visible = false" />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import ProgressBar from 'primevue/progressbar'
import { createWorker } from 'tesseract.js'

const props = defineProps({
  modelValue: Boolean,
})
const emit = defineEmits(['update:modelValue', 'recognized'])

const visible = ref(props.modelValue)
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) clearImage()
})
watch(visible, (val) => emit('update:modelValue', val))

const fileInput = ref(null)
const isDragging = ref(false)
const imagePreview = ref(null)
const isProcessing = ref(false)
const progress = ref(0)
const rawText = ref('')
const recognizedId = ref('')

const triggerFileInput = () => {
  if (fileInput.value) fileInput.value.click()
}

const clearImage = () => {
  imagePreview.value = null
  rawText.value = ''
  recognizedId.value = ''
  progress.value = 0
  isProcessing.value = false
}

const handleFileSelect = (e) => {
  const file = e.target.files[0]
  if (file) processImageFile(file)
}

const handleDrop = (e) => {
  isDragging.value = false
  const file = e.dataTransfer.files[0]
  if (file && file.type.startsWith('image/')) {
    processImageFile(file)
  }
}

// Global Paste Handler for Ctrl+V
const handlePaste = (e) => {
  if (!visible.value) return
  const items = (e.clipboardData || e.originalEvent.clipboardData).items
  for (let item of items) {
    if (item.kind === 'file' && item.type.startsWith('image/')) {
      const file = item.getAsFile()
      processImageFile(file)
      break
    }
  }
}

onMounted(() => {
  window.addEventListener('paste', handlePaste)
})
onUnmounted(() => {
  window.removeEventListener('paste', handlePaste)
})

const processImageFile = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreview.value = e.target.result
    runOcr(e.target.result)
  }
  reader.readAsDataURL(file)
}

const extractAnyDeskId = (text) => {
  if (!text) return ''
  // Pattern 1: 3-3-3 digits (e.g. 493 299 048, 493-299-048)
  const formattedMatch = text.match(/\b(\d{3})[ -](\d{3})[ -](\d{3,4})\b/)
  if (formattedMatch) {
    return formattedMatch[0].replace(/[\s-]/g, '')
  }
  // Pattern 2: 9 to 10 consecutive digits
  const plainMatch = text.match(/\b\d{9,10}\b/)
  if (plainMatch) {
    return plainMatch[0]
  }
  return ''
}

const runOcr = async (imageSource) => {
  isProcessing.value = true
  progress.value = 10
  rawText.value = ''
  recognizedId.value = ''

  try {
    const worker = await createWorker('eng', 1, {
      logger: (m) => {
        if (m.status === 'recognizing text') {
          progress.value = Math.floor(m.progress * 100)
        }
      },
    })

    const ret = await worker.recognize(imageSource)
    await worker.terminate()

    rawText.value = ret.data.text
    recognizedId.value = extractAnyDeskId(ret.data.text)
  } catch (err) {
    console.error('OCR error:', err)
  } finally {
    isProcessing.value = false
  }
}

const applyId = () => {
  if (recognizedId.value) {
    emit('recognized', recognizedId.value)
    visible.value = false
  }
}
</script>
