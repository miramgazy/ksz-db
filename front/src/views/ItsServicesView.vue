<template>
  <div class="min-h-screen flex flex-col bg-slate-50">
    <Navbar />

    <main class="flex-1 w-full px-4 sm:px-6 lg:px-8 2xl:px-10 py-6 flex flex-col gap-5">
      <!-- Header Bar -->
      <div class="bg-white rounded-xl shadow-xs border border-slate-200 p-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 class="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <i class="pi pi-shield text-emerald-600"></i>
            <span>ИТС и дополнительные услуги</span>
            <span class="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 font-mono border border-slate-200">
              {{ services.length }} подписок
            </span>
          </h1>
          <p class="text-xs text-slate-500 mt-0.5">Управление договорами техсопровождения, сроками действия подписок и тарифами</p>
        </div>

        <div class="flex flex-wrap items-center gap-2 w-full sm:w-auto">
          <Button
            label="Каталог услуг"
            icon="pi pi-list"
            severity="secondary"
            outlined
            size="small"
            @click="openCatalogModal"
          />

          <Button
            v-if="authStore.canEdit"
            label="Добавить услугу"
            icon="pi pi-plus"
            severity="primary"
            size="small"
            @click="openAddServiceModal"
          />

          <Button
            icon="pi pi-refresh"
            severity="secondary"
            outlined
            size="small"
            title="Обновить данные"
            :loading="loading"
            @click="refreshData"
          />
        </div>
      </div>

      <!-- KPI Statistics Cards -->
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-7 gap-3">
        <!-- Total on ITS -->
        <div class="bg-white p-3 rounded-xl border border-slate-200 shadow-2xs flex flex-col">
          <div class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1">
            <i class="pi pi-shield text-emerald-600 text-[10px]"></i>
            Всего на ИТС
          </div>
          <div class="mt-1 flex items-baseline gap-1">
            <span class="text-lg font-bold text-slate-900 font-mono">{{ stats.total_its_companies || 0 }}</span>
            <span class="text-xs text-slate-500 font-mono">комп.</span>
          </div>
          <div class="text-[11px] text-slate-400 mt-0.5">
            {{ stats.total_its_points || 0 }} точек (RMS)
          </div>
        </div>

        <!-- > 1 Month (Green) -->
        <div
          class="p-3 rounded-xl border transition cursor-pointer flex flex-col"
          :class="selectedExpStatus === 'over_month'
            ? 'bg-emerald-100 border-emerald-400 ring-2 ring-emerald-300'
            : 'bg-emerald-50/70 border-emerald-200 hover:bg-emerald-100/70'"
          @click="toggleExpStatusFilter('over_month')"
          title="Срок действия больше месяца (> 30 дней)"
        >
          <div class="text-[11px] font-semibold text-emerald-800 uppercase tracking-wider flex items-center justify-between">
            <span>🟢 > 1 месяца</span>
            <i v-if="selectedExpStatus === 'over_month'" class="pi pi-check text-[10px]"></i>
          </div>
          <div class="text-lg font-bold text-emerald-950 font-mono mt-1">
            {{ stats.over_month || 0 }}
          </div>
          <div class="text-[11px] text-emerald-700 mt-0.5">Плановые</div>
        </div>

        <!-- 8 - 30 Days (Yellow/Amber) -->
        <div
          class="p-3 rounded-xl border transition cursor-pointer flex flex-col"
          :class="selectedExpStatus === 'week_month'
            ? 'bg-amber-100 border-amber-400 ring-2 ring-amber-300'
            : 'bg-amber-50/70 border-amber-200 hover:bg-amber-100/70'"
          @click="toggleExpStatusFilter('week_month')"
          title="Срок действия от 8 до 30 дней (подходит срок в текущем месяце)"
        >
          <div class="text-[11px] font-semibold text-amber-800 uppercase tracking-wider flex items-center justify-between">
            <span>🟡 8–30 дней</span>
            <i v-if="selectedExpStatus === 'week_month'" class="pi pi-check text-[10px]"></i>
          </div>
          <div class="text-lg font-bold text-amber-950 font-mono mt-1">
            {{ stats.week_month || 0 }}
          </div>
          <div class="text-[11px] text-amber-700 mt-0.5">Срок в этом месяце</div>
        </div>

        <!-- 1 - 7 Days (Orange) -->
        <div
          class="p-3 rounded-xl border transition cursor-pointer flex flex-col"
          :class="selectedExpStatus === 'week'
            ? 'bg-orange-100 border-orange-400 ring-2 ring-orange-300'
            : 'bg-orange-50/70 border-orange-200 hover:bg-orange-100/70'"
          @click="toggleExpStatusFilter('week')"
          title="Срок действия меньше недели (1 - 7 дней)"
        >
          <div class="text-[11px] font-semibold text-orange-900 uppercase tracking-wider flex items-center justify-between">
            <span>🟠 &lt; 1 недели</span>
            <i v-if="selectedExpStatus === 'week'" class="pi pi-check text-[10px]"></i>
          </div>
          <div class="text-lg font-bold text-orange-950 font-mono mt-1">
            {{ stats.week || 0 }}
          </div>
          <div class="text-[11px] text-orange-800 mt-0.5">Требует внимания</div>
        </div>

        <!-- < 1 Day / Today (Dark Orange) -->
        <div
          class="p-3 rounded-xl border transition cursor-pointer flex flex-col"
          :class="selectedExpStatus === 'day'
            ? 'bg-amber-200 border-amber-500 ring-2 ring-amber-400'
            : 'bg-amber-100/60 border-amber-300 hover:bg-amber-200/60'"
          @click="toggleExpStatusFilter('day')"
          title="Истекает сегодня (< 24 часов)"
        >
          <div class="text-[11px] font-semibold text-amber-950 uppercase tracking-wider flex items-center justify-between">
            <span>🟤 Сегодня</span>
            <i v-if="selectedExpStatus === 'day'" class="pi pi-check text-[10px]"></i>
          </div>
          <div class="text-lg font-extrabold text-amber-950 font-mono mt-1">
            {{ stats.day || 0 }}
          </div>
          <div class="text-[11px] text-amber-900 mt-0.5">Критично</div>
        </div>

        <!-- Expired (Red) -->
        <div
          class="p-3 rounded-xl border transition cursor-pointer flex flex-col"
          :class="selectedExpStatus === 'expired'
            ? 'bg-rose-100 border-rose-400 ring-2 ring-rose-300'
            : 'bg-rose-50/70 border-rose-200 hover:bg-rose-100/70'"
          @click="toggleExpStatusFilter('expired')"
          title="Срок действия истек"
        >
          <div class="text-[11px] font-semibold text-rose-900 uppercase tracking-wider flex items-center justify-between">
            <span>🔴 Просрочен</span>
            <i v-if="selectedExpStatus === 'expired'" class="pi pi-check text-[10px]"></i>
          </div>
          <div class="text-lg font-bold text-rose-950 font-mono mt-1">
            {{ stats.expired || 0 }}
          </div>
          <div class="text-[11px] text-rose-800 mt-0.5">Не оплачен</div>
        </div>

        <!-- Monthly Volume (SuperAdmin / Manager only) -->
        <div
          v-if="authStore.canEdit"
          class="bg-blue-50/70 p-3 rounded-xl border border-blue-200 shadow-2xs flex flex-col col-span-2 sm:col-span-1"
        >
          <div class="text-[11px] font-semibold text-blue-900 uppercase tracking-wider flex items-center gap-1">
            <i class="pi pi-wallet text-blue-600 text-[10px]"></i>
            Оборот / месяц
          </div>
          <div class="text-base font-bold text-blue-950 font-mono mt-1 truncate" :title="formatCurrency(stats.total_monthly_sum)">
            {{ formatCurrency(stats.total_monthly_sum) }}
          </div>
          <div class="text-[11px] text-blue-700 mt-0.5">Только админ/менеджер</div>
        </div>
      </div>

      <!-- Filter Controls Bar -->
      <div class="bg-white rounded-xl shadow-xs border border-slate-200 p-3 flex flex-wrap items-center justify-between gap-3">
        <div class="flex flex-wrap items-center gap-2.5 flex-1 min-w-[280px]">
          <!-- Search input -->
          <IconField iconPosition="left" class="w-full sm:w-64">
            <InputIcon class="pi pi-search" />
            <InputText
              v-model="searchQuery"
              placeholder="Поиск по компании, городу..."
              class="w-full text-xs"
              @input="onSearchInput"
            />
          </IconField>

          <!-- Service Type filter -->
          <Select
            v-model="selectedServiceType"
            :options="serviceTypeFilterOptions"
            optionLabel="name"
            optionValue="id"
            placeholder="Все виды услуг"
            showClear
            class="w-48 text-xs"
            @change="loadServices"
          />

          <!-- Node Type filter -->
          <Select
            v-model="selectedNodeType"
            :options="nodeTypeFilterOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Все узлы (Сети/RMS)"
            showClear
            class="w-44 text-xs"
            @change="loadServices"
          />

          <!-- Expiration status dropdown filter -->
          <Select
            v-model="selectedExpStatus"
            :options="expStatusOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Все сроки"
            showClear
            class="w-48 text-xs"
            @change="loadServices"
          />
        </div>

        <Button
          v-if="hasActiveFilters"
          label="Сбросить фильтры"
          icon="pi pi-times"
          severity="secondary"
          text
          size="small"
          class="!text-xs"
          @click="resetFilters"
        />
      </div>

      <!-- Main Data Table -->
      <div class="bg-white rounded-xl shadow-xs border border-slate-200 overflow-hidden">
        <DataTable
          :value="services"
          :loading="loading"
          dataKey="id"
          class="p-datatable-sm"
          stripedRows
          hoverableRows
          responsiveLayout="scroll"
        >
          <template #empty>
            <div class="text-center py-12 text-slate-400">
              <i class="pi pi-inbox text-4xl mb-2"></i>
              <p>Подписки и услуги не найдены по заданным критериям.</p>
            </div>
          </template>

          <!-- Company / Establishment Column -->
          <Column header="Компания / Сеть" style="min-width: 250px">
            <template #body="{ data }">
              <div class="flex flex-col">
                <div class="flex items-center gap-1.5 flex-wrap">
                  <!-- Chain Badge -->
                  <span
                    v-if="data.company_node_type === 'CHAIN'"
                    class="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-md bg-purple-50 text-purple-800 border border-purple-200"
                  >
                    <i class="pi pi-sitemap text-[10px]"></i>
                    Chain • {{ data.company_branches_count || 0 }} филиалов
                  </span>

                  <!-- Branch Badge -->
                  <span
                    v-else-if="data.company_parent_chain_name"
                    class="inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 border border-indigo-200"
                  >
                    ↳ {{ data.company_parent_chain_name }}
                  </span>

                  <span class="font-bold text-slate-900">
                    {{ data.company_place_name }}
                  </span>
                </div>

                <span class="text-[11px] text-slate-500 mt-0.5">
                  <span class="font-medium text-slate-600">{{ data.company_city || 'Город не указан' }}</span>
                  <span v-if="data.comment" class="text-slate-400 ml-1.5">• {{ data.comment }}</span>
                </span>
              </div>
            </template>
          </Column>

          <!-- Service Name & Type Badge -->
          <Column header="Услуга" style="min-width: 180px">
            <template #body="{ data }">
              <div class="flex items-center gap-1.5">
                <!-- ITS Badge -->
                <span
                  v-if="data.is_its || data.service_code === 'ITS'"
                  class="inline-flex items-center gap-1 text-xs font-bold px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-900 border border-emerald-300 shadow-2xs"
                  title="ИТС"
                >
                  <i class="pi pi-shield text-[10px] text-emerald-700"></i>
                  {{ data.service_name || 'ИТС' }}
                </span>

                <!-- noIP Badge -->
                <span
                  v-else-if="data.service_code === 'NOIP'"
                  class="inline-flex items-center gap-1 text-xs font-bold px-2 py-0.5 rounded-md bg-blue-100 text-blue-900 border border-blue-300"
                >
                  <i class="pi pi-server text-[10px] text-blue-700"></i>
                  {{ data.service_name || 'Сервер noIP' }}
                </span>

                <!-- WhatsApp Badge -->
                <span
                  v-else-if="data.service_code === 'WHATSAPP'"
                  class="inline-flex items-center gap-1 text-xs font-bold px-2 py-0.5 rounded-md bg-green-100 text-green-900 border border-green-300"
                >
                  <i class="pi pi-whatsapp text-[10px] text-green-700"></i>
                  {{ data.service_name || 'WhatsApp' }}
                </span>

                <!-- Custom Service Badge -->
                <span
                  v-else
                  class="inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-md bg-slate-100 text-slate-800 border border-slate-300"
                >
                  <i class="pi pi-box text-[10px] text-slate-600"></i>
                  {{ data.service_name }}
                </span>
              </div>
            </template>
          </Column>

          <!-- Calculation Method & Tariff -->
          <Column header="Тариф / Расчёт" style="min-width: 170px">
            <template #body="{ data }">
              <div class="text-xs">
                <div class="font-medium text-slate-800">
                  {{ getPeriodLabel(data.period_type) }}
                </div>
                <div class="text-[11px] text-slate-500 mt-0.5">
                  <span v-if="data.pricing_type === 'PER_RMS'" class="text-indigo-600 font-medium">
                    За RMS ({{ formatCurrency(data.cost_per_rms) }} × {{ data.quantity || (data.company_node_type === 'CHAIN' ? Math.max(data.company_branches_count, 1) : 1) }} точ.)
                  </span>
                  <span v-else-if="data.pricing_type === 'PER_FRONT'" class="text-emerald-700 font-medium">
                    За Front ({{ formatCurrency(data.cost_per_rms) }} × {{ data.quantity || data.company_stations_count || 1 }} касс)
                  </span>
                  <span v-else class="text-slate-500">
                    Фиксированная сумма
                  </span>
                </div>
              </div>
            </template>
          </Column>

          <!-- Cost (Visible ONLY to SuperAdmin and Manager) -->
          <Column v-if="authStore.canEdit" header="Стоимость" style="min-width: 130px">
            <template #body="{ data }">
              <div class="font-mono text-sm font-bold text-slate-900">
                {{ formatCurrency(data.total_cost) }}
              </div>
            </template>
          </Column>

          <!-- Expiration Date with Color Gradation -->
          <Column header="Срок действия" :sortable="true" field="expires_at" style="min-width: 220px">
            <template #body="{ data }">
              <div class="flex items-center gap-1.5">
                <span
                  class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-mono border"
                  :class="getExpirationClass(data.days_remaining)"
                >
                  <i class="pi pi-calendar text-[11px]"></i>
                  <span>{{ formatDate(data.expires_at) }}</span>
                  <span class="text-[10px] font-sans font-bold">
                    ({{ formatDaysRemaining(data.days_remaining) }})
                  </span>
                </span>
              </div>
            </template>
          </Column>

          <!-- Status -->
          <Column header="Статус" style="min-width: 100px">
            <template #body="{ data }">
              <Tag
                :value="data.status ? 'Активна' : 'Приостановлена'"
                :severity="data.status ? 'success' : 'secondary'"
                class="!text-[10px]"
              />
            </template>
          </Column>

          <!-- Actions -->
          <Column header="Действия" style="min-width: 150px; text-align: right">
            <template #body="{ data }">
              <div class="flex items-center justify-end gap-1">
                <!-- Quick Renew Button -->
                <Button
                  v-if="authStore.canEdit"
                  icon="pi pi-history"
                  label="Продлить"
                  size="small"
                  severity="success"
                  text
                  class="!text-xs"
                  @click="openQuickRenew(data)"
                  title="Быстрое продление срока действия"
                />

                <!-- Edit Button -->
                <Button
                  v-if="authStore.canEdit"
                  icon="pi pi-pencil"
                  size="small"
                  severity="secondary"
                  text
                  rounded
                  @click="openEditService(data)"
                  title="Редактировать услугу"
                />

                <!-- Duplicate Button -->
                <Button
                  v-if="authStore.canEdit"
                  icon="pi pi-copy"
                  size="small"
                  severity="info"
                  text
                  rounded
                  @click="duplicateService(data)"
                  title="Клонировать услугу для другой компании"
                />

                <!-- Delete Button -->
                <Button
                  v-if="authStore.canEdit"
                  icon="pi pi-trash"
                  size="small"
                  severity="danger"
                  text
                  rounded
                  @click="confirmDeleteService(data)"
                  title="Удалить услугу"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </div>
    </main>

    <!-- Quick Renewal Modal -->
    <Dialog
      v-model:visible="showRenewModal"
      modal
      header="Быстрое продление услуги"
      :style="{ width: '420px' }"
    >
      <div v-if="selectedRenewService" class="flex flex-col gap-4 py-1 text-sm">
        <div class="p-3 bg-slate-50 border border-slate-200 rounded-lg">
          <div class="text-xs text-slate-500 font-medium">Компания:</div>
          <div class="font-bold text-slate-900">{{ selectedRenewService.company_place_name }}</div>
          <div class="text-xs text-slate-500 mt-1 font-medium">Услуга:</div>
          <div class="font-semibold text-emerald-800">{{ selectedRenewService.service_name }}</div>
          <div class="text-xs text-slate-500 mt-1 font-medium">Текущий срок окончания:</div>
          <div class="font-mono font-bold text-slate-800">{{ formatDate(selectedRenewService.expires_at) }}</div>
        </div>

        <div>
          <label class="block text-xs font-bold text-slate-700 uppercase mb-2">Выберите срок продления:</label>
          <div class="grid grid-cols-2 gap-2">
            <Button
              label="+ 1 месяц"
              icon="pi pi-plus"
              severity="secondary"
              outlined
              class="w-full text-xs"
              :loading="renewing"
              @click="handleQuickRenew(1)"
            />
            <Button
              label="+ 3 месяца"
              icon="pi pi-plus"
              severity="secondary"
              outlined
              class="w-full text-xs"
              :loading="renewing"
              @click="handleQuickRenew(3)"
            />
            <Button
              label="+ 6 месяцев"
              icon="pi pi-plus"
              severity="secondary"
              outlined
              class="w-full text-xs"
              :loading="renewing"
              @click="handleQuickRenew(6)"
            />
            <Button
              label="+ 1 год"
              icon="pi pi-plus"
              severity="secondary"
              outlined
              class="w-full text-xs"
              :loading="renewing"
              @click="handleQuickRenew(12)"
            />
          </div>

          <div class="mt-2.5">
            <Button
              label="До 31.12.2026 (базовый срок)"
              icon="pi pi-calendar"
              severity="primary"
              outlined
              class="w-full text-xs"
              :loading="renewing"
              @click="handleDateRenew('2026-12-31')"
            />
          </div>
        </div>

        <div class="border-t border-slate-200 pt-3">
          <label class="block text-xs font-semibold text-slate-600 mb-1">Или укажите точную дату окончания:</label>
          <div class="flex gap-2">
            <input
              type="date"
              v-model="customRenewDate"
              class="flex-1 px-3 py-1.5 border border-slate-300 rounded-lg text-sm font-mono"
            />
            <Button
              label="Применить"
              size="small"
              :disabled="!customRenewDate"
              :loading="renewing"
              @click="handleDateRenew(customRenewDate)"
            />
          </div>
        </div>
      </div>

      <template #footer>
        <Button label="Закрыть" severity="secondary" text @click="showRenewModal = false" />
      </template>
    </Dialog>

    <!-- Add / Edit / Assign Service Modal -->
    <Dialog
      v-model:visible="showServiceModal"
      modal
      :header="modalHeader"
      :style="{ width: '580px' }"
    >
      <div class="flex flex-col gap-4 py-1 text-sm">
        <!-- 1. Company Assignment Block -->
        <div>
          <div class="flex justify-between items-center mb-1">
            <label class="block text-xs font-bold text-slate-700 uppercase">
              Заведение / Сеть *
            </label>
            <button
              v-if="selectedCompany && !isChangingCompany"
              type="button"
              class="text-xs text-indigo-600 hover:text-indigo-800 font-semibold cursor-pointer flex items-center gap-1"
              @click="isChangingCompany = true"
            >
              <i class="pi pi-sync text-[10px]"></i>
              Сменить компанию
            </button>
          </div>

          <!-- Display Selected Company Card -->
          <div
            v-if="selectedCompany && !isChangingCompany"
            class="p-3 bg-gradient-to-r from-slate-50 to-indigo-50/40 border border-slate-200 rounded-xl flex items-center justify-between"
          >
            <div class="flex items-center gap-2.5">
              <div class="w-9 h-9 rounded-lg bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-sm shrink-0">
                <i class="pi pi-building"></i>
              </div>
              <div>
                <div class="font-bold text-slate-900 text-sm flex items-center gap-1.5 flex-wrap">
                  <span>{{ selectedCompany.place_name }}</span>
                  <Tag
                    :value="selectedCompany.node_type === 'CHAIN' ? `Сеть (${selectedCompany.branches_count || 0} фил.)` : (selectedCompany.parent_chain_name ? `Филиал: ${selectedCompany.parent_chain_name}` : 'Точка RMS')"
                    :severity="selectedCompany.node_type === 'CHAIN' ? 'warn' : 'secondary'"
                    class="!text-[9px]"
                  />
                </div>
                <div class="text-[11px] text-slate-500 font-mono mt-0.5">
                  <span v-if="selectedCompany.city">{{ selectedCompany.city }} • </span>
                  <span>{{ selectedCompany.node_type === 'CHAIN' ? `${selectedCompany.branches_count || 1} RMS` : '1 RMS' }}</span>
                  <span v-if="selectedCompany.stations_count"> • {{ selectedCompany.stations_count }} касс (Front)</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Search Company Input (When no company selected or changing company) -->
          <div v-else class="flex flex-col gap-1.5">
            <div class="relative">
              <IconField iconPosition="left">
                <InputIcon class="pi pi-search" />
                <InputText
                  v-model="companySearchInput"
                  placeholder="Начните вводить название заведения (от 3 букв)..."
                  class="w-full text-xs font-medium"
                  @input="onCompanySearchInput"
                  autofocus
                />
              </IconField>
              <div v-if="isSearchingCompany" class="absolute right-3 top-2.5">
                <i class="pi pi-spin pi-spinner text-slate-400 text-xs"></i>
              </div>
            </div>

            <!-- Cancel button if was changing company -->
            <div v-if="selectedCompany && isChangingCompany" class="flex justify-end">
              <button
                type="button"
                class="text-[11px] text-slate-500 hover:text-slate-800 underline cursor-pointer"
                @click="isChangingCompany = false"
              >
                Отмена (оставить {{ selectedCompany.place_name }})
              </button>
            </div>

            <!-- Live Search Results Dropdown -->
            <div
              v-if="companySearchResults.length > 0"
              class="max-h-48 overflow-y-auto border border-indigo-200 rounded-lg bg-white shadow-xl flex flex-col divide-y divide-slate-100 z-50"
            >
              <div
                v-for="comp in companySearchResults"
                :key="comp.id"
                class="p-2.5 hover:bg-indigo-50/80 cursor-pointer transition flex items-center justify-between text-xs"
                @click="chooseCompany(comp)"
              >
                <div>
                  <span class="font-bold text-slate-900">{{ comp.place_name }}</span>
                  <span v-if="comp.city" class="text-slate-500 ml-1.5 font-mono text-[11px]">({{ comp.city }})</span>
                </div>
                <div class="flex items-center gap-1.5">
                  <Tag
                    :value="comp.node_type === 'CHAIN' ? `Сеть (${comp.branches_count || 0})` : (comp.parent_chain_name ? `Филиал` : 'RMS')"
                    :severity="comp.node_type === 'CHAIN' ? 'warn' : 'secondary'"
                    class="!text-[9px]"
                  />
                  <span class="text-slate-400 font-mono text-[11px]">{{ comp.stations_count || 0 }} касс</span>
                </div>
              </div>
            </div>

            <div
              v-else-if="companySearchInput.trim().length >= 3 && !isSearchingCompany && hasSearchedCompanies"
              class="text-[11px] text-slate-400 italic px-1 py-1"
            >
              Заведений по запросу «{{ companySearchInput }}» не найдено
            </div>
            <div
              v-else-if="companySearchInput.trim().length > 0 && companySearchInput.trim().length < 3"
              class="text-[11px] text-amber-600 px-1 py-0.5 font-medium"
            >
              Введите ещё минимум {{ 3 - companySearchInput.trim().length }} символ(а) для поиска
            </div>
          </div>
        </div>

        <!-- 2. Service Catalog Selector + Custom Name -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 border-t border-slate-100">
          <div>
            <label class="block text-xs font-bold text-slate-700 uppercase mb-1">Вид услуги (Каталог) *</label>
            <Select
              v-model="serviceForm.service"
              :options="serviceTypesList"
              optionLabel="name"
              optionValue="id"
              placeholder="Выберите услугу из каталога"
              class="w-full text-xs"
              @change="onServiceTypeSelect"
            />
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-700 uppercase mb-1">
              Название тарифа / услуги
            </label>
            <InputText
              v-model="serviceForm.service_name"
              placeholder="Например: ИТС (Стандарт), VIP"
              class="w-full text-xs"
            />
          </div>
        </div>

        <!-- 3. Individual Properties for this company -->
        <div class="pt-2 border-t border-slate-100 flex flex-col gap-3">
          <div class="text-[11px] font-bold text-slate-500 uppercase tracking-wide">
            Индивидуальные свойства услуги для заведения
          </div>

        <!-- Period Type -->
        <div>
          <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Период подписки</label>
          <Select
            v-model="serviceForm.period_type"
            :options="periodOptions"
            optionLabel="label"
            optionValue="value"
            class="w-full text-xs"
          />
        </div>

        <!-- Pricing Type Selector (Manual vs Per RMS vs Per Front) -->
        <div>
          <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Способ расчёта стоимости</label>
          <Select
            v-model="serviceForm.pricing_type"
            :options="pricingTypeOptions"
            optionLabel="label"
            optionValue="value"
            class="w-full text-xs"
            @change="onPricingTypeChange"
          />
        </div>

        <!-- Price Input Fields for PER_RMS or PER_FRONT -->
        <div v-if="serviceForm.pricing_type === 'PER_RMS' || serviceForm.pricing_type === 'PER_FRONT'" class="p-3.5 bg-indigo-50/70 border border-indigo-200 rounded-xl flex flex-col gap-3">
          <div class="flex justify-between items-center text-xs">
            <span class="text-indigo-900 font-semibold">
              {{ serviceForm.pricing_type === 'PER_RMS' ? 'Точек (RMS) в базе данных:' : 'Касс (Front) в базе данных:' }}
            </span>
            <div class="flex items-center gap-1.5">
              <span class="font-bold font-mono text-indigo-950">
                {{ serviceForm.pricing_type === 'PER_RMS' ? getDatabaseRmsCount(serviceForm.company) : getDatabaseFrontCount(serviceForm.company) }}
                {{ serviceForm.pricing_type === 'PER_RMS' ? 'точ.' : 'касс' }}
              </span>
              <button
                type="button"
                class="text-[10px] text-indigo-600 hover:text-indigo-800 underline font-medium cursor-pointer"
                @click="serviceForm.quantity = (serviceForm.pricing_type === 'PER_RMS' ? getDatabaseRmsCount(serviceForm.company) : getDatabaseFrontCount(serviceForm.company)); recalculateCost()"
              >
                Подставить
              </button>
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-indigo-900 mb-1">
                {{ serviceForm.pricing_type === 'PER_RMS' ? 'Количество точек RMS *' : 'Количество касс Front *' }}
              </label>
              <InputText
                v-model.number="serviceForm.quantity"
                type="number"
                min="1"
                placeholder="1"
                class="w-full font-mono text-sm"
                @input="recalculateCost"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-indigo-900 mb-1">
                {{ serviceForm.pricing_type === 'PER_RMS' ? 'Ставка за 1 RMS в месяц (₸) *' : 'Ставка за 1 Front в месяц (₸) *' }}
              </label>
              <InputText
                v-model.number="serviceForm.cost_per_rms"
                type="number"
                placeholder="Например: 10000"
                class="w-full font-mono text-sm"
                @input="recalculateCost"
              />
            </div>
          </div>

          <div class="flex justify-between items-center text-xs pt-2 border-t border-indigo-200/80">
            <span class="text-indigo-900 font-bold">Итоговая сумма:</span>
            <div class="flex items-baseline gap-2">
              <span class="text-[11px] text-slate-500 font-mono">
                ({{ formatCurrency(serviceForm.cost_per_rms) }} × {{ serviceForm.quantity || 1 }} {{ serviceForm.pricing_type === 'PER_RMS' ? 'точ.' : 'касс' }}) =
              </span>
              <span class="font-mono font-extrabold text-base text-indigo-950">{{ formatCurrency(serviceForm.total_cost) }}</span>
            </div>
          </div>
        </div>

        <div v-else>
          <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Фиксированная стоимость (₸) *</label>
          <InputText
            v-model.number="serviceForm.total_cost"
            type="number"
            placeholder="Например: 50000"
            class="w-full font-mono text-sm"
          />
        </div>

        <!-- Dates: Start Date and Expiration Date -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-bold text-slate-700 uppercase mb-1">Дата начала</label>
            <input
              type="date"
              v-model="serviceForm.start_date"
              class="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm font-mono"
            />
          </div>
          <div>
            <div class="flex justify-between items-center mb-1">
              <label class="block text-xs font-bold text-slate-700 uppercase">Срок действия (до) *</label>
              <div class="flex gap-1">
                <button
                  type="button"
                  class="text-[10px] bg-slate-100 hover:bg-slate-200 text-slate-700 px-1.5 py-0.5 rounded"
                  @click="setFormDate(1)"
                >
                  +1 мес
                </button>
                <button
                  type="button"
                  class="text-[10px] bg-slate-100 hover:bg-slate-200 text-slate-700 px-1.5 py-0.5 rounded"
                  @click="setFormDate(12)"
                >
                  +1 год
                </button>
                <button
                  type="button"
                  class="text-[10px] bg-emerald-100 hover:bg-emerald-200 text-emerald-800 px-1.5 py-0.5 rounded font-bold"
                  @click="serviceForm.expires_at = '2026-12-31'"
                >
                  31.12.2026
                </button>
              </div>
            </div>
            <input
              type="date"
              v-model="serviceForm.expires_at"
              class="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm font-mono"
              required
            />
          </div>
        </div>

        <!-- Comment / Contract -->
        <div>
          <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Номер договора / Примечание</label>
          <InputText
            v-model="serviceForm.comment"
            placeholder="Договор №123 от 01.01.2026..."
            class="w-full text-sm"
          />
        </div>

        <!-- Status -->
        <div class="flex items-center gap-2 pt-1 border-t border-slate-100">
          <Checkbox v-model="serviceForm.status" :binary="true" inputId="srv_status_cb" />
          <label for="srv_status_cb" class="text-xs font-semibold text-slate-800 cursor-pointer">
            Услуга активна (подписка действует)
          </label>
        </div>
      </div>
    </div>

      <template #footer>
        <div class="flex justify-end gap-2">
          <Button label="Отмена" severity="secondary" text @click="showServiceModal = false" />
          <Button
            :label="editingServiceId ? 'Сохранить изменения' : 'Присвоить услугу'"
            icon="pi pi-check"
            :loading="savingService"
            @click="saveService"
          />
        </div>
      </template>
    </Dialog>

    <!-- Catalog Management Modal -->
    <Dialog
      v-model:visible="showCatalogModal"
      modal
      header="Каталог видов услуг"
      :style="{ width: '640px' }"
    >
      <div class="flex flex-col gap-4 py-1 text-sm">
        <div class="flex justify-between items-center">
          <p class="text-xs text-slate-500">Справочник доступных услуг и тарифов компании</p>
          <Button
            v-if="authStore.canEdit"
            label="Новый вид услуги"
            icon="pi pi-plus"
            size="small"
            severity="primary"
            outlined
            @click="openNewTypeForm"
          />
        </div>

        <!-- Inline Form for creating a new service type -->
        <div v-if="showNewTypeForm" class="p-3 bg-slate-50 border border-slate-200 rounded-xl flex flex-col gap-2.5">
          <div class="text-xs font-bold text-slate-800 uppercase">Новый вид услуги:</div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <div>
              <label class="block text-[11px] font-semibold text-slate-600 mb-0.5">Название услуги *</label>
              <InputText v-model="newTypeForm.name" placeholder="Например: Облачный бэкап" class="w-full text-xs" />
            </div>
            <div>
              <label class="block text-[11px] font-semibold text-slate-600 mb-0.5">Системный код (латиница)</label>
              <InputText v-model="newTypeForm.code" placeholder="BACKUP" class="w-full text-xs font-mono" />
            </div>
          </div>
          <div>
            <label class="block text-[11px] font-semibold text-slate-600 mb-0.5">Описание</label>
            <InputText v-model="newTypeForm.description" placeholder="Краткое описание" class="w-full text-xs" />
          </div>
          <div class="flex justify-end gap-2 pt-1">
            <Button label="Отмена" severity="secondary" text size="small" @click="showNewTypeForm = false" />
            <Button label="Добавить в каталог" icon="pi pi-check" size="small" :loading="savingType" @click="saveNewServiceType" />
          </div>
        </div>

        <!-- Catalog List -->
        <div class="flex flex-col gap-2 max-h-80 overflow-y-auto pr-1">
          <div
            v-for="item in serviceTypesList"
            :key="item.id"
            class="p-3 bg-white border border-slate-200 rounded-lg flex items-center justify-between"
          >
            <div>
              <div class="font-bold text-slate-900 flex items-center gap-2">
                <span>{{ item.name }}</span>
                <Tag v-if="item.is_its" value="Базовый ИТС" severity="success" class="!text-[9px]" />
                <span v-if="item.code" class="text-[10px] text-slate-400 font-mono">[{{ item.code }}]</span>
              </div>
              <div v-if="item.description" class="text-xs text-slate-500 mt-0.5">{{ item.description }}</div>
              <div class="text-[11px] text-slate-400 mt-0.5 font-mono">
                Подключений: {{ item.subscriptions_count || 0 }}
              </div>
            </div>

            <div v-if="authStore.canEdit && !item.is_its">
              <Button
                icon="pi pi-trash"
                severity="danger"
                text
                size="small"
                @click="deleteServiceType(item)"
                title="Удалить вид услуги"
              />
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <Button label="Закрыть" severity="secondary" text @click="showCatalogModal = false" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import Tag from 'primevue/tag'
import Dialog from 'primevue/dialog'
import Checkbox from 'primevue/checkbox'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { useAuthStore } from '../stores/auth'
import { servicesApi } from '../api/services'
import { companiesApi } from '../api/companies'
import Navbar from '../components/Navbar.vue'

const toast = useToast()
const confirm = useConfirm()
const authStore = useAuthStore()

const loading = ref(false)
const services = ref([])
const stats = ref({})
const serviceTypesList = ref([])

const searchQuery = ref('')
const selectedServiceType = ref(null)
const selectedNodeType = ref(null)
const selectedExpStatus = ref(null)

const expStatusOptions = [
  { label: '🟢 > 1 месяца (больше 30 дн.)', value: 'over_month' },
  { label: '🟡 8–30 дней (в этом месяце)', value: 'week_month' },
  { label: '🟠 < 1 недели (1–7 дн.)', value: 'week' },
  { label: '🟤 Сегодня (< 24ч)', value: 'day' },
  { label: '🔴 Просроченные', value: 'expired' },
]

const nodeTypeFilterOptions = [
  { label: 'Сети (Chain)', value: 'CHAIN' },
  { label: 'Точки (RMS)', value: 'RMS' },
]

const periodOptions = [
  { label: 'Ежемесячная подписка', value: 'MONTHLY' },
  { label: 'Квартальная', value: 'QUARTERLY' },
  { label: 'Годовая', value: 'YEARLY' },
  { label: 'Разовая услуга', value: 'ONE_TIME' },
]

const pricingTypeOptions = [
  { label: 'Фиксированная сумма', value: 'MANUAL' },
  { label: 'За каждую точку RMS (ставка × кол-во точек)', value: 'PER_RMS' },
  { label: 'За каждый Front (ставка × кол-во касс)', value: 'PER_FRONT' },
]

// Modals
const showRenewModal = ref(false)
const selectedRenewService = ref(null)
const customRenewDate = ref('')
const renewing = ref(false)

const showServiceModal = ref(false)
const editingServiceId = ref(null)
const savingService = ref(false)
const serviceForm = ref({
  company: null,
  service: null,
  service_name: '',
  period_type: 'MONTHLY',
  pricing_type: 'MANUAL',
  cost_per_rms: 0,
  quantity: 1,
  total_cost: 0,
  start_date: '',
  expires_at: '2026-12-31',
  status: true,
  comment: '',
})

// Company selection & dynamic search state (lazy load on >= 3 chars)
const selectedCompany = ref(null)
const isChangingCompany = ref(false)
const companySearchInput = ref('')
const companySearchResults = ref([])
const isSearchingCompany = ref(false)
const hasSearchedCompanies = ref(false)
let companySearchTimeout = null

const modalHeader = computed(() => {
  if (editingServiceId.value) {
    const compName = selectedCompany.value?.place_name || 'заведения'
    return `Свойства услуги для: ${compName}`
  }
  return 'Присвоение услуги заведению'
})

const onCompanySearchInput = () => {
  clearTimeout(companySearchTimeout)
  const q = companySearchInput.value.trim()
  if (q.length < 3) {
    companySearchResults.value = []
    hasSearchedCompanies.value = false
    return
  }
  companySearchTimeout = setTimeout(async () => {
    isSearchingCompany.value = true
    hasSearchedCompanies.value = true
    try {
      const res = await companiesApi.getCompanies({ search: q, page_size: 30 })
      companySearchResults.value = res.data.results || res.data
    } catch (err) {
      companySearchResults.value = []
    } finally {
      isSearchingCompany.value = false
    }
  }, 300)
}

const chooseCompany = (comp) => {
  selectedCompany.value = comp
  serviceForm.value.company = comp.id
  isChangingCompany.value = false
  companySearchInput.value = ''
  companySearchResults.value = []
  hasSearchedCompanies.value = false

  if (serviceForm.value.pricing_type === 'PER_RMS') {
    serviceForm.value.quantity = comp.node_type === 'CHAIN' ? Math.max(comp.branches_count || 0, 1) : 1
  } else if (serviceForm.value.pricing_type === 'PER_FRONT') {
    serviceForm.value.quantity = Math.max(comp.stations_count || comp.anydesk_stations_count || 1, 1)
  }
  recalculateCost()
}

const showCatalogModal = ref(false)
const showNewTypeForm = ref(false)
const savingType = ref(false)
const newTypeForm = ref({ name: '', code: '', description: '' })

let searchTimeout = null
const onSearchInput = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(loadServices, 350)
}

const hasActiveFilters = computed(() => {
  return !!(searchQuery.value.trim() || selectedServiceType.value || selectedNodeType.value || selectedExpStatus.value)
})

const resetFilters = () => {
  searchQuery.value = ''
  selectedServiceType.value = null
  selectedNodeType.value = null
  selectedExpStatus.value = null
  loadServices()
}

const toggleExpStatusFilter = (statusVal) => {
  if (selectedExpStatus.value === statusVal) {
    selectedExpStatus.value = null
  } else {
    selectedExpStatus.value = statusVal
  }
  loadServices()
}

const serviceTypeFilterOptions = computed(() => {
  return serviceTypesList.value.map(s => ({ id: s.id, name: s.name }))
})

const getDatabaseRmsCount = (companyId) => {
  if (selectedCompany.value && (selectedCompany.value.id === companyId || !companyId)) {
    if (selectedCompany.value.node_type === 'CHAIN') {
      return Math.max(selectedCompany.value.branches_count || 0, 1)
    }
    return 1
  }
  return 1
}

const getDatabaseFrontCount = (companyId) => {
  if (selectedCompany.value && (selectedCompany.value.id === companyId || !companyId)) {
    return Math.max(selectedCompany.value.stations_count || selectedCompany.value.anydesk_stations_count || 1, 1)
  }
  return 1
}

const onCompanySelect = () => {
  if (serviceForm.value.pricing_type === 'PER_RMS') {
    serviceForm.value.quantity = getDatabaseRmsCount(serviceForm.value.company)
  } else if (serviceForm.value.pricing_type === 'PER_FRONT') {
    serviceForm.value.quantity = getDatabaseFrontCount(serviceForm.value.company)
  }
  recalculateCost()
}

const onPricingTypeChange = () => {
  if (serviceForm.value.pricing_type === 'PER_RMS') {
    serviceForm.value.quantity = getDatabaseRmsCount(serviceForm.value.company)
  } else if (serviceForm.value.pricing_type === 'PER_FRONT') {
    serviceForm.value.quantity = getDatabaseFrontCount(serviceForm.value.company)
  }
  recalculateCost()
}

const onServiceTypeSelect = () => {
  const srv = serviceTypesList.value.find(s => s.id === serviceForm.value.service)
  if (srv) {
    serviceForm.value.service_name = srv.name
  }
}

const recalculateCost = () => {
  if (serviceForm.value.pricing_type === 'PER_RMS' || serviceForm.value.pricing_type === 'PER_FRONT') {
    const rate = Number(serviceForm.value.cost_per_rms) || 0
    const qty = Number(serviceForm.value.quantity) || 1
    serviceForm.value.total_cost = rate * qty
  }
}

const setFormDate = (months) => {
  const d = new Date()
  d.setMonth(d.getMonth() + months)
  serviceForm.value.expires_at = d.toISOString().split('T')[0]
}

const loadStats = async () => {
  try {
    const res = await servicesApi.getStats()
    stats.value = res.data
  } catch (e) {}
}

const loadServiceTypes = async () => {
  try {
    const res = await servicesApi.getServiceTypes()
    serviceTypesList.value = res.data.results || res.data
  } catch (e) {}
}

const loadServices = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchQuery.value.trim()) params.search = searchQuery.value.trim()
    if (selectedServiceType.value) params.service = selectedServiceType.value
    if (selectedNodeType.value) params.node_type = selectedNodeType.value
    if (selectedExpStatus.value) params.exp_status = selectedExpStatus.value

    const res = await servicesApi.getCompanyServices(params)
    services.value = res.data.results || res.data
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Ошибка', detail: 'Не удалось загрузить список услуг', life: 3000 })
  } finally {
    loading.value = false
  }
}

const refreshData = async () => {
  await Promise.all([loadStats(), loadServices()])
}

// Quick Renew
const openQuickRenew = (sub) => {
  selectedRenewService.value = sub
  customRenewDate.value = ''
  showRenewModal.value = true
}

const handleQuickRenew = async (months) => {
  if (!selectedRenewService.value) return
  renewing.value = true
  try {
    const res = await servicesApi.renewService(selectedRenewService.value.id, { months })
    toast.add({
      severity: 'success',
      summary: 'Услуга продлена',
      detail: `Срок действия успешно продлен до ${formatDate(res.data.expires_at)}`,
      life: 3000,
    })
    showRenewModal.value = false
    await refreshData()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Ошибка продления', detail: err.message, life: 3000 })
  } finally {
    renewing.value = false
  }
}

const handleDateRenew = async (new_date) => {
  if (!selectedRenewService.value || !new_date) return
  renewing.value = true
  try {
    const res = await servicesApi.renewService(selectedRenewService.value.id, { new_date })
    toast.add({
      severity: 'success',
      summary: 'Услуга продлена',
      detail: `Срок действия успешно продлен до ${formatDate(res.data.expires_at)}`,
      life: 3000,
    })
    showRenewModal.value = false
    await refreshData()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Ошибка продления', detail: err.message, life: 3000 })
  } finally {
    renewing.value = false
  }
}

// Add / Edit Service
const openAddServiceModal = () => {
  editingServiceId.value = null
  selectedCompany.value = null
  isChangingCompany.value = false
  companySearchInput.value = ''
  companySearchResults.value = []
  hasSearchedCompanies.value = false

  const itsSrv = serviceTypesList.value.find(s => s.is_its) || serviceTypesList.value[0]
  serviceForm.value = {
    company: null,
    service: itsSrv ? itsSrv.id : null,
    service_name: itsSrv ? itsSrv.name : '',
    period_type: 'MONTHLY',
    pricing_type: 'MANUAL',
    cost_per_rms: 0,
    quantity: 1,
    total_cost: 0,
    start_date: new Date().toISOString().split('T')[0],
    expires_at: '2026-12-31',
    status: true,
    comment: '',
  }
  showServiceModal.value = true
}

const openEditService = (sub) => {
  editingServiceId.value = sub.id
  selectedCompany.value = {
    id: sub.company,
    place_name: sub.company_place_name || 'Заведение',
    city: sub.company_city || '',
    node_type: sub.company_node_type,
    branches_count: sub.company_branches_count,
    stations_count: sub.company_stations_count,
    parent_chain_name: sub.company_parent_chain_name,
  }
  isChangingCompany.value = false
  companySearchInput.value = ''
  companySearchResults.value = []
  hasSearchedCompanies.value = false

  let defaultQty = Number(sub.quantity) || 1
  if (!sub.quantity) {
    if (sub.pricing_type === 'PER_RMS') {
      defaultQty = getDatabaseRmsCount(sub.company)
    } else if (sub.pricing_type === 'PER_FRONT') {
      defaultQty = getDatabaseFrontCount(sub.company)
    }
  }
  serviceForm.value = {
    company: sub.company,
    service: sub.service,
    service_name: sub.service_name,
    period_type: sub.period_type || 'MONTHLY',
    pricing_type: sub.pricing_type || 'MANUAL',
    cost_per_rms: Number(sub.cost_per_rms) || 0,
    quantity: defaultQty,
    total_cost: Number(sub.total_cost) || 0,
    start_date: sub.start_date || '',
    expires_at: sub.expires_at,
    status: sub.status,
    comment: sub.comment || '',
  }
  showServiceModal.value = true
}

const duplicateService = (sub) => {
  editingServiceId.value = null
  selectedCompany.value = null
  isChangingCompany.value = true
  companySearchInput.value = ''
  companySearchResults.value = []
  hasSearchedCompanies.value = false

  serviceForm.value = {
    company: null,
    service: sub.service,
    service_name: sub.service_name || '',
    period_type: sub.period_type || 'MONTHLY',
    pricing_type: sub.pricing_type || 'MANUAL',
    cost_per_rms: Number(sub.cost_per_rms) || 0,
    quantity: 1,
    total_cost: Number(sub.total_cost) || 0,
    start_date: sub.start_date || new Date().toISOString().split('T')[0],
    expires_at: sub.expires_at || '2026-12-31',
    status: true,
    comment: sub.comment || '',
  }
  showServiceModal.value = true
}

const saveService = async () => {
  if (!serviceForm.value.company) {
    toast.add({ severity: 'warn', summary: 'Внимание', detail: 'Выберите заведение для присвоения услуги', life: 3000 })
    return
  }
  if (!serviceForm.value.expires_at) {
    toast.add({ severity: 'warn', summary: 'Внимание', detail: 'Укажите срок действия', life: 3000 })
    return
  }

  savingService.value = true
  try {
    recalculateCost()
    const payload = {
      ...serviceForm.value,
      start_date: serviceForm.value.start_date ? serviceForm.value.start_date : null,
      quantity: Number(serviceForm.value.quantity) || 1,
    }
    if (editingServiceId.value) {
      await servicesApi.updateCompanyService(editingServiceId.value, payload)
      toast.add({ severity: 'success', summary: 'Успешно', detail: 'Данные услуги обновлены', life: 2500 })
    } else {
      await servicesApi.createCompanyService(payload)
      toast.add({ severity: 'success', summary: 'Успешно', detail: 'Услуга успешно подключена', life: 2500 })
    }
    showServiceModal.value = false
    await refreshData()
  } catch (err) {
    const errorMsg = err.response?.data ? JSON.stringify(err.response.data) : err.message
    toast.add({ severity: 'error', summary: 'Ошибка сохранения', detail: errorMsg, life: 4000 })
  } finally {
    savingService.value = false
  }
}

const confirmDeleteService = (sub) => {
  confirm.require({
    message: `Вы уверены, что хотите удалить услугу '${sub.service_name}' для '${sub.company_place_name}'?`,
    header: 'Подтверждение удаления',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Удалить',
    rejectLabel: 'Отмена',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await servicesApi.deleteCompanyService(sub.id)
        toast.add({ severity: 'success', summary: 'Удалено', detail: 'Услуга удалена', life: 2500 })
        await refreshData()
      } catch (err) {
        toast.add({ severity: 'error', summary: 'Ошибка', detail: err.message, life: 3000 })
      }
    },
  })
}

// Catalog Modal Actions
const openCatalogModal = () => {
  showNewTypeForm.value = false
  showCatalogModal.value = true
}

const openNewTypeForm = () => {
  newTypeForm.value = { name: '', code: '', description: '' }
  showNewTypeForm.value = true
}

const saveNewServiceType = async () => {
  if (!newTypeForm.value.name.trim()) {
    toast.add({ severity: 'warn', summary: 'Внимание', detail: 'Укажите название услуги', life: 3000 })
    return
  }
  savingType.value = true
  try {
    await servicesApi.createServiceType(newTypeForm.value)
    toast.add({ severity: 'success', summary: 'Успешно', detail: 'Вид услуги добавлен в каталог', life: 2500 })
    showNewTypeForm.value = false
    await loadServiceTypes()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Ошибка', detail: err.message, life: 3000 })
  } finally {
    savingType.value = false
  }
}

const deleteServiceType = async (item) => {
  confirm.require({
    message: `Удалить вид услуги '${item.name}' из каталога?`,
    header: 'Подтверждение',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Удалить',
    rejectLabel: 'Отмена',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await servicesApi.deleteServiceType(item.id)
        toast.add({ severity: 'success', summary: 'Успешно', detail: 'Вид услуги удален', life: 2500 })
        await loadServiceTypes()
      } catch (err) {
        toast.add({ severity: 'error', summary: 'Ошибка', detail: err.message, life: 3000 })
      }
    },
  })
}

// Formatting helpers
const formatCurrency = (val) => {
  if (val === null || val === undefined || isNaN(val)) return '—'
  return new Intl.NumberFormat('ru-RU').format(Math.round(val)) + ' ₸'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  const d = new Date(dateStr)
  return d.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

const formatDaysRemaining = (days) => {
  if (days === null || days === undefined) return '—'
  if (days < 0) return `просрочен на ${Math.abs(days)} дн.`
  if (days === 0) return 'сегодня'
  if (days === 1) return 'завтра'
  return `ещё ${days} дн.`
}

const getExpirationClass = (days) => {
  if (days === null || days === undefined) return 'bg-slate-50 text-slate-600 border-slate-200'
  if (days > 30) {
    // Green (> 1 month)
    return 'bg-emerald-50 text-emerald-800 border-emerald-300 font-semibold'
  }
  if (days >= 8 && days <= 30) {
    // Yellow / Amber (8 - 30 days)
    return 'bg-amber-50 text-amber-900 border-amber-300 font-semibold'
  }
  if (days >= 1 && days <= 7) {
    // Orange (< 1 week)
    return 'bg-orange-100 text-orange-950 border-orange-400 font-bold'
  }
  if (days === 0) {
    // Dark Orange (< 1 day / Today)
    return 'bg-amber-200 text-amber-950 border-amber-500 font-extrabold animate-pulse'
  }
  // Expired (< 0 days)
  return 'bg-rose-100 text-rose-950 border-rose-400 font-extrabold'
}

const getPeriodLabel = (period) => {
  switch (period) {
    case 'MONTHLY': return 'Ежемесячно'
    case 'QUARTERLY': return 'Квартально'
    case 'YEARLY': return 'Ежегодно'
    case 'ONE_TIME': return 'Разовая'
    default: return period || 'Ежемесячно'
  }
}

onMounted(() => {
  Promise.all([
    loadStats(),
    loadServiceTypes(),
    loadServices(),
  ])
})
</script>
