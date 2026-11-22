<template>
  <header class="bg-white border-b border-slate-200 sticky top-0 z-40 shadow-xs">
    <div class="w-full px-4 sm:px-6 lg:px-8 2xl:px-10">
      <div class="flex justify-between h-14 items-center">
        <!-- Left: Logo & Nav Links -->
        <div class="flex items-center gap-6">
          <router-link to="/" class="flex items-center gap-2.5 font-bold text-slate-800 text-lg hover:text-blue-600 transition">
            <div class="w-8 h-8 rounded-lg bg-blue-600 text-white flex items-center justify-center shadow-xs">
              <i class="pi pi-database text-sm"></i>
            </div>
            <span>KSZ<span class="text-blue-600">.DB</span></span>
          </router-link>

          <nav class="hidden md:flex items-center gap-1">
            <router-link
              to="/"
              class="px-3 py-1.5 rounded-md text-sm font-medium transition"
              :class="$route.path === '/' ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'"
            >
              <i class="pi pi-building mr-1.5 text-xs"></i>Заведения
            </router-link>

            <router-link
              to="/anydesk"
              class="px-3 py-1.5 rounded-md text-sm font-medium transition"
              :class="$route.path === '/anydesk' ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'"
            >
              <i class="pi pi-desktop mr-1.5 text-xs"></i>Все AnyDesk
            </router-link>

            <router-link
              to="/services"
              class="px-3 py-1.5 rounded-md text-sm font-medium transition flex items-center"
              :class="$route.path === '/services' ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'"
            >
              <i class="pi pi-cog mr-1.5 text-xs text-emerald-600"></i>ИТС и Доп
            </router-link>

            <router-link
              to="/distributions"
              class="px-3 py-1.5 rounded-md text-sm font-medium transition"
              :class="$route.path === '/distributions' ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'"
            >
              <i class="pi pi-download mr-1.5 text-xs"></i>Дистрибутивы iiko
            </router-link>

            <router-link
              v-if="authStore.isSuperAdmin"
              to="/users"
              class="px-3 py-1.5 rounded-md text-sm font-medium transition flex items-center gap-1.5"
              :class="$route.path === '/users' ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'"
            >
              <i class="pi pi-users text-xs"></i>
              <span>Пользователи</span>
              <Badge v-if="pendingCount > 0" :value="pendingCount" severity="danger" size="small" />
            </router-link>
          </nav>
        </div>

        <!-- Right: Companion Status, Tools, User & Logout -->
        <div class="flex items-center gap-3">
          <!-- Companion Status Indicator -->
          <div
            @click="companionStore.checkStatus()"
            class="hidden sm:flex items-center gap-2 px-2.5 py-1 rounded-full text-xs font-medium cursor-pointer border transition"
            :class="companionStore.isOnline
              ? 'bg-emerald-50 text-emerald-700 border-emerald-200 hover:bg-emerald-100'
              : 'bg-slate-100 text-slate-500 border-slate-200 hover:bg-slate-200'"
            title="Статус локального агента ksz-helper (нажмите для проверки)"
          >
            <span class="w-2 h-2 rounded-full" :class="companionStore.isOnline ? 'bg-emerald-500 animate-pulse' : 'bg-slate-400'"></span>
            <span>{{ companionStore.isOnline ? 'Агент активен' : 'Агент офлайн' }}</span>
          </div>

          <!-- Password Generator Button -->
          <Button
            icon="pi pi-key"
            text
            rounded
            severity="secondary"
            title="Генератор паролей"
            @click="showPassGen = true"
          />

          <!-- User info tag -->
          <div class="flex items-center gap-2 pl-2 border-l border-slate-200">
            <div class="text-right hidden sm:block">
              <div class="text-xs font-semibold text-slate-800 leading-tight">
                {{ authStore.userDisplayName }}
              </div>
              <div class="text-[10px] uppercase font-bold tracking-wider" :class="roleColor">
                {{ roleLabel }}
              </div>
            </div>

            <Button
              icon="pi pi-sign-out"
              text
              rounded
              severity="danger"
              title="Выйти из системы"
              @click="authStore.logout()"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Password Generator Modal -->
    <PasswordGeneratorModal v-model="showPassGen" />
  </header>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Badge from 'primevue/badge'
import Button from 'primevue/button'
import { useAuthStore } from '../stores/auth'
import { useCompanionStore } from '../stores/companion'
import { usersApi } from '../api/users'
import PasswordGeneratorModal from './PasswordGeneratorModal.vue'

const authStore = useAuthStore()
const companionStore = useCompanionStore()
const showPassGen = ref(false)
const pendingCount = ref(0)

const roleLabel = computed(() => {
  if (authStore.isSuperAdmin) return 'Суперадмин'
  if (authStore.isManager) return 'Менеджер'
  return 'Наблюдатель'
})

const roleColor = computed(() => {
  if (authStore.isSuperAdmin) return 'text-purple-600'
  if (authStore.isManager) return 'text-blue-600'
  return 'text-amber-600'
})

onMounted(async () => {
  if (authStore.isSuperAdmin) {
    try {
      const res = await usersApi.getUsers({ registration_status: 'PENDING' })
      pendingCount.value = res.data.count ?? res.data.results?.length ?? 0
    } catch (e) {
      // Ignore
    }
  }
})
</script>
