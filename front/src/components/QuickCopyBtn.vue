<template>
  <button
    type="button"
    @click.stop="copy"
    :title="title || 'Нажмите, чтобы скопировать'"
    class="inline-flex items-center gap-1 font-mono text-slate-700 dark:text-slate-200 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-slate-800 px-1.5 py-0.5 rounded transition cursor-pointer select-all group whitespace-nowrap shrink-0"
  >
    <slot><span class="whitespace-nowrap">{{ text || '—' }}</span></slot>
    <i class="pi pi-copy text-xs opacity-40 dark:opacity-50 group-hover:opacity-100 transition shrink-0"></i>
  </button>
</template>

<script setup>
import { useToast } from 'primevue/usetoast'

const props = defineProps({
  text: {
    type: String,
    default: '',
  },
  label: {
    type: String,
    default: 'Значение',
  },
  title: {
    type: String,
    default: '',
  },
})

const toast = useToast()

const copy = async () => {
  if (!props.text) return
  try {
    await navigator.clipboard.writeText(props.text)
    toast.add({
      severity: 'info',
      summary: 'Скопировано в буфер',
      detail: `${props.label}: '${props.text}'`,
      life: 2500,
    })
  } catch (err) {
    // Fallback
    const textArea = document.createElement('textarea')
    textArea.value = props.text
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    toast.add({
      severity: 'info',
      summary: 'Скопировано',
      detail: `${props.label}: '${props.text}'`,
      life: 2500,
    })
  }
}
</script>
