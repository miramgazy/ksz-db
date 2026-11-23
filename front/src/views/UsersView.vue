<template>
  <div class="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950 transition-colors">
    <Navbar />

    <main class="flex-1 w-full px-4 sm:px-6 lg:px-8 2xl:px-10 py-6 flex flex-col gap-5">
      <!-- Header -->
      <div class="bg-white dark:bg-slate-900 rounded-xl shadow-xs border border-slate-200 dark:border-slate-800 p-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 class="text-xl font-bold text-slate-900 dark:text-slate-100 tracking-tight flex items-center gap-2">
            <span>Управление пользователями и доступом</span>
            <Tag value="Суперадмин" severity="help" class="!text-[11px]" />
          </h1>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Модерация заявок на регистрацию, распределение ролей и контроль учетных записей</p>
        </div>

        <Button
          icon="pi pi-refresh"
          label="Обновить"
          severity="secondary"
          outlined
          size="small"
          :loading="loading"
          @click="loadUsers"
        />
      </div>

      <!-- Tab Filter: Pending Requests vs All Users -->
      <div class="flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-1">
        <button
          type="button"
          @click="currentTab = 'pending'"
          class="px-4 py-2 text-sm font-semibold rounded-lg transition flex items-center gap-2 cursor-pointer"
          :class="currentTab === 'pending'
            ? 'bg-blue-600 text-white shadow-xs'
            : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-200/60 dark:hover:bg-slate-800'"
        >
          <i class="pi pi-user-plus text-xs"></i>
          <span>Ожидают активации</span>
          <Badge
            v-if="pendingUsers.length > 0"
            :value="pendingUsers.length"
            :severity="currentTab === 'pending' ? 'secondary' : 'danger'"
            size="small"
          />
        </button>

        <button
          type="button"
          @click="currentTab = 'all'"
          class="px-4 py-2 text-sm font-semibold rounded-lg transition flex items-center gap-2 cursor-pointer"
          :class="currentTab === 'all'
            ? 'bg-blue-600 text-white shadow-xs'
            : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-200/60 dark:hover:bg-slate-800'"
        >
          <i class="pi pi-users text-xs"></i>
          <span>Все пользователи ({{ users.length }})</span>
        </button>
      </div>

      <!-- SECTION 1: Pending Users Queue -->
      <div v-if="currentTab === 'pending'" class="flex flex-col gap-3">
        <div v-if="!pendingUsers.length" class="bg-white dark:bg-slate-900 rounded-xl shadow-xs border border-slate-200 dark:border-slate-800 p-12 text-center text-slate-400 dark:text-slate-500">
          <i class="pi pi-check-circle text-5xl text-emerald-500 mb-3"></i>
          <h3 class="text-base font-bold text-slate-800 dark:text-slate-100">Нет новых заявок на активацию</h3>
          <p class="text-sm mt-1">Все зарегистрированные сотрудники проверены и активированы.</p>
        </div>

        <div
          v-for="user in pendingUsers"
          :key="user.id"
          class="bg-white dark:bg-slate-900 rounded-xl shadow-xs border border-amber-200 dark:border-amber-900/60 p-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 hover:shadow-md transition"
        >
          <div class="flex items-start gap-3">
            <div class="w-10 h-10 rounded-full bg-amber-100 dark:bg-amber-950/80 text-amber-700 dark:text-amber-300 flex items-center justify-center font-bold text-lg mt-0.5">
              <i class="pi pi-user"></i>
            </div>
            <div>
              <div class="flex items-center gap-2">
                <span class="font-bold text-slate-900 dark:text-white text-base">{{ user.full_name || user.username }}</span>
                <span class="text-xs text-slate-400 dark:text-slate-500 font-mono">(@{{ user.username }})</span>
                <Tag value="Ожидает одобрения" severity="warn" class="!text-[10px]" />
              </div>
              <div class="flex flex-wrap items-center gap-3 text-xs text-slate-500 dark:text-slate-400 mt-1">
                <span v-if="user.email"><i class="pi pi-envelope mr-1"></i>{{ user.email }}</span>
                <span v-if="user.phone"><i class="pi pi-phone mr-1"></i>{{ user.phone }}</span>
                <span><i class="pi pi-calendar mr-1"></i>Подана: {{ formatDate(user.date_joined) }}</span>
                <span>Запросил роль: <strong class="text-slate-700 dark:text-slate-200">{{ user.role_display }}</strong></span>
              </div>
            </div>
          </div>

          <div class="flex items-center gap-2 w-full md:w-auto justify-end border-t md:border-t-0 pt-3 md:pt-0">
            <Button
              label="Активировать"
              icon="pi pi-check"
              severity="success"
              size="small"
              @click="openApproveModal(user)"
            />
            <Button
              label="Отклонить"
              icon="pi pi-times"
              severity="warn"
              outlined
              size="small"
              @click="rejectUser(user)"
            />
            <Button
              icon="pi pi-trash"
              severity="danger"
              text
              rounded
              size="small"
              title="Удалить пользователя"
              @click="confirmDeleteUser(user)"
            />
          </div>
        </div>
      </div>

      <!-- SECTION 2: All Users Table -->
      <div v-else class="bg-white dark:bg-slate-900 rounded-xl shadow-xs border border-slate-200 dark:border-slate-800 overflow-hidden">
        <DataTable
          :value="users"
          :loading="loading"
          dataKey="id"
          class="p-datatable-sm"
          stripedRows
          hoverableRows
          responsiveLayout="scroll"
        >
          <Column field="full_name" header="Сотрудник / Логин" :sortable="true" style="min-width: 220px">
            <template #body="{ data }">
              <div class="flex flex-col">
                <span class="font-bold text-slate-800 dark:text-slate-100">{{ data.full_name || '—' }}</span>
                <span class="text-xs text-slate-400 dark:text-slate-500 font-mono">@{{ data.username }}</span>
              </div>
            </template>
          </Column>

          <Column field="email" header="Контакты" style="min-width: 200px">
            <template #body="{ data }">
              <div class="flex flex-col text-xs">
                <span class="text-slate-800 dark:text-slate-200">{{ data.email || '—' }}</span>
                <span class="text-slate-400 dark:text-slate-500">{{ data.phone || '' }}</span>
              </div>
            </template>
          </Column>

          <Column field="role" header="Роль" :sortable="true" style="min-width: 140px">
            <template #body="{ data }">
              <Tag
                :value="data.role_display"
                :severity="getRoleSeverity(data.role)"
                class="!text-[11px]"
              />
            </template>
          </Column>

          <Column field="is_active" header="Статус доступа" :sortable="true" style="min-width: 140px">
            <template #body="{ data }">
              <Tag
                :value="data.is_active ? 'Активен' : (data.registration_status === 'PENDING' ? 'Ожидает' : 'Заблокирован')"
                :severity="data.is_active ? 'success' : (data.registration_status === 'PENDING' ? 'warn' : 'danger')"
                class="!text-[11px]"
              />
            </template>
          </Column>

          <Column field="date_joined" header="Дата регистрации" :sortable="true" style="min-width: 160px">
            <template #body="{ data }">
              <span class="text-xs text-slate-500 dark:text-slate-400 font-mono">{{ formatDate(data.date_joined) }}</span>
            </template>
          </Column>

          <Column header="Действия" style="min-width: 160px; text-align: right">
            <template #body="{ data }">
              <div class="flex items-center justify-end gap-1">
                <!-- Activate button if inactive -->
                <Button
                  v-if="!data.is_active"
                  icon="pi pi-check"
                  size="small"
                  severity="success"
                  text
                  rounded
                  title="Активировать пользователя"
                  @click="openApproveModal(data)"
                />
                <!-- Block button if active and eligible -->
                <Button
                  v-else-if="canBlock(data)"
                  icon="pi pi-ban"
                  size="small"
                  severity="warn"
                  text
                  rounded
                  title="Заблокировать доступ"
                  @click="rejectUser(data)"
                />

                <!-- Edit Role / Permissions Button -->
                <Button
                  icon="pi pi-pencil"
                  size="small"
                  severity="secondary"
                  text
                  rounded
                  title="Редактировать данные и роль"
                  @click="openEditModal(data)"
                />

                <!-- Delete User Button -->
                <Button
                  v-if="canDelete(data)"
                  icon="pi pi-trash"
                  size="small"
                  severity="danger"
                  text
                  rounded
                  title="Удалить пользователя"
                  @click="confirmDeleteUser(data)"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </div>
    </main>

    <!-- Modal: Edit User Role & Permissions -->
    <Dialog
      v-model:visible="showEditModal"
      :header="`Редактирование пользователя: @${editForm.username}`"
      :modal="true"
      :style="{ width: '480px' }"
    >
      <div v-if="selectedUserToEdit" class="flex flex-col gap-4 py-2 text-sm">
        <div class="p-3 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-950/80 text-blue-700 dark:text-blue-300 flex items-center justify-center font-bold text-base shrink-0">
            <i class="pi pi-user"></i>
          </div>
          <div>
            <div class="font-bold text-slate-900 dark:text-white">
              {{ editForm.full_name || editForm.username }}
            </div>
            <div class="text-xs font-mono text-slate-500 dark:text-slate-400">
              Логин: @{{ editForm.username }}
            </div>
          </div>
        </div>

        <div>
          <label class="block text-xs font-semibold uppercase text-slate-600 dark:text-slate-300 mb-1">
            ФИО сотрудника
          </label>
          <InputText
            v-model="editForm.full_name"
            placeholder="Имя Фамилия"
            class="w-full text-sm"
          />
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-semibold uppercase text-slate-600 dark:text-slate-300 mb-1">
              Email
            </label>
            <InputText
              v-model="editForm.email"
              placeholder="user@example.com"
              class="w-full text-xs font-mono"
            />
          </div>
          <div>
            <label class="block text-xs font-semibold uppercase text-slate-600 dark:text-slate-300 mb-1">
              Телефон
            </label>
            <InputText
              v-model="editForm.phone"
              placeholder="+7 (701) 123-45-67"
              class="w-full text-xs font-mono"
            />
          </div>
        </div>

        <div>
          <label class="block text-xs font-semibold uppercase text-slate-600 dark:text-slate-300 mb-1.5">
            Роль и уровень доступа *
          </label>
          <div class="flex flex-col gap-2">
            <label class="flex items-center gap-2 p-2.5 rounded-lg border cursor-pointer transition" :class="editForm.role === 'MANAGER' ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/40 ring-1 ring-blue-400' : 'border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800/60'">
              <input type="radio" value="MANAGER" v-model="editForm.role" />
              <div>
                <span class="text-sm font-semibold text-slate-800 dark:text-slate-200">Менеджер</span>
                <p class="text-xs text-slate-500 dark:text-slate-400">Создание и редактирование заведений, договоров и AnyDesk</p>
              </div>
            </label>

            <label class="flex items-center gap-2 p-2.5 rounded-lg border cursor-pointer transition" :class="editForm.role === 'VIEWER' ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/40 ring-1 ring-blue-400' : 'border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800/60'">
              <input type="radio" value="VIEWER" v-model="editForm.role" />
              <div>
                <span class="text-sm font-semibold text-slate-800 dark:text-slate-200">Наблюдатель (Только чтение)</span>
                <p class="text-xs text-slate-500 dark:text-slate-400">Просмотр, запуск AnyDesk и копирование данных без права изменения</p>
              </div>
            </label>

            <label class="flex items-center gap-2 p-2.5 rounded-lg border cursor-pointer transition" :class="editForm.role === 'SUPERADMIN' ? 'border-purple-500 bg-purple-50 dark:bg-purple-950/40 ring-1 ring-purple-400' : 'border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800/60'">
              <input type="radio" value="SUPERADMIN" v-model="editForm.role" />
              <div>
                <span class="text-sm font-semibold text-purple-700 dark:text-purple-300">Суперадминистратор</span>
                <p class="text-xs text-slate-500 dark:text-slate-400">Полный доступ ко всей системе, тарифам и управлению пользователями</p>
              </div>
            </label>
          </div>
        </div>

        <!-- Active / Blocked status switch -->
        <div class="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-lg">
          <div>
            <div class="text-xs font-semibold text-slate-800 dark:text-slate-200">Статус учетной записи:</div>
            <div class="text-[11px] text-slate-500 dark:text-slate-400">
              {{ editForm.is_active ? 'Пользователь может авторизоваться в системе' : 'Доступ в систему заблокирован' }}
            </div>
          </div>
          <div class="flex items-center gap-2">
            <Checkbox v-model="editForm.is_active" :binary="true" inputId="user_active_cb" />
            <label for="user_active_cb" class="text-xs font-bold cursor-pointer" :class="editForm.is_active ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'">
              {{ editForm.is_active ? 'Активен' : 'Заблокирован' }}
            </label>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-end gap-2">
          <Button label="Отмена" severity="secondary" text @click="showEditModal = false" />
          <Button
            label="Сохранить изменения"
            icon="pi pi-check"
            :loading="savingEdit"
            @click="submitEditUser"
          />
        </div>
      </template>
    </Dialog>

    <!-- Modal: Approve User and Confirm Role -->
    <Dialog
      v-model:visible="showApproveModal"
      header="Активация учетной записи"
      :modal="true"
      :style="{ width: '440px' }"
    >
      <div v-if="selectedUser" class="flex flex-col gap-4 py-2">
        <p class="text-sm text-slate-600 dark:text-slate-300">
          Вы подтверждаете доступ для сотрудника:
          <strong class="text-slate-900 dark:text-white block mt-1">{{ selectedUser.full_name }} (@{{ selectedUser.username }})</strong>
        </p>

        <div>
          <label class="block text-xs font-semibold uppercase text-slate-600 dark:text-slate-300 mb-1.5">Назначить роль в системе</label>
          <div class="flex flex-col gap-2">
            <label class="flex items-center gap-2 p-2 rounded-lg border cursor-pointer transition" :class="approveRole === 'MANAGER' ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/40' : 'border-slate-200 dark:border-slate-700'">
              <input type="radio" value="MANAGER" v-model="approveRole" />
              <div>
                <span class="text-sm font-semibold text-slate-800 dark:text-slate-200">Менеджер</span>
                <p class="text-xs text-slate-500 dark:text-slate-400">Может создавать, редактировать клиентов и AnyDesk</p>
              </div>
            </label>

            <label class="flex items-center gap-2 p-2 rounded-lg border cursor-pointer transition" :class="approveRole === 'VIEWER' ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/40' : 'border-slate-200 dark:border-slate-700'">
              <input type="radio" value="VIEWER" v-model="approveRole" />
              <div>
                <span class="text-sm font-semibold text-slate-800 dark:text-slate-200">Наблюдатель (Только чтение)</span>
                <p class="text-xs text-slate-500 dark:text-slate-400">Просмотр, запуск и копирование данных без права изменения</p>
              </div>
            </label>

            <label class="flex items-center gap-2 p-2 rounded-lg border cursor-pointer transition" :class="approveRole === 'SUPERADMIN' ? 'border-purple-500 bg-purple-50 dark:bg-purple-950/40' : 'border-slate-200 dark:border-slate-700'">
              <input type="radio" value="SUPERADMIN" v-model="approveRole" />
              <div>
                <span class="text-sm font-semibold text-purple-700 dark:text-purple-300">Суперадминистратор</span>
                <p class="text-xs text-slate-500 dark:text-slate-400">Полный доступ к системе и управлению пользователями</p>
              </div>
            </label>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-end gap-2">
          <Button label="Отмена" severity="secondary" text @click="showApproveModal = false" />
          <Button
            label="Подтвердить и активировать"
            icon="pi pi-check"
            severity="success"
            :loading="approving"
            @click="submitApprove"
          />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import Badge from 'primevue/badge'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Checkbox from 'primevue/checkbox'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { useAuthStore } from '../stores/auth'
import { usersApi } from '../api/users'
import Navbar from '../components/Navbar.vue'

const toast = useToast()
const confirm = useConfirm()
const authStore = useAuthStore()

const loading = ref(false)
const users = ref([])
const currentTab = ref('pending')

const showApproveModal = ref(false)
const selectedUser = ref(null)
const approveRole = ref('MANAGER')
const approving = ref(false)

const showEditModal = ref(false)
const selectedUserToEdit = ref(null)
const savingEdit = ref(false)
const editForm = ref({
  username: '',
  full_name: '',
  email: '',
  phone: '',
  role: 'VIEWER',
  is_active: true,
})

const pendingUsers = computed(() => {
  return users.value.filter(u => u.registration_status === 'PENDING' || !u.is_active)
})

const canBlock = (user) => {
  if (user.username === 'admin') return false
  if (authStore.user?.id && user.id === authStore.user.id) return false
  if (user.username === authStore.user?.username) return false
  return true
}

const canDelete = (user) => {
  if (user.username === 'admin') return false
  if (authStore.user?.id && user.id === authStore.user.id) return false
  if (user.username === authStore.user?.username) return false
  return true
}

const loadUsers = async () => {
  loading.value = true
  try {
    const res = await usersApi.getUsers()
    users.value = res.data.results || res.data
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Ошибка', detail: 'Не удалось загрузить список пользователей', life: 3000 })
  } finally {
    loading.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  const d = new Date(dateStr)
  return d.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const getRoleSeverity = (role) => {
  if (role === 'SUPERADMIN') return 'help'
  if (role === 'MANAGER') return 'info'
  return 'warn'
}

const openApproveModal = (user) => {
  selectedUser.value = user
  approveRole.value = user.role || 'MANAGER'
  showApproveModal.value = true
}

const submitApprove = async () => {
  if (!selectedUser.value) return
  approving.value = true
  try {
    await usersApi.approveUser(selectedUser.value.id, { role: approveRole.value })
    toast.add({
      severity: 'success',
      summary: 'Пользователь активирован',
      detail: `Пользователь ${selectedUser.value.username} теперь может войти в систему.`,
      life: 3500,
    })
    showApproveModal.value = false
    loadUsers()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Ошибка активации', detail: err.message, life: 3000 })
  } finally {
    approving.value = false
  }
}

const openEditModal = (user) => {
  selectedUserToEdit.value = user
  editForm.value = {
    username: user.username,
    full_name: user.full_name || '',
    email: user.email || '',
    phone: user.phone || '',
    role: user.role || 'VIEWER',
    is_active: Boolean(user.is_active),
  }
  showEditModal.value = true
}

const submitEditUser = async () => {
  if (!selectedUserToEdit.value) return
  savingEdit.value = true
  try {
    const payload = {
      full_name: editForm.value.full_name.trim(),
      email: editForm.value.email.trim(),
      phone: editForm.value.phone.trim(),
      role: editForm.value.role,
      is_active: editForm.value.is_active,
    }
    await usersApi.updateUser(selectedUserToEdit.value.id, payload)
    toast.add({
      severity: 'success',
      summary: 'Успешно',
      detail: `Права и данные пользователя @${selectedUserToEdit.value.username} сохранены.`,
      life: 3000,
    })
    showEditModal.value = false
    await loadUsers()
  } catch (err) {
    const detail = err.response?.data?.role?.[0] || err.response?.data?.detail || err.message || 'Ошибка обновления пользователя'
    toast.add({ severity: 'error', summary: 'Ошибка сохранения', detail, life: 4000 })
  } finally {
    savingEdit.value = false
  }
}

const rejectUser = (user) => {
  confirm.require({
    message: `Вы уверены, что хотите заблокировать пользователя '${user.username}'?`,
    header: 'Блокировка доступа',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Заблокировать',
    rejectLabel: 'Отмена',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await usersApi.rejectUser(user.id)
        toast.add({ severity: 'warn', summary: 'Успешно', detail: `Доступ для ${user.username} заблокирован`, life: 2500 })
        loadUsers()
      } catch (err) {
        toast.add({ severity: 'error', summary: 'Ошибка', detail: err.message, life: 3000 })
      }
    },
  })
}

const confirmDeleteUser = (user) => {
  confirm.require({
    message: `Вы действительно хотите безвозвратно удалить пользователя "${user.full_name || user.username}" (@${user.username})? Это действие нельзя отменить.`,
    header: 'Удаление пользователя',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Удалить безвозвратно',
    rejectLabel: 'Отмена',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await usersApi.deleteUser(user.id)
        toast.add({
          severity: 'success',
          summary: 'Пользователь удален',
          detail: `Пользователь @${user.username} успешно удален из системы.`,
          life: 3000,
        })
        await loadUsers()
      } catch (err) {
        const detail = err.response?.data?.detail || err.message || 'Ошибка удаления пользователя'
        toast.add({ severity: 'error', summary: 'Ошибка', detail, life: 4000 })
      }
    },
  })
}

onMounted(() => {
  loadUsers()
})
</script>
