<template>
  <div class="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950 transition-colors">
    <Navbar />

    <main class="flex-1 w-full px-4 sm:px-6 lg:px-8 2xl:px-10 py-6 flex flex-col gap-5">
      <!-- Top Action & Filter Bar -->
      <div class="bg-white dark:bg-slate-900 rounded-xl shadow-xs border border-slate-200 dark:border-slate-800 p-4 flex flex-col gap-4">
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <div>
            <h1 class="text-xl font-bold text-slate-900 dark:text-slate-100 tracking-tight flex flex-wrap items-center gap-2">
              <span>Клиентская база заведений</span>
              <span
                class="inline-flex items-center gap-1.5 text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 font-mono border border-slate-200 dark:border-slate-700"
                title="Всего заведений в выбранной системе"
              >
                <i class="pi pi-building text-[10px] text-slate-500 dark:text-slate-400"></i>
                Всего: {{ currentTotalCount }}
              </span>
              <span
                class="inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 font-mono"
                title="Количество активных заведений"
              >
                <i class="pi pi-check-circle text-[10px] text-emerald-600 dark:text-emerald-400"></i>
                Активных: {{ activeCount }}
              </span>
              <span
                class="inline-flex items-center gap-1.5 text-xs font-bold px-2.5 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950/80 text-emerald-900 dark:text-emerald-200 border border-emerald-300 dark:border-emerald-700 font-mono shadow-2xs"
                title="ИТС: всего заведений (точек) и количество уникальных компаний/сетей"
              >
                <i class="pi pi-shield text-[10px] text-emerald-700 dark:text-emerald-400"></i>
                <span>На ИТС: {{ itsCount }} всего ({{ itsCompaniesCount }} комп.)</span>
              </span>
              <span
                v-if="isFiltered"
                class="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800 font-mono"
                title="Найдено заведений по текущим фильтрам"
              >
                <i class="pi pi-filter text-[10px] text-blue-500 dark:text-blue-400"></i>
                Найдено: {{ totalCount }}
              </span>
            </h1>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Управление параметрами подключения, серверами и учетными записями</p>
          </div>

          <div class="flex items-center gap-2 w-full sm:w-auto">
            <Button
              v-if="authStore.canEdit"
              label="Добавить заведение"
              icon="pi pi-plus"
              severity="primary"
              size="small"
              @click="openCreateCompany"
            />
            <Button
              label="Все AnyDesk"
              icon="pi pi-desktop"
              severity="secondary"
              outlined
              size="small"
              title="Открыть реестр подключений AnyDesk"
              class="transition-colors cursor-pointer"
              :class="themeStore.isDark ? '!text-slate-200 !border-slate-700 hover:!bg-slate-800' : '!text-slate-700 !border-slate-300 hover:!bg-slate-100'"
              @click="showAnydeskRegistryModal = true"
            />
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
            <Button
              :icon="themeStore.isDark ? 'pi pi-sun' : 'pi pi-moon'"
              severity="secondary"
              outlined
              size="small"
              :title="themeStore.isDark ? 'Переключить на светлую тему' : 'Переключить на тёмную тему'"
              class="transition-colors cursor-pointer"
              :class="themeStore.isDark ? '!text-amber-400 !border-slate-700 hover:!bg-slate-800' : '!text-slate-600 !border-slate-300 hover:!bg-slate-100'"
              @click="themeStore.toggleTheme"
            />
          </div>
        </div>

        <!-- Software System Toggle (iiko vs Rosta) & Node Type Quick Filter -->
        <div class="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-100 dark:border-slate-800">
          <div class="inline-flex p-1 bg-slate-100 dark:bg-slate-800/80 rounded-lg border border-slate-200 dark:border-slate-700">
            <!-- iiko button -->
            <button
              type="button"
              class="px-3.5 py-1.5 text-xs font-bold rounded-md transition-all flex items-center gap-2 cursor-pointer"
              :class="selectedSoftwareType === 'IIKO' ? 'bg-blue-600 text-white shadow-xs' : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white'"
              @click="setSoftwareType('IIKO')"
            >
              <i class="pi pi-server"></i>
              <span>iiko</span>
              <span
                class="px-1.5 py-0.2 rounded-full text-[10px]"
                :class="selectedSoftwareType === 'IIKO' ? 'bg-blue-700 text-white' : 'bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300'"
              >
                {{ filterOptions.iiko_count || 907 }}
              </span>
            </button>

            <!-- Rosta button -->
            <button
              type="button"
              class="px-3.5 py-1.5 text-xs font-bold rounded-md transition-all flex items-center gap-2 cursor-pointer"
              :class="selectedSoftwareType === 'ROSTA' ? 'bg-emerald-600 text-white shadow-xs' : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white'"
              @click="setSoftwareType('ROSTA')"
            >
              <i class="pi pi-tags"></i>
              <span>Rosta</span>
              <span
                class="px-1.5 py-0.2 rounded-full text-[10px]"
                :class="selectedSoftwareType === 'ROSTA' ? 'bg-emerald-700 text-white' : 'bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300'"
              >
                {{ filterOptions.rosta_count || 79 }}
              </span>
            </button>

            <!-- All systems button -->
            <button
              type="button"
              class="px-3 py-1.5 text-xs font-medium rounded-md transition-all flex items-center gap-1.5 cursor-pointer"
              :class="selectedSoftwareType === '' ? 'bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-xs border border-slate-200 dark:border-slate-700' : 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'"
              @click="setSoftwareType('')"
            >
              <span>Все системы</span>
              <span
                class="px-1.5 py-0.2 rounded-full text-[10px]"
                :class="selectedSoftwareType === '' ? 'bg-slate-200 dark:bg-slate-700 text-slate-800 dark:text-slate-200' : 'bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-400'"
              >
                {{ filterOptions.total_count || 985 }}
              </span>
            </button>
          </div>

          <!-- Quick Node Type Filter & Quick AnyDesk -->
          <div class="flex flex-wrap items-center gap-3">
            <!-- Quick Node Type Filter -->
            <div class="flex items-center gap-2">
              <span class="text-xs text-slate-500 dark:text-slate-400 font-medium whitespace-nowrap">Тип заведения:</span>
              <Select
                v-model="selectedNodeType"
                :options="nodeTypeFilterOptions"
                optionLabel="label"
                optionValue="value"
                placeholder="Все типы"
                showClear
                class="w-40 text-xs"
                @change="onFilterChange"
              />
            </div>

            <!-- Quick AnyDesk Launch -->
            <div class="flex items-center gap-1.5 pl-3 border-l border-slate-200 dark:border-slate-700">
              <span class="text-xs text-slate-500 dark:text-slate-400 font-medium whitespace-nowrap">Быстрый AnyDesk:</span>
              <div class="flex items-center gap-1">
                <div class="relative flex items-center">
                  <IconField iconPosition="right">
                    <InputText
                      v-model="quickAnydeskId"
                      placeholder="AnyDesk ID"
                      class="w-38 text-xs font-mono !pr-6"
                      @keydown.enter.stop.prevent="launchQuickAnydesk"
                    />
                    <InputIcon
                      v-if="!quickAnydeskId"
                      class="pi pi-arrow-down-left text-slate-400 dark:text-slate-500 text-[10px]"
                      title="Нажмите Enter для запуска"
                    />
                  </IconField>
                  <button
                    v-if="quickAnydeskId"
                    type="button"
                    class="absolute right-2 text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:hover:text-slate-300 transition cursor-pointer"
                    title="Очистить"
                    @click="quickAnydeskId = ''"
                  >
                    <i class="pi pi-times text-[10px]"></i>
                  </button>
                </div>
                <Button
                  icon="pi pi-arrow-right"
                  severity="danger"
                  size="small"
                  outlined
                  class="!p-1.5 !w-7 !h-7"
                  title="Выбрать профиль и подключиться (Enter)"
                  :disabled="!quickAnydeskId.trim()"
                  @click="launchQuickAnydesk"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Filter Controls Row (7 Columns) -->
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-2.5 pt-3 border-t border-slate-100 dark:border-slate-800">
          <!-- Search input with Reset Filters & Sorting button on the left -->
          <div class="sm:col-span-2 flex items-center gap-1.5">
            <button
              type="button"
              class="self-stretch w-[34px] shrink-0 rounded-lg flex items-center justify-center border transition-all cursor-pointer"
              :class="hasActiveFiltersOrSort
                ? 'bg-rose-50 dark:bg-rose-950/60 border-rose-300 dark:border-rose-700 text-rose-600 dark:text-rose-300 hover:bg-rose-100 dark:hover:bg-rose-900/60 shadow-2xs'
                : 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-400 dark:text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:border-slate-300 dark:hover:border-slate-600 hover:bg-slate-50 dark:hover:bg-slate-700'"
              title="Сбросить все фильтры и сортировку"
              @click="resetAllFiltersAndSorting"
            >
              <i class="pi pi-filter-slash text-sm"></i>
            </button>
            <div class="relative flex-1 min-w-0">
              <IconField iconPosition="left" class="w-full">
                <InputIcon class="pi pi-search" />
                <InputText
                  v-model="searchQuery"
                  placeholder="Поиск (название, CRM, UID, сервер, город)..."
                  class="w-full text-xs !pr-7"
                  @input="onSearchInput"
                />
              </IconField>
              <button
                v-if="searchQuery"
                type="button"
                class="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:hover:text-slate-300 transition cursor-pointer p-0.5"
                title="Очистить поиск"
                @click="clearSearch"
              >
                <i class="pi pi-times text-[10px]"></i>
              </button>
            </div>
          </div>

          <!-- Chain filter (MS Access co_list equivalent) -->
          <div>
            <Select
              v-model="selectedChain"
              :options="filterOptions.chains"
              optionLabel="place_name"
              optionValue="id"
              placeholder="Все сети (ГО)"
              showClear
              filter
              class="w-full text-xs"
              @change="onFilterChange"
            />
          </div>

          <!-- City filter -->
          <div>
            <Select
              v-model="selectedCity"
              :options="filterOptions.cities"
              placeholder="Все города"
              showClear
              filter
              class="w-full text-xs"
              @change="onFilterChange"
            />
          </div>

          <!-- Status filter (Активный / Неактивный) -->
          <div>
            <Select
              v-model="selectedStatus"
              :options="statusOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="Все статусы"
              showClear
              class="w-full text-xs"
              @change="onFilterChange"
            />
          </div>

          <!-- ITS Filter -->
          <div>
            <Select
              v-model="selectedIts"
              :options="itsFilterOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="ИТС (Все)"
              showClear
              class="w-full text-xs"
              @change="onFilterChange"
            />
          </div>

          <!-- Licence Type Filter (replaces Sort filter) -->
          <div>
            <Select
              v-model="selectedLicenceType"
              :options="filterOptions.licence_types"
              placeholder="Тип лицензии"
              showClear
              filter
              class="w-full text-xs"
              @change="onFilterChange"
            />
          </div>
        </div>

        <!-- Active Chain Filter Banner -->
        <div
          v-if="selectedChain"
          class="mt-3 flex items-center justify-between px-3 py-2 bg-indigo-50/90 dark:bg-indigo-950/60 border border-indigo-200 dark:border-indigo-800 rounded-lg text-xs text-indigo-900 dark:text-indigo-200"
        >
          <div class="flex items-center gap-2">
            <i class="pi pi-sitemap text-indigo-600 dark:text-indigo-400 font-bold"></i>
            <span>
              Показаны только заведения сети:
              <strong class="font-bold underline text-indigo-950 dark:text-indigo-100">{{ activeChainName }}</strong>
              (головной узел и все филиалы)
            </span>
          </div>
          <Button
            label="Сбросить фильтр сети"
            icon="pi pi-times"
            severity="secondary"
            size="small"
            text
            class="!text-xs !p-1 text-indigo-700 dark:text-indigo-300 hover:text-indigo-900 dark:hover:text-indigo-100"
            @click="clearChainFilter"
          />
        </div>

        <!-- Active Column Filters Banner (City, Versions, Licence Type, License Status) -->
        <div
          v-if="selectedCities.length > 0 || selectedVersions.length > 0 || selectedLicenceTypes.length > 0 || selectedLicenseStatuses.length > 0"
          class="mt-3 flex flex-wrap items-center gap-2 px-3 py-2 bg-slate-100/90 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg text-xs"
        >
          <span class="text-slate-500 dark:text-slate-400 font-semibold flex items-center gap-1">
            <i class="pi pi-filter text-[11px] text-slate-400"></i>
            Фильтры колонок:
          </span>

          <!-- City Filter Tag -->
          <span
            v-if="selectedCities.length > 0"
            class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-blue-50 dark:bg-blue-950/80 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800 font-medium"
          >
            <span>Города ({{ selectedCities.length }}): <strong>{{ selectedCities.join(', ') }}</strong></span>
            <button
              type="button"
              class="hover:text-blue-900 dark:hover:text-white cursor-pointer ml-0.5"
              title="Сбросить фильтр городов"
              @click="clearCityFilter"
            >
              <i class="pi pi-times text-[10px]"></i>
            </button>
          </span>

          <!-- Version Filter Tag -->
          <span
            v-if="selectedVersions.length > 0"
            class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-indigo-50 dark:bg-indigo-950/80 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 font-medium"
          >
            <span>Версии ({{ selectedVersions.length }}): <strong>{{ selectedVersions.join(', ') }}</strong></span>
            <button
              type="button"
              class="hover:text-indigo-900 dark:hover:text-white cursor-pointer ml-0.5"
              title="Сбросить фильтр версий"
              @click="clearVersionFilter"
            >
              <i class="pi pi-times text-[10px]"></i>
            </button>
          </span>

          <!-- Licence Type Filter Tag -->
          <span
            v-if="selectedLicenceTypes.length > 0"
            class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-purple-50 dark:bg-purple-950/80 text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-800 font-medium"
          >
            <span>Лицензии ({{ selectedLicenceTypes.length }}): <strong>{{ selectedLicenceTypes.join(', ') }}</strong></span>
            <button
              type="button"
              class="hover:text-purple-900 dark:hover:text-white cursor-pointer ml-0.5"
              title="Сбросить фильтр типов лицензий"
              @click="clearLicenceTypeFilter"
            >
              <i class="pi pi-times text-[10px]"></i>
            </button>
          </span>

          <!-- License Status Filter Tag -->
          <span
            v-if="selectedLicenseStatuses.length > 0"
            class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-amber-50 dark:bg-amber-950/80 text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-800 font-medium"
          >
            <span>Состояние лицензий: <strong>{{ getSelectedLicenseStatusesLabels() }}</strong></span>
            <button
              type="button"
              class="hover:text-amber-950 dark:hover:text-white cursor-pointer ml-0.5"
              title="Сбросить фильтр лицензий"
              @click="clearLicenseStatusFilter"
            >
              <i class="pi pi-times text-[10px]"></i>
            </button>
          </span>
        </div>
      </div>

      <!-- Main Data Table -->
      <div class="bg-white dark:bg-slate-900 rounded-xl shadow-xs border border-slate-200 dark:border-slate-800 overflow-hidden">
        <DataTable
          :value="companies"
          :loading="loading"
          :rowClass="rowClass"
          dataKey="id"
          class="p-datatable-sm"
          stripedRows
          hoverableRows
          responsiveLayout="scroll"
          @row-click="onRowClick"
          @sort="onSort"
          :sortField="currentSortField"
          :sortOrder="currentSortOrder"
        >
          <template #empty>
            <div class="text-center py-12 text-slate-400 dark:text-slate-500">
              <i class="pi pi-inbox text-4xl mb-2"></i>
              <p>Заведения не найдены по заданным критериям поиска.</p>
            </div>
          </template>

          <!-- Place Name & City with Chain/RMS hierarchy -->
          <Column field="place_name" :sortable="true" style="min-width: 250px">
            <template #header>
              <div class="flex items-center justify-between gap-1.5 w-full" @click.stop>
                <span class="font-bold text-slate-700 dark:text-slate-200">Заведение / Юр. лицо</span>
                <button
                  type="button"
                  class="relative w-6 h-6 rounded flex items-center justify-center transition cursor-pointer shrink-0"
                  :class="selectedCities.length > 0
                    ? 'bg-blue-100 text-blue-700 dark:bg-blue-950/80 dark:text-blue-300 font-bold border border-blue-300 dark:border-blue-700 shadow-2xs'
                    : 'text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800'"
                  :title="selectedCities.length > 0 ? `Фильтр городов: выбрано ${selectedCities.length}` : 'Фильтр по городам'"
                  @click.stop="toggleCityPopover"
                >
                  <i class="pi pi-map-marker text-[11px]"></i>
                  <span
                    v-if="selectedCities.length > 0"
                    class="absolute -top-1.5 -right-1.5 min-w-[14px] h-[14px] px-0.5 rounded-full bg-blue-600 text-white text-[9px] font-bold flex items-center justify-center shadow-xs"
                  >
                    {{ selectedCities.length }}
                  </span>
                </button>
              </div>
            </template>
            <template #body="{ data }">
              <div class="flex flex-col">
                <div class="flex items-center gap-1.5 flex-wrap">
                  <!-- Chain Node Badge (Clickable to filter this chain) -->
                  <button
                    v-if="data.node_type === 'CHAIN'"
                    type="button"
                    @click.stop="toggleChainFilter(data.id, data.place_name)"
                    class="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-md border transition cursor-pointer group"
                    :class="selectedChain === data.id
                      ? 'bg-purple-700 text-white border-purple-700 shadow-xs ring-2 ring-purple-200 dark:ring-purple-900'
                      : 'text-purple-800 dark:text-purple-200 bg-purple-50 dark:bg-purple-950/60 border-purple-200 dark:border-purple-800 hover:bg-purple-100 dark:hover:bg-purple-900/60'"
                    :title="selectedChain === data.id
                      ? `Нажмите, чтобы сбросить фильтр по сети '${data.place_name}'`
                      : `Показать только сеть '${data.place_name}' (${data.branches_count || 0} филиалов)`"
                  >
                    <i class="pi pi-sitemap text-[10px]"></i>
                    <span>Chain [CO] • {{ data.branches_count || 0 }}</span>
                    <i
                      v-if="selectedChain === data.id"
                      class="pi pi-times text-[9px] ml-0.5 opacity-80 group-hover:opacity-100"
                    ></i>
                    <i
                      v-else
                      class="pi pi-filter text-[9px] opacity-40 group-hover:opacity-100 transition"
                    ></i>
                  </button>

                  <!-- RMS Branch Badge (Clickable to filter its parent chain) -->
                  <button
                    v-else-if="data.parent_chain_name"
                    type="button"
                    @click.stop="toggleChainFilter(data.parent_chain, data.parent_chain_name)"
                    class="inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-md border transition cursor-pointer group"
                    :class="selectedChain === data.parent_chain
                      ? 'bg-indigo-600 text-white border-indigo-600 shadow-xs ring-2 ring-indigo-200 dark:ring-indigo-900'
                      : 'text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/60 border-indigo-200 dark:border-indigo-800 hover:bg-indigo-100 dark:hover:bg-indigo-900/60'"
                    :title="selectedChain === data.parent_chain
                      ? `Нажмите, чтобы сбросить фильтр по сети '${data.parent_chain_name}'`
                      : `Показать сеть '${data.parent_chain_name}' и все её филиалы`"
                  >
                    <span>↳ {{ data.parent_chain_name }}</span>
                    <i
                      v-if="selectedChain === data.parent_chain"
                      class="pi pi-times text-[9px] ml-0.5 opacity-80 group-hover:opacity-100"
                    ></i>
                    <i
                      v-else
                      class="pi pi-filter text-[9px] opacity-40 group-hover:opacity-100 transition"
                    ></i>
                  </button>

                  <!-- Place name with ITS color gradation highlighting & shield/clock/alert badge -->
                  <span
                    class="font-bold transition cursor-pointer inline-flex items-center gap-1.5"
                    :class="data.status && data.helpdesk_its === 'Да' ? getExpirationTextClass(data.its_days_remaining ?? getDaysRemaining(data.its_expires_at), true) : 'text-slate-900 dark:text-slate-100 hover:text-blue-600 dark:hover:text-blue-400'"
                  >
                    <span>{{ data.place_name }}</span>
                    <span
                      v-if="data.status && data.helpdesk_its === 'Да'"
                      class="inline-flex items-center gap-1 text-[10px] font-bold px-1.5 py-0.5 rounded-md shrink-0 shadow-2xs border transition"
                      :class="getExpirationBadgeClass(data.its_days_remaining ?? getDaysRemaining(data.its_expires_at))"
                      :title="getItsTooltip(data)"
                    >
                      <i :class="['text-[9px]', getExpirationIcon(data.its_days_remaining ?? getDaysRemaining(data.its_expires_at))]"></i>
                      <span>ИТС</span>
                      <span
                        v-if="data.its_expires_at && (data.its_days_remaining ?? getDaysRemaining(data.its_expires_at)) !== null && (data.its_days_remaining ?? getDaysRemaining(data.its_expires_at)) <= 30"
                        class="text-[9px] font-mono opacity-90 ml-0.5 font-bold"
                      >
                        {{ formatDaysRemaining(data.its_days_remaining ?? getDaysRemaining(data.its_expires_at)) }}
                      </span>
                    </span>

                    <!-- WebKassa Globe Badge (icon only with color gradation) -->
                    <span
                      v-if="data.webkassa_count > 0"
                      class="inline-flex items-center justify-center w-5 h-5 rounded-md shrink-0 shadow-2xs border transition cursor-pointer"
                      :class="getWebkassaBadgeClass(data.webkassa_days_remaining)"
                      :title="getWebkassaTooltip(data)"
                    >
                      <i class="pi pi-globe text-[11px]" :class="getWebkassaIconClass(data.webkassa_days_remaining)"></i>
                    </span>
                  </span>
                </div>

                <span class="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                  {{ data.company_name || '—' }} • <span class="font-medium text-slate-600 dark:text-slate-300">{{ data.city || 'Город не указан' }}</span>
                </span>
              </div>
            </template>
          </Column>

          <!-- Row Action Buttons (positioned right after venue name) -->
          <Column style="min-width: 110px; width: 110px; text-align: center">
            <template #header>
              <div class="flex items-center justify-center gap-1.5 w-full" @click.stop>
                <span class="font-bold text-slate-700 dark:text-slate-200">Действия</span>
                <button
                  type="button"
                  class="relative w-6 h-6 rounded flex items-center justify-center transition cursor-pointer"
                  :class="selectedLicenseStatuses.length > 0
                    ? 'bg-amber-100 text-amber-800 dark:bg-amber-950/80 dark:text-amber-300 font-bold border border-amber-300 dark:border-amber-700 shadow-2xs'
                    : 'text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800'"
                  :title="selectedLicenseStatuses.length > 0 ? `Фильтр лицензий: выбрано ${selectedLicenseStatuses.length}` : 'Фильтр по состоянию лицензий'"
                  @click.stop="toggleLicenseStatusPopover"
                >
                  <i class="pi pi-filter text-[11px]"></i>
                  <span
                    v-if="selectedLicenseStatuses.length > 0"
                    class="absolute -top-1.5 -right-1.5 min-w-[14px] h-[14px] px-0.5 rounded-full bg-amber-600 text-white text-[9px] font-bold flex items-center justify-center shadow-xs"
                  >
                    {{ selectedLicenseStatuses.length }}
                  </span>
                </button>
              </div>
            </template>
            <template #body="{ data }">
              <div class="flex items-center justify-center gap-0.5" @click.stop>
                <!-- Launch BackOffice (only for iiko) -->
                <Button
                  v-if="data.software_type !== 'ROSTA'"
                  icon="pi pi-play"
                  text
                  rounded
                  size="small"
                  severity="primary"
                  title="Запустить BackOffice через ClearBat"
                  @click="quickLaunchBackoffice(data)"
                />

                <!-- Quick AnyDesk Stations Selection Modal -->
                <Button
                  icon="pi pi-desktop"
                  text
                  rounded
                  size="small"
                  severity="danger"
                  class="!text-red-500 hover:!bg-red-50 dark:hover:!bg-red-950/40"
                  :title="`AnyDesk подключения (${data.anydesk_stations?.length || data.stations_count || 0})`"
                  @click="openCompanyAnydeskList(data)"
                />

                <!-- Current Licenses Modal -->
                <div v-if="data.software_type !== 'ROSTA'" class="relative inline-flex items-center">
                  <Button
                    :icon="data.last_license_error ? 'pi pi-exclamation-triangle' : 'pi pi-id-card'"
                    text
                    rounded
                    size="small"
                    :class="getCompanyLicenseIconClass(data)"
                    :title="getCompanyLicenseTooltip(data)"
                    @click="openCompanyLicense(data)"
                  />
                  <span
                    v-if="data.last_license_error"
                    class="absolute -top-0.5 -right-0.5 w-3.5 h-3.5 rounded-full bg-red-600 text-white flex items-center justify-center text-[9px] font-bold pointer-events-none shadow-xs"
                    :title="`Ошибка обновления: ${data.last_license_error}`"
                  >
                    !
                  </span>
                </div>
              </div>
            </template>
          </Column>

          <!-- CRM ID (iiko only) -->
          <Column v-if="selectedSoftwareType !== 'ROSTA'" field="crm_id" header="CRM ID" style="min-width: 105px; white-space: nowrap">
            <template #body="{ data }">
              <QuickCopyBtn :text="data.crm_id" label="CRM ID" />
            </template>
          </Column>

          <!-- UID (iiko only) - non-wrapping single line -->
          <Column v-if="selectedSoftwareType !== 'ROSTA'" field="uid" header="UID" style="min-width: 150px; white-space: nowrap">
            <template #body="{ data }">
              <div class="whitespace-nowrap">
                <QuickCopyBtn :text="data.uid" label="UID" />
              </div>
            </template>
          </Column>

          <!-- Server / Port - non-wrapping single line -->
          <Column field="server_name" header="Сервер" style="min-width: 230px; white-space: nowrap">
            <template #body="{ data }">
              <div class="flex items-center gap-1 font-mono text-xs whitespace-nowrap">
                <QuickCopyBtn :text="data.server_name" label="Сервер" />
                <span v-if="data.port_number && data.port_number !== '443'" class="text-slate-400 dark:text-slate-500 shrink-0">
                  :{{ data.port_number }}
                </span>
              </div>
            </template>
          </Column>

          <!-- Admin Login -->
          <Column field="system_admin_name" header="Логин" style="min-width: 95px; white-space: nowrap">
            <template #body="{ data }">
              <QuickCopyBtn :text="data.system_admin_name" label="Логин" />
            </template>
          </Column>

          <!-- Admin Password -->
          <Column field="system_admin_password" header="Пароль" style="min-width: 110px; white-space: nowrap">
            <template #body="{ data }">
              <QuickCopyBtn :text="data.system_admin_password" label="Пароль">
                ••••••••
              </QuickCopyBtn>
            </template>
          </Column>

          <!-- License Type -->
          <Column field="licence_type" :sortable="true" style="min-width: 135px; white-space: nowrap">
            <template #header>
              <div class="flex items-center justify-between gap-1 w-full" @click.stop>
                <span class="font-bold text-slate-700 dark:text-slate-200">Лицензия</span>
                <button
                  type="button"
                  class="relative w-6 h-6 rounded flex items-center justify-center transition cursor-pointer shrink-0"
                  :class="selectedLicenceTypes.length > 0
                    ? 'bg-purple-100 text-purple-700 dark:bg-purple-950/80 dark:text-purple-300 font-bold border border-purple-300 dark:border-purple-700 shadow-2xs'
                    : 'text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800'"
                  :title="selectedLicenceTypes.length > 0 ? `Фильтр типов лицензий: выбрано ${selectedLicenceTypes.length}` : 'Фильтр по типу лицензии'"
                  @click.stop="toggleLicenceTypePopover"
                >
                  <i class="pi pi-filter text-[11px]"></i>
                  <span
                    v-if="selectedLicenceTypes.length > 0"
                    class="absolute -top-1.5 -right-1.5 min-w-[14px] h-[14px] px-0.5 rounded-full bg-purple-600 text-white text-[9px] font-bold flex items-center justify-center shadow-xs"
                  >
                    {{ selectedLicenceTypes.length }}
                  </span>
                </button>
              </div>
            </template>
            <template #body="{ data }">
              <span class="text-xs font-medium text-slate-700 dark:text-slate-200 whitespace-nowrap">
                {{ data.licence_type || (data.software_type === 'ROSTA' ? 'Rosta' : '—') }}
              </span>
            </template>
          </Column>

          <!-- Version / Distribution -->
          <Column field="iiko_version" :sortable="true" style="min-width: 130px; white-space: nowrap">
            <template #header>
              <div class="flex items-center justify-between gap-1 w-full" @click.stop>
                <span class="font-bold text-slate-700 dark:text-slate-200">Версия</span>
                <button
                  type="button"
                  class="relative w-6 h-6 rounded flex items-center justify-center transition cursor-pointer"
                  :class="selectedVersions.length > 0
                    ? 'bg-indigo-100 text-indigo-700 dark:bg-indigo-950/80 dark:text-indigo-300 font-bold border border-indigo-300 dark:border-indigo-700 shadow-2xs'
                    : 'text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800'"
                  :title="selectedVersions.length > 0 ? `Фильтр версий: выбрано ${selectedVersions.length}` : 'Фильтр по версии iiko'"
                  @click.stop="toggleVersionPopover"
                >
                  <i class="pi pi-filter text-[11px]"></i>
                  <span
                    v-if="selectedVersions.length > 0"
                    class="absolute -top-1.5 -right-1.5 min-w-[14px] h-[14px] px-0.5 rounded-full bg-indigo-600 text-white text-[9px] font-bold flex items-center justify-center shadow-xs"
                  >
                    {{ selectedVersions.length }}
                  </span>
                </button>
              </div>
            </template>
            <template #body="{ data }">
              <div class="flex items-center gap-1 text-xs whitespace-nowrap">
                <span v-if="data.software_type !== 'ROSTA'" class="font-medium font-mono text-slate-700 dark:text-slate-200">
                  {{ data.iiko_version || '—' }}
                </span>
                <span v-else class="text-emerald-600 dark:text-emerald-400 font-semibold">
                  Rosta
                </span>

                <!-- Copy Distribution Link Button (for iiko with or without distribution_link) -->
                <button
                  v-if="data.software_type !== 'ROSTA' && data.iiko_version"
                  type="button"
                  @click.stop="copyDistributionLink(data)"
                  :title="data.distribution_link ? `Скопировать ссылку на дистрибутив (${data.iiko_version})` : `Для версии '${data.iiko_version}' нет ссылки на скачивание в реестре дистрибутивов`"
                  class="inline-flex items-center justify-center w-5 h-5 rounded transition shrink-0 cursor-pointer ml-0.5"
                  :class="data.distribution_link ? 'text-blue-500 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 hover:bg-blue-50 dark:hover:bg-slate-800' : 'text-red-500 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900/50 hover:bg-red-100 dark:hover:bg-red-900/60'"
                >
                  <i class="pi pi-copy text-[11px]"></i>
                </button>
              </div>
            </template>
          </Column>

          <!-- Status: Активный / Неактивный (No ИСТИНА/ЛОЖЬ) -->
          <Column field="status" header="Статус" :sortable="true" style="min-width: 95px">
            <template #body="{ data }">
              <Tag
                :value="data.status ? 'Активный' : 'Неактивный'"
                :severity="data.status ? 'success' : 'danger'"
                class="!text-[11px] !px-2 !py-0.5 font-medium"
              />
            </template>
          </Column>
        </DataTable>

        <!-- Pagination -->
        <div class="p-3 border-t border-slate-200 dark:border-slate-800 flex flex-col md:flex-row justify-between items-center gap-3 text-xs text-slate-600 dark:text-slate-300 bg-slate-50 dark:bg-slate-900">
          <div class="flex items-center gap-3 flex-wrap">
            <span class="whitespace-nowrap font-medium">Показано {{ companies.length }} из {{ totalCount }} заведений</span>
            <div class="flex items-center gap-1.5 border-l border-slate-200 dark:border-slate-700 pl-3">
              <span class="text-slate-500 dark:text-slate-400 whitespace-nowrap">Показывать по:</span>
              <Select
                v-model="pageSize"
                :options="pageSizeOptions"
                optionLabel="label"
                optionValue="value"
                size="small"
                class="w-24 text-xs font-medium"
                @change="onPageSizeChange"
              />
            </div>
          </div>

          <!-- Page Navigation with Numbers (1, 2, 3, 4 ... 19) -->
          <div class="flex items-center gap-1 flex-wrap justify-center">
            <!-- First Page Button -->
            <button
              type="button"
              class="w-8 h-8 flex items-center justify-center rounded-lg text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-100 hover:bg-slate-200 dark:hover:bg-slate-800 disabled:opacity-30 disabled:pointer-events-none transition cursor-pointer"
              :disabled="currentPage <= 1"
              @click="changePage(1)"
              title="Первая страница"
            >
              <i class="pi pi-angle-double-left text-xs"></i>
            </button>

            <!-- Previous Page Button -->
            <button
              type="button"
              class="w-8 h-8 flex items-center justify-center rounded-lg text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-100 hover:bg-slate-200 dark:hover:bg-slate-800 disabled:opacity-30 disabled:pointer-events-none transition cursor-pointer"
              :disabled="currentPage <= 1"
              @click="changePage(currentPage - 1)"
              title="Предыдущая страница"
            >
              <i class="pi pi-chevron-left text-xs"></i>
            </button>

            <!-- Numbered Pages -->
            <template v-for="(p, idx) in visiblePages" :key="idx">
              <span
                v-if="p === '...'"
                class="w-6 h-8 flex items-center justify-center text-slate-400 dark:text-slate-500 font-mono select-none"
              >
                ...
              </span>
              <button
                v-else
                type="button"
                @click="changePage(p)"
                class="min-w-8 h-8 px-2 flex items-center justify-center rounded-lg text-xs font-mono font-medium transition cursor-pointer"
                :class="p === currentPage
                  ? 'bg-blue-600 text-white font-bold shadow-xs'
                  : 'text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-800 hover:text-blue-600 dark:hover:text-blue-400'"
              >
                {{ p }}
              </button>
            </template>

            <!-- Next Page Button -->
            <button
              type="button"
              class="w-8 h-8 flex items-center justify-center rounded-lg text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-100 hover:bg-slate-200 dark:hover:bg-slate-800 disabled:opacity-30 disabled:pointer-events-none transition cursor-pointer"
              :disabled="currentPage >= totalPages"
              @click="changePage(currentPage + 1)"
              title="Следующая страница"
            >
              <i class="pi pi-chevron-right text-xs"></i>
            </button>

            <!-- Last Page Button -->
            <button
              type="button"
              class="w-8 h-8 flex items-center justify-center rounded-lg text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-100 hover:bg-slate-200 dark:hover:bg-slate-800 disabled:opacity-30 disabled:pointer-events-none transition cursor-pointer"
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

    <!-- Drawer for detailed view/edit -->
    <CompanyDetailDrawer
      v-model="showDrawer"
      :company-id="selectedCompanyId"
      @updated="handleUpdated"
    />

    <!-- Company License Drawer (opened from table actions icon) -->
    <CompanyLicenseDialog
      v-model="showLicenseDialog"
      :company="selectedCompanyForLicense"
      :updating="updatingLicense"
      :status-text="updatingStatusText"
      :as-drawer="true"
      @refresh="handleLaunchLicenseFromTable"
      @reload="handleLicenseReloadFromTable"
    />

    <!-- Quick Anydesk Launch Modal -->
    <AnydeskVersionSelectModal
      v-model="showQuickAnydeskModal"
      :station="quickAnydeskStation"
    />

    <!-- Company AnyDesk Stations Selection Modal (from table desktop icon) -->
    <Dialog
      v-model:visible="showCompanyAnydeskModal"
      modal
      :header="`AnyDesk подключения: ${selectedCompanyForAnydesk?.place_name || ''}`"
      :style="{ width: '520px', maxWidth: '95vw' }"
      :dismissableMask="true"
    >
      <div class="py-2">
        <div v-if="loadingCompanyStations" class="text-center py-8 text-slate-400 dark:text-slate-500">
          <i class="pi pi-spin pi-spinner text-2xl"></i>
        </div>

        <div
          v-else-if="!companyStationsList.length"
          class="text-center py-8 text-slate-400 dark:text-slate-500 text-sm"
        >
          <div class="w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center mx-auto mb-2 text-slate-400">
            <i class="pi pi-desktop text-xl"></i>
          </div>
          <p>К этому заведению еще не привязано ни одного подключения AnyDesk.</p>
          <Button
            label="Открыть карточку заведения"
            icon="pi pi-external-link"
            size="small"
            text
            class="mt-2 text-xs"
            @click="showCompanyAnydeskModal = false; openDetails(selectedCompanyForAnydesk?.id)"
          />
        </div>

        <div v-else class="flex flex-col gap-2 max-h-80 overflow-y-auto pr-1">
          <div
            v-for="st in companyStationsList"
            :key="st.id"
            class="p-3 bg-white dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl flex items-center justify-between hover:border-blue-400 dark:hover:border-blue-500 hover:shadow-xs transition"
          >
            <div class="flex items-center gap-3 min-w-0">
              <div class="w-9 h-9 rounded-lg bg-red-50 dark:bg-red-950/60 text-red-600 dark:text-red-400 flex items-center justify-center shrink-0">
                <i class="pi pi-desktop text-sm"></i>
              </div>
              <div class="flex flex-col min-w-0">
                <span class="font-bold text-slate-900 dark:text-slate-100 text-sm truncate">
                  {{ st.description || 'Рабочее место' }}
                </span>
                <div class="flex items-center gap-2 mt-0.5 flex-wrap">
                  <QuickCopyBtn :text="st.anydesk_id" label="AnyDesk ID" />
                  <span
                    v-if="st.any_pass"
                    class="text-[10px] font-medium text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-1.5 py-0.2 rounded border border-emerald-200 dark:border-emerald-800 flex items-center gap-1"
                    title="Пароль скопируется в буфер при запуске"
                  >
                    <i class="pi pi-check text-[9px]"></i> Пароль
                  </span>
                </div>
              </div>
            </div>

            <Button
              icon="pi pi-play"
              label="Запустить"
              severity="success"
              size="small"
              class="shrink-0 font-semibold !text-xs !px-3"
              @click="launchStationFromModal(st)"
            />
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-between items-center w-full">
          <Button
            label="Закрыть"
            severity="secondary"
            text
            size="small"
            @click="showCompanyAnydeskModal = false"
          />
          <span class="text-xs text-slate-400 dark:text-slate-500">
            Всего подключений: {{ companyStationsList.length }}
          </span>
        </div>
      </template>
    </Dialog>

    <!-- Version Select / Launch Profile Modal for Stations -->
    <AnydeskVersionSelectModal
      v-model="showVersionSelectModal"
      :station="selectedStationForLaunch"
    />

    <!-- Global AnyDesk Registry Modal -->
    <AnydeskRegistryModal
      v-model:visible="showAnydeskRegistryModal"
      @open-company="handleOpenCompanyFromAnydesk"
    />

    <!-- Column Header Filter: iiko Version Popover -->
    <Popover ref="versionPopover">
      <div class="w-64 p-2 flex flex-col gap-2 text-xs">
        <div class="flex items-center justify-between pb-1.5 border-b border-slate-100 dark:border-slate-800">
          <span class="font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
            <i class="pi pi-code text-indigo-600 dark:text-indigo-400 text-xs"></i>
            Фильтр версий
          </span>
          <button
            v-if="selectedVersions.length > 0"
            type="button"
            class="text-[11px] text-rose-500 hover:text-rose-700 dark:hover:text-rose-400 cursor-pointer font-medium"
            @click="clearVersionFilter"
          >
            Сбросить ({{ selectedVersions.length }})
          </button>
        </div>

        <!-- Search input -->
        <div class="relative">
          <IconField iconPosition="left" class="w-full">
            <InputIcon class="pi pi-search text-xs text-slate-400" />
            <InputText
              v-model="versionSearchQuery"
              placeholder="Поиск версии..."
              class="w-full !text-xs !py-1 !pl-7 !pr-6"
            />
          </IconField>
          <button
            v-if="versionSearchQuery"
            type="button"
            class="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 text-[10px] cursor-pointer"
            @click="versionSearchQuery = ''"
          >
            <i class="pi pi-times"></i>
          </button>
        </div>

        <!-- Counter info -->
        <div class="text-[10px] text-slate-400 dark:text-slate-500 px-1 flex items-center justify-between">
          <span>Все доступные версии ({{ displayedVersionsList.length }}):</span>
          <span v-if="selectedVersions.length > 0" class="text-indigo-600 dark:text-indigo-400 font-semibold">
            Выбрано: {{ selectedVersions.length }}
          </span>
        </div>

        <!-- Checkbox list -->
        <div class="max-h-60 overflow-y-auto flex flex-col gap-1 pr-1 divide-y divide-slate-100 dark:divide-slate-800/60">
          <label
            v-for="ver in displayedVersionsList"
            :key="ver"
            class="flex items-center gap-2 p-1.5 rounded hover:bg-slate-100 dark:hover:bg-slate-800 cursor-pointer select-none transition"
          >
            <Checkbox
              v-model="selectedVersions"
              :value="ver"
              @change="onVersionFilterChange"
            />
            <span class="font-mono text-xs text-slate-800 dark:text-slate-200">{{ ver }}</span>
          </label>
          <div
            v-if="displayedVersionsList.length === 0"
            class="text-slate-400 dark:text-slate-500 text-center py-3 text-xs italic"
          >
            Версий не найдено
          </div>
        </div>
      </div>
    </Popover>

    <!-- Column Header Filter: License Status Popover -->
    <Popover ref="licenseStatusPopover">
      <div class="w-64 p-2 flex flex-col gap-2 text-xs">
        <div class="flex items-center justify-between pb-1.5 border-b border-slate-100 dark:border-slate-800">
          <span class="font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
            <i class="pi pi-id-card text-amber-600 dark:text-amber-400 text-xs"></i>
            Состояние лицензий
          </span>
          <button
            v-if="selectedLicenseStatuses.length > 0"
            type="button"
            class="text-[11px] text-rose-500 hover:text-rose-700 dark:hover:text-rose-400 cursor-pointer font-medium"
            @click="clearLicenseStatusFilter"
          >
            Сбросить ({{ selectedLicenseStatuses.length }})
          </button>
        </div>

        <!-- Checkbox list of statuses -->
        <div class="flex flex-col gap-1 pt-1">
          <label
            v-for="st in licenseStatusOptions"
            :key="st.value"
            class="flex items-center justify-between p-1.5 rounded hover:bg-slate-100 dark:hover:bg-slate-800 cursor-pointer select-none transition"
          >
            <div class="flex items-center gap-2">
              <Checkbox
                v-model="selectedLicenseStatuses"
                :value="st.value"
                @change="onLicenseStatusFilterChange"
              />
              <span class="flex items-center gap-1.5 font-medium text-slate-800 dark:text-slate-200">
                <span :class="st.dotClass" class="w-2.5 h-2.5 rounded-full inline-block shrink-0"></span>
                <span>{{ st.label }}</span>
              </span>
            </div>
            <span class="text-[10px] text-slate-400 dark:text-slate-500 font-mono">{{ st.desc }}</span>
          </label>
        </div>
      </div>
    </Popover>

    <!-- Column Header Filter: City Popover -->
    <Popover ref="cityPopover">
      <div class="w-64 p-2 flex flex-col gap-2 text-xs">
        <div class="flex items-center justify-between pb-1.5 border-b border-slate-100 dark:border-slate-800">
          <span class="font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
            <i class="pi pi-map-marker text-blue-600 dark:text-blue-400 text-xs"></i>
            Фильтр по городам
          </span>
          <button
            v-if="selectedCities.length > 0"
            type="button"
            class="text-[11px] text-rose-500 hover:text-rose-700 dark:hover:text-rose-400 cursor-pointer font-medium"
            @click="clearCityFilter"
          >
            Сбросить ({{ selectedCities.length }})
          </button>
        </div>

        <!-- Search input for City -->
        <div class="relative">
          <IconField iconPosition="left" class="w-full">
            <InputIcon class="pi pi-search text-xs text-slate-400" />
            <InputText
              v-model="citySearchQuery"
              placeholder="Поиск города..."
              class="w-full !text-xs !py-1 !pl-7 !pr-6"
            />
          </IconField>
          <button
            v-if="citySearchQuery"
            type="button"
            class="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 text-[10px] cursor-pointer"
            @click="citySearchQuery = ''"
          >
            <i class="pi pi-times"></i>
          </button>
        </div>

        <!-- Checkbox list of cities -->
        <div class="max-h-52 overflow-y-auto flex flex-col gap-1 pr-1 divide-y divide-slate-100 dark:divide-slate-800/60">
          <label
            v-for="c in displayedCitiesList"
            :key="c"
            class="flex items-center gap-2 p-1.5 rounded hover:bg-slate-100 dark:hover:bg-slate-800 cursor-pointer select-none transition"
          >
            <Checkbox
              v-model="selectedCities"
              :value="c"
              @change="onCityFilterChange"
            />
            <span class="text-xs text-slate-800 dark:text-slate-200">{{ c }}</span>
          </label>
          <div
            v-if="displayedCitiesList.length === 0"
            class="text-slate-400 dark:text-slate-500 text-center py-3 text-xs italic"
          >
            Городов не найдено
          </div>
        </div>
      </div>
    </Popover>

    <!-- Column Header Filter: Licence Type Popover -->
    <Popover ref="licenceTypePopover">
      <div class="w-64 p-2 flex flex-col gap-2 text-xs">
        <div class="flex items-center justify-between pb-1.5 border-b border-slate-100 dark:border-slate-800">
          <span class="font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
            <i class="pi pi-id-card text-purple-600 dark:text-purple-400 text-xs"></i>
            Тип лицензии
          </span>
          <button
            v-if="selectedLicenceTypes.length > 0"
            type="button"
            class="text-[11px] text-rose-500 hover:text-rose-700 dark:hover:text-rose-400 cursor-pointer font-medium"
            @click="clearLicenceTypeFilter"
          >
            Сбросить ({{ selectedLicenceTypes.length }})
          </button>
        </div>

        <!-- Search input for Licence Type -->
        <div class="relative">
          <IconField iconPosition="left" class="w-full">
            <InputIcon class="pi pi-search text-xs text-slate-400" />
            <InputText
              v-model="licenceTypeSearchQuery"
              placeholder="Поиск типа лицензии..."
              class="w-full !text-xs !py-1 !pl-7 !pr-6"
            />
          </IconField>
          <button
            v-if="licenceTypeSearchQuery"
            type="button"
            class="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 text-[10px] cursor-pointer"
            @click="licenceTypeSearchQuery = ''"
          >
            <i class="pi pi-times"></i>
          </button>
        </div>

        <!-- Checkbox list of licence types -->
        <div class="max-h-52 overflow-y-auto flex flex-col gap-1 pr-1 divide-y divide-slate-100 dark:divide-slate-800/60">
          <label
            v-for="lt in displayedLicenceTypesList"
            :key="lt"
            class="flex items-center gap-2 p-1.5 rounded hover:bg-slate-100 dark:hover:bg-slate-800 cursor-pointer select-none transition"
          >
            <Checkbox
              v-model="selectedLicenceTypes"
              :value="lt"
              @change="onLicenceTypeFilterChange"
            />
            <span class="text-xs text-slate-800 dark:text-slate-200 font-medium">{{ lt }}</span>
          </label>
          <div
            v-if="displayedLicenceTypesList.length === 0"
            class="text-slate-400 dark:text-slate-500 text-center py-3 text-xs italic"
          >
            Типов лицензий не найдено
          </div>
        </div>
      </div>
    </Popover>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import Select from 'primevue/select'
import Tag from 'primevue/tag'
import Popover from 'primevue/popover'
import Checkbox from 'primevue/checkbox'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { useAuthStore } from '../stores/auth'
import { useCompanionStore } from '../stores/companion'
import { useThemeStore } from '../stores/theme'
import { companiesApi } from '../api/companies'
import Navbar from '../components/Navbar.vue'
import QuickCopyBtn from '../components/QuickCopyBtn.vue'
import CompanyDetailDrawer from '../components/CompanyDetailDrawer.vue'
import AnydeskVersionSelectModal from '../components/AnydeskVersionSelectModal.vue'
import AnydeskRegistryModal from '../components/AnydeskRegistryModal.vue'
import CompanyLicenseDialog from '../components/CompanyLicenseDialog.vue'
import { anydeskApi } from '../api/anydesk'
import { matchesSmartSearch } from '../utils/keyboard'
import {
  getDaysRemaining,
  getExpirationBadgeClass,
  getExpirationTextClass,
  getExpirationIcon,
  getItsTooltip,
  getWebkassaBadgeClass,
  getWebkassaIconClass,
  getWebkassaTooltip,
  formatDaysRemaining,
  formatDate,
  getLicenseIconClass,
  getLicenseTooltip,
  getLicenseStatus,
} from '../utils/expiration'

const toast = useToast()
const confirm = useConfirm()
const authStore = useAuthStore()
const companionStore = useCompanionStore()
const themeStore = useThemeStore()

const loading = ref(false)
const companies = ref([])
const totalCount = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const pageSizeOptions = [
  { label: '20', value: 20 },
  { label: '50', value: 50 },
  { label: '100', value: 100 },
]

const onPageSizeChange = () => {
  currentPage.value = 1
  loadCompanies()
}
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

const searchQuery = ref('')
const selectedSoftwareType = ref('IIKO')
const selectedNodeType = ref(null)
const selectedChain = ref(null)
const selectedCity = ref(null)
const selectedStatus = ref(null)
const selectedBusinessType = ref(null)
const selectedLicenceType = ref(null)
const selectedOrdering = ref('chain_smart')

const filterOptions = ref({
  cities: [],
  business_types: [],
  licence_types: [],
  iiko_rosta: [],
  chains: [],
  total_count: 0,
  active_count: 0,
  its_count: 0,
  its_companies_count: 0,
  iiko_count: 0,
  iiko_active_count: 0,
  iiko_its_count: 0,
  iiko_its_companies_count: 0,
  rosta_count: 0,
  rosta_active_count: 0,
  rosta_its_count: 0,
  rosta_its_companies_count: 0,
})

const activeCount = computed(() => {
  if (selectedSoftwareType.value === 'IIKO') return filterOptions.value.iiko_active_count || 0
  if (selectedSoftwareType.value === 'ROSTA') return filterOptions.value.rosta_active_count || 0
  return filterOptions.value.active_count || 0
})

const itsCount = computed(() => {
  if (selectedSoftwareType.value === 'IIKO') return filterOptions.value.iiko_its_count || 0
  if (selectedSoftwareType.value === 'ROSTA') return filterOptions.value.rosta_its_count || 0
  return filterOptions.value.its_count || 0
})

const itsCompaniesCount = computed(() => {
  if (selectedSoftwareType.value === 'IIKO') return filterOptions.value.iiko_its_companies_count || 0
  if (selectedSoftwareType.value === 'ROSTA') return filterOptions.value.rosta_its_companies_count || 0
  return filterOptions.value.its_companies_count || 0
})

const currentTotalCount = computed(() => {
  if (selectedSoftwareType.value === 'IIKO') return filterOptions.value.iiko_count || 0
  if (selectedSoftwareType.value === 'ROSTA') return filterOptions.value.rosta_count || 0
  return filterOptions.value.total_count || 0
})

const isFiltered = computed(() => {
  return !!(
    searchQuery.value.trim() ||
    selectedChain.value ||
    selectedCity.value ||
    (selectedStatus.value !== null && selectedStatus.value !== undefined && selectedStatus.value !== '') ||
    selectedIts.value ||
    selectedNodeType.value
  )
})

const hasActiveFiltersOrSort = computed(() => {
  return !!(
    searchQuery.value.trim() ||
    selectedNodeType.value ||
    selectedChain.value ||
    selectedCity.value ||
    selectedCities.value.length > 0 ||
    (selectedStatus.value !== null && selectedStatus.value !== undefined && selectedStatus.value !== '') ||
    selectedIts.value ||
    selectedLicenceType.value ||
    selectedLicenceTypes.value.length > 0 ||
    selectedBusinessType.value ||
    selectedVersions.value.length > 0 ||
    selectedLicenseStatuses.value.length > 0 ||
    (selectedOrdering.value && selectedOrdering.value !== 'chain_smart')
  )
})

const statusOptions = [
  { label: 'Активный', value: 'true' },
  { label: 'Неактивный', value: 'false' },
]

const nodeTypeFilterOptions = [
  { label: 'Сети (Chain)', value: 'CHAIN' },
  { label: 'Точки (RMS)', value: 'RMS' },
]

const selectedIts = ref(null)
const itsFilterOptions = [
  { label: 'ИТС: Все на ИТС', value: 'yes' },
  { label: '🟢 ИТС > 1 месяца', value: 'over_month' },
  { label: '🟡 ИТС 8–30 дней', value: 'week_month' },
  { label: '🟠 ИТС < 1 недели', value: 'week' },
  { label: '🟤 ИТС Сегодня', value: 'day' },
  { label: '🔴 ИТС Просроченные', value: 'expired' },
  { label: 'Без ИТС (Нет)', value: 'no' },
]

const showDrawer = ref(false)
const selectedCompanyId = ref(null)
const showAnydeskRegistryModal = ref(false)

const handleOpenCompanyFromAnydesk = (companyId) => {
  showAnydeskRegistryModal.value = false
  if (companyId) {
    selectedCompanyId.value = companyId
    showDrawer.value = true
  }
}

// Column header filters: city
const cityPopover = ref(null)
const citySearchQuery = ref('')
const selectedCities = ref([])

const displayedCitiesList = computed(() => {
  const all = filterOptions.value?.cities || []
  const q = citySearchQuery.value.trim()
  if (!q) return all
  return all.filter(c => c && matchesSmartSearch(c, q))
})

const toggleCityPopover = (event) => {
  cityPopover.value?.toggle(event)
}

const onCityFilterChange = () => {
  currentPage.value = 1
  loadCompanies()
}

const clearCityFilter = () => {
  selectedCities.value = []
  citySearchQuery.value = ''
  currentPage.value = 1
  loadCompanies()
}

// Column header filters: iiko_version
const versionPopover = ref(null)
const versionSearchQuery = ref('')
const selectedVersions = ref([])

const displayedVersionsList = computed(() => {
  const allVersions = filterOptions.value?.iiko_versions || []
  const q = versionSearchQuery.value.trim()
  if (!q) return allVersions
  return allVersions.filter(v => matchesSmartSearch(v, q))
})

const toggleVersionPopover = (event) => {
  versionPopover.value?.toggle(event)
}

const onVersionFilterChange = () => {
  currentPage.value = 1
  loadCompanies()
}

const clearVersionFilter = () => {
  selectedVersions.value = []
  versionSearchQuery.value = ''
  currentPage.value = 1
  loadCompanies()
}

// Column header filters: license_status
const licenseStatusPopover = ref(null)
const selectedLicenseStatuses = ref([])

const licenseStatusOptions = [
  { value: 'active', label: 'Действующая', desc: 'Активна', dotClass: 'bg-emerald-500' },
  { value: 'error', label: 'С ошибками', desc: 'Ошибка', dotClass: 'bg-red-500' },
  { value: 'expired', label: 'Просроченная', desc: 'Истекла', dotClass: 'bg-amber-500' },
  { value: 'not_requested', label: 'Не запрошенная', desc: 'Нет данных', dotClass: 'bg-slate-400' },
]

const toggleLicenseStatusPopover = (event) => {
  licenseStatusPopover.value?.toggle(event)
}

const onLicenseStatusFilterChange = () => {
  currentPage.value = 1
  loadCompanies()
}

const clearLicenseStatusFilter = () => {
  selectedLicenseStatuses.value = []
  currentPage.value = 1
  loadCompanies()
}

const getSelectedLicenseStatusesLabels = () => {
  return selectedLicenseStatuses.value
    .map(val => licenseStatusOptions.find(o => o.value === val)?.label || val)
    .join(', ')
}

// Column header filters: licence_type
const licenceTypePopover = ref(null)
const licenceTypeSearchQuery = ref('')
const selectedLicenceTypes = ref([])

const displayedLicenceTypesList = computed(() => {
  const all = filterOptions.value?.licence_types || []
  const q = licenceTypeSearchQuery.value.trim()
  if (!q) return all
  return all.filter(lt => lt && matchesSmartSearch(lt, q))
})

const toggleLicenceTypePopover = (event) => {
  licenceTypePopover.value?.toggle(event)
}

const onLicenceTypeFilterChange = () => {
  currentPage.value = 1
  loadCompanies()
}

const clearLicenceTypeFilter = () => {
  selectedLicenceTypes.value = []
  licenceTypeSearchQuery.value = ''
  currentPage.value = 1
  loadCompanies()
}

const showCompanyAnydeskModal = ref(false)
const selectedCompanyForAnydesk = ref(null)
const companyStationsList = ref([])
const loadingCompanyStations = ref(false)
const showVersionSelectModal = ref(false)
const selectedStationForLaunch = ref(null)

const showLicenseDialog = ref(false)
const selectedCompanyForLicense = ref(null)
const updatingLicense = ref(false)
const updatingStatusText = ref('')

const openCompanyLicense = async (comp) => {
  selectedCompanyForLicense.value = comp
  showLicenseDialog.value = true
  if (comp.id) {
    try {
      const res = await companiesApi.getCompany(comp.id)
      if (res.data) {
        selectedCompanyForLicense.value = res.data
        const idx = companies.value.findIndex(item => item.id === comp.id)
        if (idx !== -1) {
          companies.value[idx] = res.data
        }
      }
    } catch (e) {}
  }
}

const handleLicenseReloadFromTable = (freshCompany) => {
  if (freshCompany) {
    selectedCompanyForLicense.value = freshCompany
    const idx = companies.value.findIndex(item => item.id === freshCompany.id)
    if (idx !== -1) {
      companies.value[idx] = freshCompany
    }
    loadCompanies()
    loadFilterOptions()
  }
}

const handleLaunchLicenseFromTable = async () => {
  const c = selectedCompanyForLicense.value
  if (!c) return

  const serverName = (c.server_name || '').trim()
  if (!serverName) {
    toast.add({
      severity: 'warn',
      summary: 'Отсутствует адрес сервера',
      detail: 'Адрес сервера не заполнен. Запрос на обновление лицензии не может быть отправлен.',
      life: 5000,
    })
    return
  }

  let licenseUrl = ''
  let plainPass = c.system_admin_password || ''
  try {
    const p = await companiesApi.getClearbatParams(c.id)
    licenseUrl = p.data.license_url
    if (p.data && p.data.password) plainPass = p.data.password
  } catch (e) {}

  if (companionStore.isOnline) {
    updatingLicense.value = true
    updatingStatusText.value = 'Запуск ClearBat и подключение к серверу iiko...'
    toast.add({
      severity: 'info',
      summary: 'Обновление лицензии',
      detail: 'Запрос отправлен в ClearBat. Ожидание ответа сервера iiko...',
      life: 4000,
    })

    try {
      const res = await companionStore.launchLicense({
        company_id: c.id,
        server: c.server_name,
        port: c.port_number || '443',
        login: c.system_admin_name || 'iikoadm',
        password: plainPass,
        place_name: c.place_name,
        licenseUrl,
      })

      const taskId = res?.task_id

      if (taskId) {
        const pollRes = await companionStore.pollLicenseTaskStatus(taskId, c.id, {
          maxAttempts: 14,
          intervalMs: 2500,
          onAttempt: (attempt, max) => {
            const elapsedSec = (attempt - 1) * 2.5
            if (elapsedSec < 5) {
              updatingStatusText.value = `Запуск ClearBat и подключение к серверу iiko... (${attempt}/${max})`
            } else if (elapsedSec < 15) {
              updatingStatusText.value = `Ожидание формирования лицензий сервером iiko... (${attempt}/${max})`
            } else {
              updatingStatusText.value = `Завершение синхронизации сведений о лицензии... (${attempt}/${max})`
            }
          }
        })

        if (pollRes.success) {
          const wasInactive = !c.status
          let autoActivated = false
          let freshCompany = null
          try {
            const compRes = await companiesApi.getCompany(c.id)
            if (compRes.data) {
              freshCompany = compRes.data
              selectedCompanyForLicense.value = compRes.data
              const idx = companies.value.findIndex(item => item.id === c.id)
              if (idx !== -1) {
                companies.value[idx] = compRes.data
              }
              if (wasInactive && compRes.data.status) {
                autoActivated = true
              }
            }
          } catch (e) {}

          loadFilterOptions()
          loadCompanies()

          const isNewVer = pollRes.data?.is_new_version || false
          const currentVer = pollRes.data?.iiko_version || freshCompany?.iiko_version || ''

          if (isNewVer) {
            toast.add({
              severity: 'warn',
              summary: 'Новая версия iiko!',
              detail: `Версия iiko новая (${currentVer}) — добавлена в справочник дистрибутивов, необходимо заполнить поле со ссылкой!`,
              life: 8000,
            })
          }

          const modCount = pollRes.data?.modules_count || selectedCompanyForLicense.value?.license_data?.modules?.length || 0
          toast.add({
            severity: 'success',
            summary: autoActivated ? 'Лицензия обновлена (Заведение активировано!)' : 'Лицензия обновлена',
            detail: `Данные лицензии успешно сохранены в базе! Активных модулей: ${modCount}${autoActivated ? ' • Заведение стало активным' : ''}`,
            life: 5000,
          })
        } else if (pollRes.error && !pollRes.timeout) {
          try {
            const compRes = await companiesApi.get(c.id)
            if (compRes.data) {
              selectedCompanyForLicense.value = compRes.data
              const idx = companies.value.findIndex(item => item.id === c.id)
              if (idx !== -1) {
                companies.value[idx] = compRes.data
              }
            }
          } catch (e) {}

          toast.add({
            severity: 'error',
            summary: 'Ошибка сервера iiko',
            detail: pollRes.error,
            life: 6000,
          })
        } else if (pollRes.timeout) {
          toast.add({
            severity: 'warn',
            summary: 'Таймаут ожидания',
            detail: 'Не удалось получить ответ от сервера iiko за 30 секунд. Проверьте запущен ли ClearBat и Companion Helper.',
            life: 6000,
          })
        }
      }
    } catch (err) {
      toast.add({
        severity: 'error',
        summary: 'Ошибка отправки',
        detail: err.message || 'Не удалось отправить команду обновления',
        life: 4000,
      })
    } finally {
      updatingLicense.value = false
      updatingStatusText.value = ''
    }
  } else if (licenseUrl) {
    window.location.href = licenseUrl
    toast.add({
      severity: 'info',
      summary: 'Обновление лицензии',
      detail: 'Запрос на обновление отправлен через протокол clearbat://',
      life: 3000,
    })
  }
}

const openCompanyAnydeskList = async (comp) => {
  selectedCompanyForAnydesk.value = comp
  showCompanyAnydeskModal.value = true
  if (comp.anydesk_stations && comp.anydesk_stations.length) {
    companyStationsList.value = comp.anydesk_stations
  } else {
    loadingCompanyStations.value = true
    try {
      const res = await companiesApi.getCompany(comp.id)
      companyStationsList.value = res.data.anydesk_stations || []
      comp.anydesk_stations = res.data.anydesk_stations || []
    } catch (e) {
      companyStationsList.value = []
    } finally {
      loadingCompanyStations.value = false
    }
  }
}

const launchStationFromModal = (st) => {
  selectedStationForLaunch.value = {
    ...st,
    description: st.description || selectedCompanyForAnydesk.value?.place_name || 'Рабочее место',
  }
  showCompanyAnydeskModal.value = false
  showVersionSelectModal.value = true
}

const quickAnydeskId = ref('')
const showQuickAnydeskModal = ref(false)
const quickAnydeskStation = ref(null)

const launchQuickAnydesk = async () => {
  const rawId = quickAnydeskId.value.trim()
  if (!rawId) {
    toast.add({
      severity: 'warn',
      summary: 'AnyDesk ID',
      detail: 'Введите AnyDesk ID для подключения',
      life: 2500,
    })
    return
  }

  const cleanDigits = rawId.replace(/\D/g, '')
  let matchedStation = null

  if (cleanDigits) {
    try {
      const res = await anydeskApi.getAnydeskStations({ search: rawId })
      const results = res.data?.results || res.data || []
      matchedStation = results.find(
        (s) => s.anydesk_id && s.anydesk_id.replace(/\D/g, '') === cleanDigits
      )
    } catch (e) {
      // Ignore lookup errors
    }
  }

  if (matchedStation) {
    quickAnydeskStation.value = {
      anydesk_id: matchedStation.anydesk_id,
      description: matchedStation.company_name
        ? `${matchedStation.company_name} (${matchedStation.description || 'Рабочее место'})`
        : (matchedStation.description || 'Быстрое подключение'),
      any_pass: matchedStation.any_pass || '',
    }
  } else {
    quickAnydeskStation.value = {
      anydesk_id: rawId,
      description: 'Быстрое подключение',
      any_pass: '',
    }
  }

  showQuickAnydeskModal.value = true
}

let searchTimeout = null
const onSearchInput = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    loadCompanies()
  }, 350)
}

const setSoftwareType = (type) => {
  selectedSoftwareType.value = type
  currentPage.value = 1
  loadCompanies()
}

const currentSortField = computed(() => {
  if (!selectedOrdering.value || selectedOrdering.value === 'chain_smart') return null
  if (selectedOrdering.value.startsWith('-')) {
    return selectedOrdering.value.slice(1)
  }
  return selectedOrdering.value
})

const currentSortOrder = computed(() => {
  if (!selectedOrdering.value || selectedOrdering.value === 'chain_smart') return null
  return selectedOrdering.value.startsWith('-') ? -1 : 1
})

const onSort = (event) => {
  if (event.sortField) {
    if (event.sortOrder === -1) {
      selectedOrdering.value = `-${event.sortField}`
    } else {
      selectedOrdering.value = event.sortField
    }
    currentPage.value = 1
    loadCompanies()
  }
}

const onFilterChange = () => {
  currentPage.value = 1
  loadCompanies()
}

const activeChainName = computed(() => {
  if (!selectedChain.value) return ''
  const c = filterOptions.value.chains?.find((ch) => ch.id === selectedChain.value)
  return c ? c.place_name : `Сеть #${selectedChain.value}`
})

const clearSearch = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
    searchTimeout = null
  }
  searchQuery.value = ''
  currentPage.value = 1
  loadCompanies()
}

const resetAllFiltersAndSorting = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
    searchTimeout = null
  }
  searchQuery.value = ''
  selectedNodeType.value = null
  selectedChain.value = null
  selectedCity.value = null
  selectedStatus.value = null
  selectedIts.value = null
  selectedLicenceType.value = null
  selectedBusinessType.value = null
  selectedOrdering.value = 'chain_smart'
  selectedCities.value = []
  citySearchQuery.value = ''
  selectedVersions.value = []
  versionSearchQuery.value = ''
  selectedLicenceTypes.value = []
  licenceTypeSearchQuery.value = ''
  selectedLicenseStatuses.value = []
  currentPage.value = 1
  loadCompanies()
  toast.add({
    severity: 'info',
    summary: 'Фильтры сброшены',
    detail: 'Все фильтры и сортировка сброшены к значениям по умолчанию',
    life: 2500,
  })
}

const clearChainFilter = () => {
  selectedChain.value = null
  currentPage.value = 1
  loadCompanies()
  toast.add({
    severity: 'info',
    summary: 'Фильтр сброшен',
    detail: 'Отображаются все заведения и сети',
    life: 2500,
  })
}

const toggleChainFilter = (chainId, chainName) => {
  if (selectedChain.value === chainId) {
    selectedChain.value = null
    toast.add({
      severity: 'info',
      summary: 'Фильтр сброшен',
      detail: 'Отображаются все заведения и сети',
      life: 2500,
    })
  } else {
    selectedChain.value = chainId
    toast.add({
      severity: 'info',
      summary: 'Фильтр по сети',
      detail: `Отображается сеть: '${chainName}' (ГО и филиалы)`,
      life: 3000,
    })
  }
  currentPage.value = 1
  loadCompanies()
}

const rowClass = (data) => {
  if (data.status && data.helpdesk_its === 'Да') {
    return 'bg-emerald-50/30 dark:bg-emerald-950/20 hover:!bg-emerald-50/70 dark:hover:!bg-emerald-950/40 border-l-4 border-l-emerald-600 dark:border-l-emerald-500 transition-colors'
  }
  return ''
}

const handleRefresh = async () => {
  await Promise.all([loadFilterOptions(), loadCompanies()])
}

const handleUpdated = () => {
  loadFilterOptions()
  loadCompanies()
}

const loadFilterOptions = async () => {
  try {
    const res = await companiesApi.getFilterOptions()
    filterOptions.value = res.data
  } catch (e) {
    console.error('Ошибка загрузки опций фильтрации:', e)
  }
}

const loadCompanies = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (searchQuery.value.trim()) params.search = searchQuery.value.trim()
    if (selectedSoftwareType.value) params.software_type = selectedSoftwareType.value
    if (selectedNodeType.value) params.node_type = selectedNodeType.value
    if (selectedChain.value) params.chain_id = selectedChain.value

    const allCities = [...selectedCities.value]
    if (selectedCity.value && !allCities.includes(selectedCity.value)) {
      allCities.push(selectedCity.value)
    }
    if (allCities.length > 0) {
      params.city = allCities.join(',')
    }

    if (selectedStatus.value !== null && selectedStatus.value !== undefined && selectedStatus.value !== '') {
      params.status = selectedStatus.value
    }
    if (selectedIts.value) params.its = selectedIts.value

    const allLicTypes = [...selectedLicenceTypes.value]
    if (selectedLicenceType.value && !allLicTypes.includes(selectedLicenceType.value)) {
      allLicTypes.push(selectedLicenceType.value)
    }
    if (allLicTypes.length > 0) {
      params.licence_type = allLicTypes.join(',')
    }

    if (selectedBusinessType.value) params.business_type = selectedBusinessType.value
    if (selectedOrdering.value) params.ordering = selectedOrdering.value
    if (selectedVersions.value && selectedVersions.value.length > 0) {
      params.iiko_version = selectedVersions.value.join(',')
    }
    if (selectedLicenseStatuses.value && selectedLicenseStatuses.value.length > 0) {
      params.license_status = selectedLicenseStatuses.value.join(',')
    }

    const res = await companiesApi.getCompanies(params)
    companies.value = res.data.results || res.data
    totalCount.value = res.data.count || companies.value.length
    totalPages.value = Math.ceil(totalCount.value / pageSize.value)
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Ошибка', detail: 'Не удалось загрузить список заведений', life: 3000 })
  } finally {
    loading.value = false
  }
}

const changePage = (page) => {
  currentPage.value = page
  loadCompanies()
}

const onRowClick = (event) => {
  openDetails(event.data.id)
}

const openDetails = (id) => {
  selectedCompanyId.value = id
  showDrawer.value = true
}

const openCreateCompany = () => {
  selectedCompanyId.value = null
  showDrawer.value = true
}

const quickLaunchBackoffice = async (company) => {
  let clearbatUrl = ''
  try {
    const p = await companiesApi.getClearbatParams(company.id)
    clearbatUrl = p.data.clearbat_url
  } catch (e) {}

  const res = await companionStore.launchBackoffice({
    server: company.server_name,
    port: company.port_number || '443',
    login: company.system_admin_name || 'iikoadm',
    password: company.system_admin_password || '',
    clearbatUrl,
  })

  toast.add({
    severity: res.success ? 'success' : 'warn',
    summary: 'BackOffice',
    detail: res.message,
    life: 3000,
  })
}

const copyDistributionLink = async (company) => {
  const link = company.distribution_link
  if (!link) {
    toast.add({
      severity: 'warn',
      summary: 'Нет ссылки для этой версии',
      detail: `Для версии '${company.iiko_version || '—'}' нет ссылки на скачивание в реестре дистрибутивов`,
      life: 4000,
    })
    return
  }

  // Follow Form_Company_list.md logic: link & "?=" & server_name
  const server = (company.server_name || '').trim()
  const copyText = server ? `${link}?=${server}` : link

  try {
    await navigator.clipboard.writeText(copyText)
    toast.add({
      severity: 'success',
      summary: 'Ссылка скопирована',
      detail: `Адрес ссылки: '${copyText}' на скачивание iiko Office скопирован в буфер обмена!`,
      life: 4000,
    })
  } catch (err) {
    const textArea = document.createElement('textarea')
    textArea.value = copyText
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    toast.add({
      severity: 'success',
      summary: 'Ссылка скопирована',
      detail: `Адрес ссылки: '${copyText}' на скачивание iiko Office скопирован в буфер обмена!`,
      life: 4000,
    })
  }
}

const deleteCompany = (company) => {
  confirm.require({
    message: `Вы действительно хотите удалить заведение '${company.place_name}' и все связанные станции AnyDesk?`,
    header: 'Удаление заведения',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Удалить',
    rejectLabel: 'Отмена',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await companiesApi.deleteCompany(company.id)
        toast.add({ severity: 'success', summary: 'Успешно', detail: 'Заведение удалено', life: 2500 })
        loadCompanies()
      } catch (err) {
        toast.add({ severity: 'error', summary: 'Ошибка', detail: err.message, life: 3000 })
      }
    },
  })
}

const keyModulesVersion = ref(0)
const onKeyModulesUpdated = () => {
  keyModulesVersion.value++
}

const getCompanyLicenseIconClass = (company) => {
  const _ = keyModulesVersion.value
  return getLicenseIconClass(company)
}

const getCompanyLicenseTooltip = (company) => {
  const _ = keyModulesVersion.value
  return getLicenseTooltip(company)
}

onMounted(() => {
  window.addEventListener('ksz_key_modules_updated', onKeyModulesUpdated)
  loadFilterOptions()
  loadCompanies()
})

onUnmounted(() => {
  window.removeEventListener('ksz_key_modules_updated', onKeyModulesUpdated)
})
</script>
