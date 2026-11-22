<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-100 p-4">
    <div class="max-w-md w-full bg-white rounded-2xl shadow-xl border border-slate-200 p-8">
      <!-- Header -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-blue-600 text-white mb-4 shadow-md">
          <i class="pi pi-database text-2xl"></i>
        </div>
        <h1 class="text-2xl font-bold text-slate-900 tracking-tight">Вход в систему KSZ-DB</h1>
        <p class="text-sm text-slate-500 mt-1">База клиентов и технической поддержки iiko</p>
      </div>

      <!-- Error / Notice Alert -->
      <div
        v-if="errorMessage"
        class="mb-6 p-4 rounded-xl text-sm border flex items-start gap-3"
        :class="isPendingError
          ? 'bg-amber-50 text-amber-800 border-amber-200'
          : 'bg-rose-50 text-rose-800 border-rose-200'"
      >
        <i :class="isPendingError ? 'pi pi-clock text-amber-600' : 'pi pi-exclamation-circle text-rose-600'" class="text-lg mt-0.5"></i>
        <div>
          <div class="font-semibold">{{ isPendingError ? 'Доступ проверяется' : 'Ошибка авторизации' }}</div>
          <div>{{ errorMessage }}</div>
        </div>
      </div>

      <!-- Login Form -->
      <form @submit.prevent="handleLogin" class="flex flex-col gap-4">
        <div>
          <label class="block text-xs font-semibold uppercase text-slate-600 mb-1.5">Имя пользователя или Email</label>
          <div class="p-input-icon-left w-full">
            <InputText
              v-model="username"
              placeholder="Введите логин"
              class="w-full text-sm"
              autofocus
              required
            />
          </div>
        </div>

        <div>
          <label class="block text-xs font-semibold uppercase text-slate-600 mb-1.5">Пароль</label>
          <div class="p-input-icon-left w-full">
            <InputText
              v-model="password"
              type="password"
              placeholder="Введите пароль"
              class="w-full text-sm font-mono"
              required
            />
          </div>
        </div>

        <Button
          type="submit"
          label="Войти в систему"
          icon="pi pi-sign-in"
          :loading="authStore.loading"
          class="w-full mt-2"
        />
      </form>

      <!-- Registration link -->
      <div class="mt-8 pt-6 border-t border-slate-200 text-center text-sm text-slate-500">
        Нет учетной записи?
        <router-link to="/register" class="text-blue-600 font-semibold hover:underline ml-1">
          Подать заявку на регистрацию
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const errorMessage = ref('')

const isPendingError = computed(() => {
  return errorMessage.value.toLowerCase().includes('ожидает') ||
         errorMessage.value.toLowerCase().includes('проверяется')
})

const handleLogin = async () => {
  errorMessage.value = ''
  const res = await authStore.login(username.value, password.value)
  if (res.success) {
    router.push('/')
  } else {
    errorMessage.value = res.error
  }
}
</script>
