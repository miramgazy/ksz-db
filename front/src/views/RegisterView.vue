<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-100 p-4">
    <div class="max-w-lg w-full bg-white rounded-2xl shadow-xl border border-slate-200 p-8">
      <!-- Header -->
      <div class="text-center mb-6">
        <div class="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-blue-600 text-white mb-3 shadow-md">
          <i class="pi pi-user-plus text-xl"></i>
        </div>
        <h1 class="text-2xl font-bold text-slate-900 tracking-tight">Регистрация в KSZ-DB</h1>
        <p class="text-xs text-slate-500 mt-1">Заполните данные для создания учетной записи сотрудника</p>
      </div>

      <!-- Success Screen after submission -->
      <div v-if="submittedSuccess" class="py-6 text-center flex flex-col items-center gap-4">
        <div class="w-16 h-16 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center text-3xl">
          <i class="pi pi-check-circle"></i>
        </div>
        <div>
          <h2 class="text-xl font-bold text-slate-800">Заявка успешно принята!</h2>
          <p class="text-sm text-slate-600 mt-2 max-w-sm">
            Ваш доступ проверяется администратором. Вы сможете войти в систему после того, как суперадминистратор активирует вашу учетную запись.
          </p>
        </div>
        <router-link to="/login" class="mt-4">
          <Button label="Перейти на страницу входа" icon="pi pi-arrow-left" severity="primary" />
        </router-link>
      </div>

      <!-- Registration Form -->
      <div v-else>
        <!-- Error Alert -->
        <div v-if="errorMessage" class="mb-4 p-3 bg-rose-50 border border-rose-200 text-rose-700 rounded-xl text-sm flex items-center gap-2">
          <i class="pi pi-exclamation-circle"></i>
          <span>{{ errorMessage }}</span>
        </div>

        <form @submit.prevent="handleRegister" class="flex flex-col gap-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold uppercase text-slate-600 mb-1">Имя пользователя (Логин) *</label>
              <InputText v-model="form.username" placeholder="ivanov" class="w-full text-sm" required />
            </div>

            <div>
              <label class="block text-xs font-semibold uppercase text-slate-600 mb-1">ФИО сотрудника *</label>
              <InputText v-model="form.full_name" placeholder="Иванов Иван" class="w-full text-sm" required />
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold uppercase text-slate-600 mb-1">Email</label>
              <InputText v-model="form.email" type="email" placeholder="ivanov@ksz.kz" class="w-full text-sm" />
            </div>

            <div>
              <label class="block text-xs font-semibold uppercase text-slate-600 mb-1">Телефон</label>
              <InputText v-model="form.phone" placeholder="+7 700 000 00 00" class="w-full text-sm" />
            </div>
          </div>

          <!-- Role selection -->
          <div>
            <label class="block text-xs font-semibold uppercase text-slate-600 mb-1.5">Запрашиваемая роль *</label>
            <div class="grid grid-cols-2 gap-3 text-sm">
              <label
                class="flex flex-col p-3 rounded-xl border cursor-pointer transition"
                :class="form.role === 'MANAGER' ? 'border-blue-500 bg-blue-50/50' : 'border-slate-200 hover:border-slate-300'"
              >
                <div class="flex items-center gap-2 font-semibold text-slate-800">
                  <input type="radio" value="MANAGER" v-model="form.role" class="text-blue-600" />
                  <span>Менеджер</span>
                </div>
                <span class="text-xs text-slate-500 mt-1">Создание и редактирование записей клиентов</span>
              </label>

              <label
                class="flex flex-col p-3 rounded-xl border cursor-pointer transition"
                :class="form.role === 'VIEWER' ? 'border-blue-500 bg-blue-50/50' : 'border-slate-200 hover:border-slate-300'"
              >
                <div class="flex items-center gap-2 font-semibold text-slate-800">
                  <input type="radio" value="VIEWER" v-model="form.role" class="text-blue-600" />
                  <span>Наблюдатель</span>
                </div>
                <span class="text-xs text-slate-500 mt-1">Только просмотр, запуск и копирование данных</span>
              </label>
            </div>
          </div>

          <!-- Password & Confirm -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold uppercase text-slate-600 mb-1">Пароль *</label>
              <InputText v-model="form.password" type="password" placeholder="Минимум 6 символов" class="w-full text-sm font-mono" required />
            </div>

            <div>
              <label class="block text-xs font-semibold uppercase text-slate-600 mb-1">Подтверждение *</label>
              <InputText v-model="form.password_confirm" type="password" placeholder="Повторите пароль" class="w-full text-sm font-mono" required />
            </div>
          </div>

          <Button
            type="submit"
            label="Отправить заявку на регистрацию"
            icon="pi pi-send"
            :loading="authStore.loading"
            class="w-full mt-2"
          />
        </form>

        <div class="mt-6 pt-4 border-t border-slate-200 text-center text-sm text-slate-500">
          Уже есть аккаунт?
          <router-link to="/login" class="text-blue-600 font-semibold hover:underline ml-1">
            Войти в систему
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const form = ref({
  username: '',
  full_name: '',
  email: '',
  phone: '',
  role: 'MANAGER',
  password: '',
  password_confirm: '',
})

const errorMessage = ref('')
const submittedSuccess = ref(false)

const handleRegister = async () => {
  errorMessage.value = ''
  if (form.value.password !== form.value.password_confirm) {
    errorMessage.value = 'Введенные пароли не совпадают.'
    return
  }

  const res = await authStore.register(form.value)
  if (res.success) {
    submittedSuccess.value = true
  } else {
    errorMessage.value = res.error
  }
}
</script>
