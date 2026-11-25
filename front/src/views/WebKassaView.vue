<template>
  <div class="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950 transition-colors">
    <Navbar />

    <main class="flex-1 w-full px-4 sm:px-6 lg:px-8 2xl:px-10 py-6 flex flex-col gap-5">
      <!-- Top Title & Action Bar -->
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 class="text-2xl font-bold text-slate-900 dark:text-slate-100 tracking-tight flex items-center gap-2.5">
            <div class="w-8 h-8 rounded-lg bg-sky-500 text-white flex items-center justify-center shadow-xs">
              <i class="pi pi-globe text-sm"></i>
            </div>
            <span>Реестр касс WebKassa</span>
            <span class="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-mono">
              {{ totalCount }} касс
            </span>
            <span
              v-if="selectedGradation"
              class="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-100 dark:bg-blue-950 text-blue-700 dark:text-blue-300 border border-blue-300 dark:border-blue-800 flex items-center gap-1 cursor-pointer"
              title="Нажмите для сброса фильтра дэшборда"
              @click="toggleGradation(null)"
            >
              <span>{{ getGradationLabel(selectedGradation) }}</span>
              <i class="pi pi-times text-[10px]"></i>
            </span>
          </h1>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Учёт фискальных регистраторов, интеграция с ОФД, отслеживание подписок и автоматическая привязка к заведениям
          </p>
        </div>

        <div class="flex items-center gap-2.5 w-full sm:w-auto">
          <!-- Refresh Button -->
          <Button
            icon="pi pi-refresh"
            severity="secondary"
            outlined
            size="small"
            title="Обновить список"
            :loading="loading"
            class="transition-colors cursor-pointer"
            :class="themeStore.isDark ? '!text-slate-200 !border-slate-700 hover:!bg-slate-800' : '!text-slate-600 !border-slate-300 hover:!bg-slate-100'"
            @click="handleRefresh"
          />

          <!-- Upload CSV Button -->
          <Button
            v-if="authStore.canEdit"
            label="Загрузить CSV"
            icon="pi pi-upload"
            severity="primary"
            size="small"
            class="shadow-xs font-semibold"
            @click="showUploadModal = true"
          />
        </div>
      </div>

      <!-- Interactive Expiration Dashboard Cards -->
      <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2.5">
        <!-- 1. Expired -->
        <div
          class="p-2.5 rounded-xl border transition cursor-pointer flex flex-col justify-between"
          :class="selectedGradation === 'expired'
            ? 'bg-rose-500 text-white border-rose-600 shadow-md ring-2 ring-rose-400'
            : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:border-rose-400 dark:hover:border-rose-600 shadow-xs'"
          @click="toggleGradation('expired')"
        >
          <div class="flex items-center justify-between text-[11px] font-semibold" :class="selectedGradation === 'expired' ? 'text-rose-100' : 'text-rose-600 dark:text-rose-400'">
            <span>Просрочено</span>
            <i class="pi pi-times-circle text-xs"></i>
          </div>
          <div class="mt-1 flex items-baseline justify-between">
            <span class="text-xl font-bold font-mono" :class="selectedGradation === 'expired' ? 'text-white' : 'text-slate-900 dark:text-slate-100'">
              {{ dashboardData.expired?.count || 0 }}
            </span>
            <span class="text-[10px]" :class="selectedGradation === 'expired' ? 'text-rose-100' : 'text-slate-400'">
              {{ dashboardData.expired?.companies_count || 0 }} комп.
            </span>
          </div>
        </div>

        <!-- 2. 1 Day -->
        <div
          class="p-2.5 rounded-xl border transition cursor-pointer flex flex-col justify-between"
          :class="selectedGradation === 'day1'
            ? 'bg-red-500 text-white border-red-600 shadow-md ring-2 ring-red-400'
            : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:border-red-400 dark:hover:border-red-600 shadow-xs'"
          @click="toggleGradation('day1')"
        >
          <div class="flex items-center justify-between text-[11px] font-semibold" :class="selectedGradation === 'day1' ? 'text-red-100' : 'text-red-600 dark:text-red-400'">
            <span>1 день</span>
            <i class="pi pi-exclamation-circle text-xs"></i>
          </div>
          <div class="mt-1 flex items-baseline justify-between">
            <span class="text-xl font-bold font-mono" :class="selectedGradation === 'day1' ? 'text-white' : 'text-slate-900 dark:text-slate-100'">
              {{ dashboardData.day1?.count || 0 }}
            </span>
            <span class="text-[10px]" :class="selectedGradation === 'day1' ? 'text-red-100' : 'text-slate-400'">
              {{ dashboardData.day1?.companies_count || 0 }} комп.
            </span>
          </div>
        </div>

        <!-- 3. Up to 3 Days -->
        <div
          class="p-2.5 rounded-xl border transition cursor-pointer flex flex-col justify-between"
          :class="selectedGradation === 'days3'
            ? 'bg-orange-500 text-white border-orange-600 shadow-md ring-2 ring-orange-400'
            : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:border-orange-400 dark:hover:border-orange-600 shadow-xs'"
          @click="toggleGradation('days3')"
        >
          <div class="flex items-center justify-between text-[11px] font-semibold" :class="selectedGradation === 'days3' ? 'text-orange-100' : 'text-orange-600 dark:text-orange-400'">
            <span>До 3 дней</span>
            <i class="pi pi-clock text-xs"></i>
          </div>
          <div class="mt-1 flex items-baseline justify-between">
            <span class="text-xl font-bold font-mono" :class="selectedGradation === 'days3' ? 'text-white' : 'text-slate-900 dark:text-slate-100'">
              {{ dashboardData.days3?.count || 0 }}
            </span>
            <span class="text-[10px]" :class="selectedGradation === 'days3' ? 'text-orange-100' : 'text-slate-400'">
              {{ dashboardData.days3?.companies_count || 0 }} комп.
            </span>
          </div>
        </div>

        <!-- 4. Up to 7 Days -->
        <div
          class="p-2.5 rounded-xl border transition cursor-pointer flex flex-col justify-between"
          :class="selectedGradation === 'days7'
            ? 'bg-amber-500 text-white border-amber-600 shadow-md ring-2 ring-amber-400'
            : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:border-amber-400 dark:hover:border-amber-600 shadow-xs'"
          @click="toggleGradation('days7')"
        >
          <div class="flex items-center justify-between text-[11px] font-semibold" :class="selectedGradation === 'days7' ? 'text-amber-100' : 'text-amber-600 dark:text-amber-400'">
            <span>До 7 дней</span>
            <i class="pi pi-calendar text-xs"></i>
          </div>
          <div class="mt-1 flex items-baseline justify-between">
            <span class="text-xl font-bold font-mono" :class="selectedGradation === 'days7' ? 'text-white' : 'text-slate-900 dark:text-slate-100'">
              {{ dashboardData.days7?.count || 0 }}
            </span>
            <span class="text-[10px]" :class="selectedGradation === 'days7' ? 'text-amber-100' : 'text-slate-400'">
              {{ dashboardData.days7?.companies_count || 0 }} комп.
            </span>
          </div>
        </div>

        <!-- 5. Up to 15 Days -->
        <div
          class="p-2.5 rounded-xl border transition cursor-pointer flex flex-col justify-between"
          :class="selectedGradation === 'days15'
            ? 'bg-blue-500 text-white border-blue-600 shadow-md ring-2 ring-blue-400'
            : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:border-blue-400 dark:hover:border-blue-600 shadow-xs'"
          @click="toggleGradation('days15')"
        >
          <div class="flex items-center justify-between text-[11px] font-semibold" :class="selectedGradation === 'days15' ? 'text-blue-100' : 'text-blue-600 dark:text-blue-400'">
            <span>До 15 дней</span>
            <i class="pi pi-calendar-plus text-xs"></i>
          </div>
          <div class="mt-1 flex items-baseline justify-between">
            <span class="text-xl font-bold font-mono" :class="selectedGradation === 'days15' ? 'text-white' : 'text-slate-900 dark:text-slate-100'">
              {{ dashboardData.days15?.count || 0 }}
            </span>
            <span class="text-[10px]" :class="selectedGradation === 'days15' ? 'text-blue-100' : 'text-slate-400'">
              {{ dashboardData.days15?.companies_count || 0 }} комп.
            </span>
          </div>
        </div>

        <!-- 6. Up to 30 Days -->
        <div
          class="p-2.5 rounded-xl border transition cursor-pointer flex flex-col justify-between"
          :class="selectedGradation === 'days30'
            ? 'bg-indigo-500 text-white border-indigo-600 shadow-md ring-2 ring-indigo-400'
            : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:border-indigo-400 dark:hover:border-indigo-600 shadow-xs'"
          @click="toggleGradation('days30')"
        >
          <div class="flex items-center justify-between text-[11px] font-semibold" :class="selectedGradation === 'days30' ? 'text-indigo-100' : 'text-indigo-600 dark:text-indigo-400'">
            <span>До 30 дней</span>
            <i class="pi pi-bookmark text-xs"></i>
          </div>
          <div class="mt-1 flex items-baseline justify-between">
            <span class="text-xl font-bold font-mono" :class="selectedGradation === 'days30' ? 'text-white' : 'text-slate-900 dark:text-slate-100'">
              {{ dashboardData.days30?.count || 0 }}
            </span>
            <span class="text-[10px]" :class="selectedGradation === 'days30' ? 'text-indigo-100' : 'text-slate-400'">
              {{ dashboardData.days30?.companies_count || 0 }} комп.
            </span>
          </div>
        </div>

        <!-- 7. Active > 30 Days -->
        <div
          class="p-2.5 rounded-xl border transition cursor-pointer flex flex-col justify-between"
          :class="selectedGradation === 'active_over30'
            ? 'bg-emerald-600 text-white border-emerald-700 shadow-md ring-2 ring-emerald-400'
            : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:border-emerald-500 dark:hover:border-emerald-600 shadow-xs'"
          @click="toggleGradation('active_over30')"
        >
          <div class="flex items-center justify-between text-[11px] font-semibold" :class="selectedGradation === 'active_over30' ? 'text-emerald-100' : 'text-emerald-600 dark:text-emerald-400'">
            <span>> 30 дней</span>
            <i class="pi pi-check-circle text-xs"></i>
          </div>
          <div class="mt-1 flex items-baseline justify-between">
            <span class="text-xl font-bold font-mono" :class="selectedGradation === 'active_over30' ? 'text-white' : 'text-slate-900 dark:text-slate-100'">
              {{ dashboardData.active_over30?.count || 0 }}
            </span>
            <span class="text-[10px]" :class="selectedGradation === 'active_over30' ? 'text-emerald-100' : 'text-slate-400'">
              {{ dashboardData.active_over30?.companies_count || 0 }} комп.
            </span>
          </div>
        </div>

        <!-- 8. Total / Unmatched -->
        <div
          class="p-2.5 rounded-xl border transition cursor-pointer flex flex-col justify-between bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 shadow-xs"
          @click="toggleGradation(null)"
        >
          <div class="flex items-center justify-between text-[11px] font-semibold text-slate-500 dark:text-slate-400">
            <span>Всего касс</span>
            <i class="pi pi-database text-xs text-blue-500"></i>
          </div>
          <div class="mt-1 flex items-baseline justify-between">
            <span class="text-xl font-bold font-mono text-slate-900 dark:text-slate-100">
              {{ dashboardData.total || 0 }}
            </span>
            <span
              v-if="dashboardData.unmatched > 0"
              class="text-[10px] font-semibold text-amber-600 dark:text-amber-400"
              title="Касс без привязки к заведению"
            >
              {{ dashboardData.unmatched }} без комп.
            </span>
          </div>
        </div>
      </div>

      <!-- Filters & Search Toolbar -->
      <div class="bg-white dark:bg-slate-900 rounded-xl shadow-xs border border-slate-200 dark:border-slate-800 p-3.5 flex flex-col lg:flex-row justify-between items-start lg:items-center gap-3">
        <div class="flex items-center gap-2.5 flex-wrap w-full lg:w-auto">
          <!-- Search Bar -->
          <div class="w-full sm:w-72">
            <IconField iconPosition="left">
              <InputIcon class="pi pi-search text-xs text-slate-400" />
              <InputText
                v-model="searchQuery"
                placeholder="Поиск по номеру, кассе, БИН, заведению..."
                class="w-full text-xs"
                @input="onSearchInput"
              />
            </IconField>
          </div>

          <!-- Status Filter -->
          <Select
            v-model="selectedStatus"
            :options="statusFilterOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Все статусы"
            class="w-36 text-xs font-medium"
            @change="onFilterChange"
          />

          <!-- OFD Filter -->
          <Select
            v-model="selectedOfd"
            :options="ofdFilterOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Все ОФД"
            class="w-48 text-xs font-medium"
            @change="onFilterChange"
          />

          <!-- Matched Filter -->
          <Select
            v-model="selectedMatched"
            :options="matchedFilterOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Привязка"
            class="w-40 text-xs font-medium"
            @change="onFilterChange"
          />

          <!-- Clear Filters Button -->
          <Button
            v-if="hasActiveFilters"
            icon="pi pi-filter-slash"
            label="Сбросить"
            severity="secondary"
            text
            size="small"
            class="!text-xs !py-1 text-rose-600 dark:text-rose-400"
            @click="resetFilters"
          />
        </div>

        <div class="text-xs text-slate-500 dark:text-slate-400 font-medium">
          Показано: <span class="font-bold text-slate-800 dark:text-slate-200">{{ registers.length }}</span> из {{ totalCount }}
        </div>
      </div>

      <!-- Main WebKassa Table -->
      <div class="bg-white dark:bg-slate-900 rounded-xl shadow-xs border border-slate-200 dark:border-slate-800 overflow-hidden">
        <DataTable
          :value="registers"
          :loading="loading"
          dataKey="id"
          class="p-datatable-sm"
          stripedRows
          hoverableRows
          responsiveLayout="scroll"
          :rowClass="(data) => data.is_active === false ? 'opacity-65 bg-slate-50/70 dark:bg-slate-900/50' : ''"
        >
          <template #empty>
            <div class="text-center py-12 text-slate-400">
              <i class="pi pi-globe text-4xl mb-2 text-slate-300 dark:text-slate-600"></i>
              <p class="text-sm font-medium">Кассы WebKassa не найдены.</p>
              <p class="text-xs text-slate-400 mt-1">Загрузите CSV файл или измените параметры фильтрации.</p>
            </div>
          </template>

          <!-- 1. Linked Company (Привязанное заведение) - First on the left -->
          <Column header="Привязанное заведение" style="min-width: 220px">
            <template #body="{ data }">
              <div v-if="data.company" class="flex flex-col">
                <button
                  type="button"
                  class="text-left font-bold text-blue-600 dark:text-blue-400 hover:underline hover:text-blue-800 dark:hover:text-blue-300 transition cursor-pointer text-xs truncate flex items-center gap-1.5"
                  @click="openCompany(data.company)"
                >
                  <i class="pi pi-building text-[10px]"></i>
                  <span>{{ data.company_place_name }}</span>
                  <Tag
                    v-if="data.company_node_type === 'CHAIN'"
                    value="Сеть"
                    severity="warn"
                    class="!text-[9px] !px-1 font-bold"
                  />
                </button>
                <span class="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5 truncate">
                  {{ data.company_city || 'Без города' }} • {{ data.company_name || '—' }}
                </span>
              </div>

              <!-- Not linked: quick assign button -->
              <div v-else>
                <Button
                  label="Привязать"
                  icon="pi pi-link"
                  size="small"
                  severity="warn"
                  text
                  class="!text-xs !py-1 !px-2 font-semibold"
                  @click="openRegisterDetails(data)"
                />
              </div>
            </template>
          </Column>

          <!-- 2. SWK Номер -->
          <Column header="SWK Номер" style="min-width: 140px">
            <template #body="{ data }">
              <button
                type="button"
                class="font-mono font-bold text-blue-600 dark:text-blue-400 hover:underline hover:text-blue-800 dark:hover:text-blue-300 transition cursor-pointer text-xs flex items-center gap-1.5"
                @click="openRegisterDetails(data)"
                title="Открыть карточку кассы"
              >
                <span>{{ data.serial_number }}</span>
                <i class="pi pi-external-link text-[10px] opacity-70"></i>
              </button>
            </template>
          </Column>

          <!-- 3. Register Name -->
          <Column field="name" header="Название кассы" style="min-width: 170px">
            <template #body="{ data }">
              <span class="font-bold text-slate-800 dark:text-slate-200 text-xs">
                {{ data.name }}
              </span>
            </template>
          </Column>

          <!-- 4. Expiration Date & Days Badge -->
          <Column header="Срок окончания" style="min-width: 160px">
            <template #body="{ data }">
              <div class="flex flex-col">
                <span class="font-bold text-xs" :class="getExpirationClass(data.days_remaining)">
                  {{ formatDate(data.expires_at) }}
                </span>
                <span class="text-[10px] font-mono mt-0.5" :class="getExpirationClass(data.days_remaining)">
                  {{ formatDaysRemaining(data.days_remaining) }}
                </span>
              </div>
            </template>
          </Column>

          <!-- 5. Status -->
          <Column header="Статус ОФД" style="min-width: 130px">
            <template #body="{ data }">
              <Tag
                :value="data.status || '—'"
                :severity="data.status === 'Готова к работе' ? 'success' : 'danger'"
                class="!text-[11px] !px-2 !py-0.5 font-bold"
              />
            </template>
          </Column>

          <!-- 6. OFD -->
          <Column field="ofd" header="ОФД" style="min-width: 160px">
            <template #body="{ data }">
              <span class="text-slate-600 dark:text-slate-400 text-xs">
                {{ data.ofd || '—' }}
              </span>
            </template>
          </Column>

          <!-- 7. Organization / BIN (убрано слово WebKassa) -->
          <Column header="Организация / БИН" style="min-width: 220px">
            <template #body="{ data }">
              <div class="flex flex-col">
                <span class="font-semibold text-slate-800 dark:text-slate-200 text-xs truncate" :title="data.organization">
                  {{ data.organization || '—' }}
                </span>
                <span v-if="data.bin_iin" class="font-mono text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                  БИН: <strong class="text-slate-700 dark:text-slate-300">{{ data.bin_iin }}</strong>
                </span>
              </div>
            </template>
          </Column>

          <!-- 8. Actions with Active Status Icon and Column Filter -->
          <Column style="min-width: 140px; text-align: right">
            <template #header>
              <div class="flex items-center justify-end gap-1.5 w-full">
                <span class="text-xs font-bold text-slate-700 dark:text-slate-200">Действия</span>
                <!-- Filter by active status (icon) -->
                <Select
                  v-model="selectedActive"
                  :options="activeFilterHeaderOptions"
                  optionLabel="label"
                  optionValue="value"
                  size="small"
                  class="!w-7 !h-7 !min-w-0 !p-0 !border-0 !bg-transparent hover:!bg-slate-200 dark:hover:!bg-slate-800 !rounded-lg !shadow-none flex items-center justify-center cursor-pointer transition [&_.p-select-dropdown]:!hidden [&_.p-select-label]:!p-0 [&_.p-select-label]:!flex [&_.p-select-label]:!items-center [&_.p-select-label]:!justify-center"
                  @change="onFilterChange"
                  title="Фильтр активности касс (Все / Активные / Неактивные)"
                >
                  <template #dropdownicon>
                    <span class="hidden"></span>
                  </template>
                  <template #value="{ value }">
                    <span class="w-7 h-7 flex items-center justify-center">
                      <i
                        v-if="value === 'active'"
                        class="pi pi-check text-emerald-600 dark:text-emerald-400 font-bold text-xs"
                      ></i>
                      <i
                        v-else-if="value === 'inactive'"
                        class="pi pi-ban text-rose-600 dark:text-rose-400 font-bold text-xs"
                      ></i>
                      <i
                        v-else
                        class="pi pi-filter text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 text-xs"
                      ></i>
                    </span>
                  </template>
                  <template #option="{ option }">
                    <div class="flex items-center gap-2 text-xs py-0.5">
                      <i v-if="option.value === 'active'" class="pi pi-check text-emerald-600 font-bold"></i>
                      <i v-else-if="option.value === 'inactive'" class="pi pi-ban text-rose-600 font-bold"></i>
                      <i v-else class="pi pi-list text-slate-400"></i>
                      <span>{{ option.label }}</span>
                    </div>
                  </template>
                </Select>
              </div>
            </template>
            <template #body="{ data }">
              <div class="flex items-center justify-end gap-1">
                <!-- Status icon: green checkmark (active) or red crossed circle (inactive) -->
                <button
                  type="button"
                  class="w-7 h-7 rounded-lg flex items-center justify-center transition cursor-pointer select-none"
                  :class="data.is_active !== false
                    ? 'text-emerald-600 dark:text-emerald-400 hover:bg-emerald-50 dark:hover:bg-emerald-950/60'
                    : 'text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/60'"
                  :title="authStore.canEdit
                    ? (data.is_active !== false ? 'Касса активна (нажмите, чтобы деактивировать)' : 'Касса не активна (нажмите, чтобы активировать)')
                    : (data.is_active !== false ? 'Касса активна' : 'Касса не активна')"
                  :disabled="!authStore.canEdit"
                  @click="toggleRegisterActive(data)"
                >
                  <i
                    class="text-sm font-bold"
                    :class="data.is_active !== false ? 'pi pi-check' : 'pi pi-ban'"
                  ></i>
                </button>

                <!-- Edit Button -->
                <Button
                  icon="pi pi-pencil"
                  size="small"
                  severity="secondary"
                  text
                  rounded
                  title="Редактировать / привязать заведение"
                  @click="openRegisterDetails(data)"
                />

                <!-- Delete Button -->
                <Button
                  v-if="authStore.canEdit"
                  icon="pi pi-trash"
                  size="small"
                  severity="danger"
                  text
                  rounded
                  title="Удалить кассу"
                  @click="deleteRegister(data)"
                />
              </div>
            </template>
          </Column>

          <!-- 9. CTO (переименовано в ЦТО) -->
          <Column field="cto" header="ЦТО" style="min-width: 140px">
            <template #body="{ data }">
              <span class="font-medium text-slate-700 dark:text-slate-300 text-xs">
                {{ data.cto || '—' }}
              </span>
            </template>
          </Column>
        </DataTable>

        <!-- Pagination -->
        <div class="p-3 border-t border-slate-200 dark:border-slate-800 flex flex-col md:flex-row justify-between items-center gap-3 text-xs text-slate-600 dark:text-slate-400 bg-slate-50 dark:bg-slate-900/60">
          <div class="flex items-center gap-3 flex-wrap">
            <span class="whitespace-nowrap font-medium text-slate-600 dark:text-slate-300">
              Показано {{ registers.length }} из {{ totalCount }} касс
            </span>
            <div class="flex items-center gap-1.5 border-l border-slate-200 dark:border-slate-700 pl-3">
              <span class="text-slate-500 dark:text-slate-400 whitespace-nowrap">Показывать по:</span>
              <Select
                v-model="pageSize"
                :options="pageSizeOptions"
                optionLabel="label"
                optionValue="value"
                size="small"
                class="w-24 text-xs font-medium"
                style="min-width: 90px"
                @change="onPageSizeChange"
              />
            </div>
          </div>

          <!-- Page Navigation -->
          <div class="flex items-center gap-1 flex-wrap justify-center">
            <button
              type="button"
              class="w-7 h-7 flex items-center justify-center rounded-lg text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-100 hover:bg-slate-200 dark:hover:bg-slate-800 disabled:opacity-30 disabled:pointer-events-none transition cursor-pointer"
              :disabled="currentPage <= 1"
              @click="changePage(1)"
              title="Первая страница"
            >
              <i class="pi pi-angle-double-left text-xs"></i>
            </button>

            <button
              type="button"
              class="w-7 h-7 flex items-center justify-center rounded-lg text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-100 hover:bg-slate-200 dark:hover:bg-slate-800 disabled:opacity-30 disabled:pointer-events-none transition cursor-pointer"
              :disabled="currentPage <= 1"
              @click="changePage(currentPage - 1)"
              title="Предыдущая страница"
            >
              <i class="pi pi-chevron-left text-xs"></i>
            </button>

            <template v-for="(p, idx) in visiblePages" :key="idx">
              <span
                v-if="p === '...'"
                class="w-6 h-7 flex items-center justify-center text-slate-400 dark:text-slate-500 font-mono select-none text-xs"
              >
                ...
              </span>
              <button
                v-else
                type="button"
                @click="changePage(p)"
                class="min-w-7 h-7 px-1.5 flex items-center justify-center rounded-lg text-xs font-mono font-medium transition cursor-pointer"
                :class="p === currentPage
                  ? 'bg-blue-600 text-white font-bold shadow-xs'
                  : 'text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-800 hover:text-blue-600 dark:hover:text-blue-400'"
              >
                {{ p }}
              </button>
            </template>

            <button
              type="button"
              class="w-7 h-7 flex items-center justify-center rounded-lg text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-100 hover:bg-slate-200 dark:hover:bg-slate-800 disabled:opacity-30 disabled:pointer-events-none transition cursor-pointer"
              :disabled="currentPage >= totalPages"
              @click="changePage(currentPage + 1)"
              title="Следующая страница"
            >
              <i class="pi pi-chevron-right text-xs"></i>
            </button>

            <button
              type="button"
              class="w-7 h-7 flex items-center justify-center rounded-lg text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-100 hover:bg-slate-200 dark:hover:bg-slate-800 disabled:opacity-30 disabled:pointer-events-none transition cursor-pointer"
              :disabled="currentPage >= totalPages"
              @click="changePage(totalPages)"
              title="Последняя страница"
            >
              <i class="pi pi-angle-double-right text-xs"></i>
            </button>
          </div>
        </div>
      </div>
    </main>

    <!-- Upload CSV Modal -->
    <WebkassaUploadModal
      v-model:visible="showUploadModal"
      @uploaded="onCsvUploaded"
    />

    <!-- Edit Register / Assign Company Modal -->
    <WebkassaRegisterModal
      v-model:visible="showRegisterModal"
      :register="selectedRegister"
      @saved="onRegisterSaved"
    />

    <!-- Company Detail Drawer -->
    <CompanyDetailDrawer
      v-model="showCompanyDrawer"
      :company-id="selectedCompanyId"
      @updated="loadRegisters"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import Tag from 'primevue/tag'
import Select from 'primevue/select'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { useAuthStore } from '../stores/auth'
import { useThemeStore } from '../stores/theme'
import { webkassaApi } from '../api/webkassa'
import Navbar from '../components/Navbar.vue'
import CompanyDetailDrawer from '../components/CompanyDetailDrawer.vue'
import WebkassaUploadModal from '../components/WebkassaUploadModal.vue'
import WebkassaRegisterModal from '../components/WebkassaRegisterModal.vue'
import { formatDate, formatDaysRemaining } from '../utils/expiration'

const toast = useToast()
const confirm = useConfirm()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const loading = ref(false)
const registers = ref([])
const totalCount = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const pageSizeOptions = [
  { label: '20', value: 20 },
  { label: '50', value: 50 },
  { label: '100', value: 100 },
]
const totalPages = ref(1)

const visiblePages = computed(() => {
  const total = totalPages.value || 1
  const current = currentPage.value

  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1)
  }

  const pages = []

  if (current <= 4) {
    for (let i = 1; i <= 5; i++) pages.push(i)
    pages.push('...')
    pages.push(total)
  } else if (current >= total - 3) {
    pages.push(1)
    pages.push('...')
    for (let i = total - 4; i <= total; i++) pages.push(i)
  } else {
    pages.push(1)
    pages.push('...')
    pages.push(current - 1)
    pages.push(current)
    pages.push(current + 1)
    pages.push('...')
    pages.push(total)
  }

  return pages
})

// Filters
const searchQuery = ref('')
const selectedCto = ref('all')
const ctoList = ref([])
const selectedOfd = ref('all')
const ofdList = ref([])
const selectedStatus = ref('all')
const selectedMatched = ref('all')
const selectedActive = ref('all')
const selectedGradation = ref(null)

const ctoFilterOptions = computed(() => {
  const opts = [{ label: 'Все ЦТО', value: 'all' }]
  ctoList.value.forEach((cto) => {
    if (cto) opts.push({ label: cto, value: cto })
  })
  return opts
})

const ofdFilterOptions = computed(() => {
  const opts = [{ label: 'Все ОФД', value: 'all' }]
  ofdList.value.forEach((ofd) => {
    if (ofd) opts.push({ label: ofd, value: ofd })
  })
  return opts
})

const statusFilterOptions = [
  { label: 'Все статусы ОФД', value: 'all' },
  { label: 'Готова к работе', value: 'Готова к работе' },
  { label: 'Заблокирована', value: 'Заблокирована' },
]

const matchedFilterOptions = [
  { label: 'Все привязки', value: 'all' },
  { label: 'Привязаны к заведению', value: 'matched' },
  { label: 'Без заведения', value: 'unmatched' },
]

const activeFilterOptions = [
  { label: 'Все (активность)', value: 'all' },
  { label: 'Только активные', value: 'active' },
  { label: 'Неактивные', value: 'inactive' },
]

const activeFilterHeaderOptions = [
  { label: 'Все', value: 'all' },
  { label: 'Активные', value: 'active' },
  { label: 'Неактивные', value: 'inactive' },
]

const getActiveFilterHeaderLabel = (val) => {
  if (val === 'active') return 'Активн.'
  if (val === 'inactive') return 'Неакт.'
  return 'Все'
}

const hasActiveFilters = computed(() => {
  return (
    !!searchQuery.value.trim() ||
    selectedOfd.value !== 'all' ||
    selectedStatus.value !== 'all' ||
    selectedMatched.value !== 'all' ||
    selectedActive.value !== 'all' ||
    selectedGradation.value !== null
  )
})

// Dashboard Data
const dashboardData = ref({
  expired: { count: 0, companies_count: 0 },
  day1: { count: 0, companies_count: 0 },
  days3: { count: 0, companies_count: 0 },
  days7: { count: 0, companies_count: 0 },
  days15: { count: 0, companies_count: 0 },
  days30: { count: 0, companies_count: 0 },
  active_over30: { count: 0, companies_count: 0 },
  total: 0,
  matched: 0,
  unmatched: 0,
})

// Modals
const showUploadModal = ref(false)
const showRegisterModal = ref(false)
const selectedRegister = ref(null)

const showCompanyDrawer = ref(false)
const selectedCompanyId = ref(null)

const getGradationLabel = (g) => {
  const map = {
    expired: 'Просрочено',
    day1: '1 день',
    days3: 'До 3 дней',
    days7: 'До 7 дней',
    days15: 'До 15 дней',
    days30: 'До 30 дней',
    active_over30: '> 30 дней',
  }
  return map[g] || g
}

const toggleGradation = (g) => {
  if (selectedGradation.value === g) {
    selectedGradation.value = null
  } else {
    selectedGradation.value = g
  }
  currentPage.value = 1
  loadRegisters()
}

const getExpirationClass = (days) => {
  if (days === null || days === undefined) return 'text-slate-400'
  if (days < 0) return 'text-rose-600 dark:text-rose-400 font-bold'
  if (days <= 3) return 'text-orange-600 dark:text-orange-400 font-bold'
  if (days <= 7) return 'text-amber-600 dark:text-amber-400 font-semibold'
  if (days <= 30) return 'text-blue-600 dark:text-blue-400'
  return 'text-emerald-600 dark:text-emerald-400'
}

let searchTimeout = null
const onSearchInput = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    loadRegisters()
  }, 350)
}

const onFilterChange = () => {
  currentPage.value = 1
  loadRegisters()
  loadDashboard()
}

const onPageSizeChange = () => {
  currentPage.value = 1
  loadRegisters()
}

const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  loadRegisters()
}

const resetFilters = () => {
  searchQuery.value = ''
  selectedCto.value = 'all'
  selectedOfd.value = 'all'
  selectedStatus.value = 'all'
  selectedMatched.value = 'all'
  selectedActive.value = 'all'
  selectedGradation.value = null
  currentPage.value = 1
  loadRegisters()
  loadDashboard()
}

const loadDashboard = async () => {
  try {
    const params = {}
    if (selectedCto.value && selectedCto.value !== 'all') {
      params.cto = selectedCto.value
    }
    if (selectedOfd.value && selectedOfd.value !== 'all') {
      params.ofd = selectedOfd.value
    }
    if (selectedActive.value === 'active') {
      params.is_active = 'true'
    } else if (selectedActive.value === 'inactive') {
      params.is_active = 'false'
    }
    const res = await webkassaApi.getDashboard(params)
    dashboardData.value = res.data || dashboardData.value
  } catch (e) {
    console.error('Ошибка загрузки дэшборда WebKassa:', e)
  }
}

const loadCtoList = async () => {
  try {
    const res = await webkassaApi.getCtoList()
    ctoList.value = res.data || []
  } catch (e) {
    console.error('Ошибка загрузки списка ЦТО:', e)
  }
}

const loadOfdList = async () => {
  try {
    const res = await webkassaApi.getOfdList()
    ofdList.value = res.data || []
  } catch (e) {
    console.error('Ошибка загрузки списка ОФД:', e)
  }
}

const loadRegisters = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (searchQuery.value.trim()) params.search = searchQuery.value.trim()
    if (selectedCto.value && selectedCto.value !== 'all') params.cto = selectedCto.value
    if (selectedOfd.value && selectedOfd.value !== 'all') params.ofd = selectedOfd.value
    if (selectedStatus.value && selectedStatus.value !== 'all') params.status = selectedStatus.value
    if (selectedMatched.value && selectedMatched.value !== 'all') params.matched = selectedMatched.value
    if (selectedActive.value === 'active') params.is_active = 'true'
    else if (selectedActive.value === 'inactive') params.is_active = 'false'
    if (selectedGradation.value) params.gradation = selectedGradation.value

    const res = await webkassaApi.getRegisters(params)
    registers.value = res.data.results || res.data || []
    totalCount.value = res.data.count || registers.value.length
    totalPages.value = Math.ceil(totalCount.value / pageSize.value) || 1
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Не удалось загрузить кассы WebKassa',
      life: 3000,
    })
  } finally {
    loading.value = false
  }
}

const executeActiveChange = async (register, newVal) => {
  const oldVal = register.is_active
  register.is_active = newVal
  try {
    await webkassaApi.updateRegister(register.id, { is_active: newVal })
    toast.add({
      severity: newVal ? 'success' : 'info',
      summary: newVal ? 'Касса активирована' : 'Касса деактивирована',
      detail: `${register.name || register.serial_number}: ${newVal ? 'Активна' : 'Не активна'}`,
      life: 2000,
    })
    loadDashboard()
  } catch (err) {
    register.is_active = oldVal
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: err.message || 'Не удалось изменить статус активности',
      life: 3000,
    })
  }
}

const toggleRegisterActive = (register) => {
  if (!authStore.canEdit) return
  const isCurrentlyActive = register.is_active !== false

  if (isCurrentlyActive) {
    confirm.require({
      message: `Деактивировать кассу «${register.serial_number}» (${register.name || 'WebKassa'})?`,
      header: 'Подтверждение деактивации',
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Да',
      rejectLabel: 'Нет',
      acceptClass: 'p-button-danger',
      rejectClass: 'p-button-secondary p-button-outlined',
      accept: () => {
        executeActiveChange(register, false)
      },
    })
  } else {
    confirm.require({
      message: `Активировать кассу «${register.serial_number}» (${register.name || 'WebKassa'})?`,
      header: 'Подтверждение активации',
      icon: 'pi pi-question-circle',
      acceptLabel: 'Да',
      rejectLabel: 'Нет',
      acceptClass: 'p-button-success',
      rejectClass: 'p-button-secondary p-button-outlined',
      accept: () => {
        executeActiveChange(register, true)
      },
    })
  }
}

const handleRefresh = async () => {
  await Promise.all([loadRegisters(), loadDashboard(), loadCtoList(), loadOfdList()])
  toast.add({ severity: 'info', summary: 'Обновлено', detail: 'Данные касс актуализированы', life: 2000 })
}

const openRegisterDetails = (register) => {
  selectedRegister.value = register
  showRegisterModal.value = true
}

const openCompany = (companyId) => {
  selectedCompanyId.value = companyId
  showCompanyDrawer.value = true
}

const onCsvUploaded = () => {
  loadRegisters()
  loadDashboard()
  loadCtoList()
  loadOfdList()
}

const onRegisterSaved = () => {
  loadRegisters()
  loadDashboard()
}

const deleteRegister = (register) => {
  confirm.require({
    message: `Удалить кассу '${register.serial_number}' (${register.name})?`,
    header: 'Подтверждение удаления',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Удалить',
    rejectLabel: 'Отмена',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await webkassaApi.deleteRegister(register.id)
        toast.add({ severity: 'success', summary: 'Успешно', detail: 'Касса удалена', life: 2500 })
        loadRegisters()
        loadDashboard()
      } catch (err) {
        toast.add({ severity: 'error', summary: 'Ошибка удаления', detail: err.message, life: 3000 })
      }
    },
  })
}

onMounted(() => {
  loadRegisters()
  loadDashboard()
  loadCtoList()
  loadOfdList()
})
</script>
