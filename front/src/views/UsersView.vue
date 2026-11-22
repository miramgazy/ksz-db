<template>
  <div class="min-h-screen flex flex-col bg-slate-50">
    <Navbar />

    <main class="flex-1 w-full px-4 sm:px-6 lg:px-8 2xl:px-10 py-6 flex flex-col gap-5">
      <!-- Header -->
      <div class="bg-white rounded-xl shadow-xs border border-slate-200 p-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 class="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <span>Управление пользователями и доступом</span>
            <Tag value="Суперадмин" severity="help" class="!text-[11px]" />
          </h1>
          <p class="text-xs text-slate-500 mt-0.5">Модерация заявок на регистрацию, распределение ролей и контроль учетных записей</p>
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
      <div class="flex items-center gap-2 border-b border-slate-200 pb-1">
        <button
          type="button"
          @click="currentTab = 'pending'"
          class="px-4 py-2 text-sm font-semibold rounded-lg transition flex items-center gap-2"
          :class="currentTab === 'pending'
            ? 'bg-blue-600 text-white shadow-xs'
            : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/60'"
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
          class="px-4 py-2 text-sm font-semibold rounded-lg transition flex items-center gap-2"
          :class="currentTab === 'all'
            ? 'bg-blue-600 text-white shadow-xs'
            : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/60'"
        >
          <i class="pi pi-users text-xs"></i>
          <span>Все пользователи ({{ users.length }})</span>
        </button>
      </div>

      <!-- SECTION 1: Pending Users Queue -->
      <div v-if="currentTab === 'pending'" class="flex flex-col gap-3">
        <div v-if="!pendingUsers.length" class="bg-white rounded-xl shadow-xs border border-slate-200 p-12 text-center text-slate-400">
          <i class="pi pi-check-circle text-5xl text-emerald-500 mb-3"></i>
          <h3 class="text-base font-bold text-slate-800">Нет новых заявок на активацию</h3>
          <p class="text-sm mt-1">Все зарегистрированные сотрудники проверены и активированы.</p>
        </div>

        <div
          v-for="user in pendingUsers"
          :key="user.id"
          class="bg-white rounded-xl shadow-xs border border-amber-200 p-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 hover:shadow-md transition"
        >
          <div class="flex items-start gap-3">
            <div class="w-10 h-10 rounded-full bg-amber-100 text-amber-700 flex items-center justify-center font-bold text-lg mt-0.5">
              <i class="pi pi-user"></i>
            </div>
            <div>
              <div class="flex items-center gap-2">
                <span class="font-bold text-slate-900 text-base">{{ user.full_name || user.username }}</span>
                <span class="text-xs text-slate-400 font-mono">(@{{ user.username }})</span>
                <Tag value="Ожидает одобрения" severity="warn" class="!text-[10px]" />
              </div>
              <div class="flex flex-wrap items-center gap-3 text-xs text-slate-500 mt-1">
                <span v-if="user.email"><i class="pi pi-envelope mr-1"></i>{{ user.email }}</span>
                <span v-if="user.phone"><i class="pi pi-phone mr-1"></i>{{ user.phone }}</span>
                <span><i class="pi pi-calendar mr-1"></i>Подана: {{ formatDate(user.date_joined) }}</span>
                <span>Запросил роль: <strong class="text-slate-700">{{ user.role_display }}</strong></span>
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
              severity="danger"
              outlined
              size="small"
              @click="rejectUser(user)"
            />
          </div>
        </div>
      </div>

      <!-- SECTION 2: All Users Table -->
      <div v-else class="bg-white rounded-xl shadow-xs border border-slate-200 overflow-hidden">
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
                <span class="font-bold text-slate-800">{{ data.full_name || '—' }}</span>
                <span class="text-xs text-slate-400 font-mono">@{{ data.username }}</span>
              </div>
            </template>
          </Column>

          <Column field="email" header="Контакты" style="min-width: 200px">
            <template #body="{ data }">
              <div class="flex flex-col text-xs">
                <span>{{ data.email || '—' }}</span>
                <span class="text-slate-400">{{ data.phone || '' }}</span>
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
              <span class="text-xs text-slate-500">{{ formatDate(data.date_joined) }}</span>
            </template>
          </Column>

          <Column header="Действия" style="min-width: 120px; text-align: right">
            <template #body="{ data }">
              <div class="flex items-center justify-end gap-1">
                <Button
                  v-if="!data.is_active"
                  icon="pi pi-check"
                  size="small"
                  severity="success"
                  text
                  title="Активировать пользователя"
                  @click="openApproveModal(data)"
                />
                <Button
                  v-else-if="data.username !== 'admin'"
                  icon="pi pi-ban"
                  size="small"
                  severity="danger"
                  text
                  title="Заблокировать пользователя"
                  @click="rejectUser(data)"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </div>
    </main>

    <!-- Modal: Approve User and Confirm Role -->
    <Dialog
      v-model:visible="showApproveModal"
      header="Активация учетной записи"
      :modal="true"
      :style="{ width: '440px' }"
    >
      <div v-if="selectedUser" class="flex flex-col gap-4 py-2">
        <p class="text-sm text-slate-600">
          Вы подтверждаете доступ для сотрудника:
          <strong class="text-slate-900 block mt-1">{{ selectedUser.full_name }} (@{{ selectedUser.username }})</strong>
        </p>

        <div>
          <label class="block text-xs font-semibold uppercase text-slate-600 mb-1.5">Назначить роль в системе</label>
          <div class="flex flex-col gap-2">
            <label class="flex items-center gap-2 p-2 rounded-lg border cursor-pointer" :class="approveRole === 'MANAGER' ? 'border-blue-500 bg-blue-50' : 'border-slate-200'">
              <input type="radio" value="MANAGER" v-model="approveRole" />
              <div>
                <span class="text-sm font-semibold text-slate-800">Менеджер</span>
                <p class="text-xs text-slate-500">Может создавать, редактировать клиентов и AnyDesk</p>
              </div>
            </label>

            <label class="flex items-center gap-2 p-2 rounded-lg border cursor-pointer" :class="approveRole === 'VIEWER' ? 'border-blue-500 bg-blue-50' : 'border-slate-200'">
              <input type="radio" value="VIEWER" v-model="approveRole" />
              <div>
                <span class="text-sm font-semibold text-slate-800">Наблюдатель (Только чтение)</span>
                <p class="text-xs text-slate-500">Просмотр, запуск и копирование данных без права изменения</p>
              </div>
            </label>

            <label class="flex items-center gap-2 p-2 rounded-lg border cursor-pointer" :class="approveRole === 'SUPERADMIN' ? 'border-purple-500 bg-purple-50' : 'border-slate-200'">
              <input type="radio" value="SUPERADMIN" v-model="approveRole" />
              <div>
                <span class="text-sm font-semibold text-purple-700">Суперадминистратор</span>
                <p class="text-xs text-slate-500">Полный доступ к системе и управлению пользователями</p>
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
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { usersApi } from '../api/users'
import Navbar from '../components/Navbar.vue'

const toast = useToast()
const confirm = useConfirm()

const loading = ref(false)
const users = ref([])
const currentTab = ref('pending')

const showApproveModal = ref(false)
const selectedUser = ref(null)
const approveRole = ref('MANAGER')
const approving = ref(false)

const pendingUsers = computed(() => {
  return users.value.filter(u => u.registration_status === 'PENDING' || !u.is_active)
})

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

const rejectUser = (user) => {
  confirm.require({
    message: `Вы уверены, что хотите отклонить/заблокировать пользователя '${user.username}'?`,
    header: 'Отклонение заявки',
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

onMounted(() => {
  loadUsers()
})
</script>
