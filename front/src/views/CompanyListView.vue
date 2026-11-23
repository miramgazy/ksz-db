<template>
  <div class="min-h-screen flex flex-col bg-slate-50">
    <Navbar />

    <main class="flex-1 w-full px-4 sm:px-6 lg:px-8 2xl:px-10 py-6 flex flex-col gap-5">
      <!-- Top Action & Filter Bar -->
      <div class="bg-white rounded-xl shadow-xs border border-slate-200 p-4 flex flex-col gap-4">
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <div>
            <h1 class="text-xl font-bold text-slate-900 tracking-tight flex flex-wrap items-center gap-2">
              <span>Клиентская база заведений</span>
              <span
                class="inline-flex items-center gap-1.5 text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 font-mono border border-slate-200"
                title="Всего заведений в выбранной системе"
              >
                <i class="pi pi-building text-[10px] text-slate-500"></i>
                Всего: {{ currentTotalCount }}
              </span>
              <span
                class="inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 font-mono"
                title="Количество активных заведений"
              >
                <i class="pi pi-check-circle text-[10px] text-emerald-600"></i>
                Активных: {{ activeCount }}
              </span>
              <span
                class="inline-flex items-center gap-1.5 text-xs font-bold px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-900 border border-emerald-300 font-mono shadow-2xs"
                title="ИТС: всего заведений (точек) и количество уникальных компаний/сетей"
              >
                <i class="pi pi-shield text-[10px] text-emerald-700"></i>
                <span>На ИТС: {{ itsCount }} всего ({{ itsCompaniesCount }} комп.)</span>
              </span>
              <span
                v-if="isFiltered"
                class="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200 font-mono"
                title="Найдено заведений по текущим фильтрам"
              >
                <i class="pi pi-filter text-[10px] text-blue-500"></i>
                Найдено: {{ totalCount }}
              </span>
            </h1>
            <p class="text-xs text-slate-500 mt-0.5">Управление параметрами подключения, серверами и учетными записями</p>
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
              icon="pi pi-refresh"
              severity="secondary"
              outlined
              size="small"
              title="Обновить список"
              :loading="loading"
              @click="handleRefresh"
            />
          </div>
        </div>

        <!-- Software System Toggle (iiko vs Rosta) & Node Type Quick Filter -->
        <div class="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-100">
          <div class="inline-flex p-1 bg-slate-100 rounded-lg border border-slate-200">
            <!-- iiko button -->
            <button
              type="button"
              class="px-3.5 py-1.5 text-xs font-bold rounded-md transition-all flex items-center gap-2"
              :class="selectedSoftwareType === 'IIKO' ? 'bg-blue-600 text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'"
              @click="setSoftwareType('IIKO')"
            >
              <i class="pi pi-server"></i>
              <span>iiko</span>
              <span
                class="px-1.5 py-0.2 rounded-full text-[10px]"
                :class="selectedSoftwareType === 'IIKO' ? 'bg-blue-700 text-white' : 'bg-slate-200 text-slate-700'"
              >
                {{ filterOptions.iiko_count || 907 }}
              </span>
            </button>

            <!-- Rosta button -->
            <button
              type="button"
              class="px-3.5 py-1.5 text-xs font-bold rounded-md transition-all flex items-center gap-2"
              :class="selectedSoftwareType === 'ROSTA' ? 'bg-emerald-600 text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'"
              @click="setSoftwareType('ROSTA')"
            >
              <i class="pi pi-tags"></i>
              <span>Rosta</span>
              <span
                class="px-1.5 py-0.2 rounded-full text-[10px]"
                :class="selectedSoftwareType === 'ROSTA' ? 'bg-emerald-700 text-white' : 'bg-slate-200 text-slate-700'"
              >
                {{ filterOptions.rosta_count || 79 }}
              </span>
            </button>

            <!-- All systems button -->
            <button
              type="button"
              class="px-3 py-1.5 text-xs font-medium rounded-md transition-all flex items-center gap-1.5"
              :class="selectedSoftwareType === '' ? 'bg-white text-slate-900 shadow-xs border border-slate-200' : 'text-slate-500 hover:text-slate-800'"
              @click="setSoftwareType('')"
            >
              <span>Все системы</span>
              <span
                class="px-1.5 py-0.2 rounded-full text-[10px]"
                :class="selectedSoftwareType === '' ? 'bg-slate-200 text-slate-800' : 'bg-slate-200 text-slate-600'"
              >
                {{ filterOptions.total_count || 985 }}
              </span>
            </button>
          </div>

          <!-- Quick Node Type Filter & Quick AnyDesk -->
          <div class="flex flex-wrap items-center gap-3">
            <!-- Quick Node Type Filter -->
            <div class="flex items-center gap-2">
              <span class="text-xs text-slate-500 font-medium whitespace-nowrap">Тип заведения:</span>
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
            <div class="flex items-center gap-1.5 pl-3 border-l border-slate-200">
              <span class="text-xs text-slate-500 font-medium whitespace-nowrap">Быстрый AnyDesk:</span>
              <div class="flex items-center gap-1">
                <div class="relative flex items-center">
                  <IconField iconPosition="left">
                    <InputIcon class="pi pi-desktop text-red-500 text-xs" />
                    <InputText
                      v-model="quickAnydeskId"
                      placeholder="AnyDesk ID (Enter)..."
                      class="w-44 text-xs font-mono !pl-7 !pr-6"
                      @keydown.enter.stop.prevent="launchQuickAnydesk"
                    />
                  </IconField>
                  <button
                    v-if="quickAnydeskId"
                    type="button"
                    class="absolute right-2 text-slate-400 hover:text-slate-600 transition cursor-pointer"
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
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-2.5 pt-3 border-t border-slate-100">
          <!-- Search input -->
          <div class="sm:col-span-2">
            <IconField iconPosition="left">
              <InputIcon class="pi pi-search" />
              <InputText
                v-model="searchQuery"
                placeholder="Поиск (название, CRM, UID, сервер, город)..."
                class="w-full text-xs"
                @input="onSearchInput"
              />
            </IconField>
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

          <!-- Sort Filter -->
          <div>
            <Select
              v-model="selectedOrdering"
              :options="orderingOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="Сортировка"
              class="w-full text-xs"
              @change="onFilterChange"
            />
          </div>
        </div>

        <!-- Active Chain Filter Banner -->
        <div
          v-if="selectedChain"
          class="mt-3 flex items-center justify-between px-3 py-2 bg-indigo-50/90 border border-indigo-200 rounded-lg text-xs text-indigo-900"
        >
          <div class="flex items-center gap-2">
            <i class="pi pi-sitemap text-indigo-600 font-bold"></i>
            <span>
              Показаны только заведения сети:
              <strong class="font-bold underline text-indigo-950">{{ activeChainName }}</strong>
              (головной узел и все филиалы)
            </span>
          </div>
          <Button
            label="Сбросить фильтр сети"
            icon="pi pi-times"
            severity="secondary"
            size="small"
            text
            class="!text-xs !p-1 text-indigo-700 hover:text-indigo-900"
            @click="clearChainFilter"
          />
        </div>
      </div>

      <!-- Main Data Table -->
      <div class="bg-white rounded-xl shadow-xs border border-slate-200 overflow-hidden">
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
            <div class="text-center py-12 text-slate-400">
              <i class="pi pi-inbox text-4xl mb-2"></i>
              <p>Заведения не найдены по заданным критериям поиска.</p>
            </div>
          </template>

          <!-- Place Name & City with Chain/RMS hierarchy -->
          <Column field="place_name" header="Заведение / Юр. лицо" :sortable="true" style="min-width: 240px">
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
                      ? 'bg-purple-700 text-white border-purple-700 shadow-xs ring-2 ring-purple-200'
                      : 'text-purple-800 bg-purple-50 border-purple-200 hover:bg-purple-100 hover:border-purple-300'"
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
                      ? 'bg-indigo-600 text-white border-indigo-600 shadow-xs ring-2 ring-indigo-200'
                      : 'text-indigo-700 bg-indigo-50 border-indigo-200 hover:bg-indigo-100 hover:border-indigo-300'"
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
                    :class="data.helpdesk_its === 'Да' ? getExpirationTextClass(data.its_days_remaining ?? getDaysRemaining(data.its_expires_at), true) : 'text-slate-900 hover:text-blue-600'"
                  >
                    <span>{{ data.place_name }}</span>
                    <span
                      v-if="data.helpdesk_its === 'Да'"
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
                  </span>
                </div>

                <span class="text-[11px] text-slate-500 mt-0.5">
                  {{ data.company_name || '—' }} • <span class="font-medium text-slate-600">{{ data.city || 'Город не указан' }}</span>
                </span>
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
                <span v-if="data.port_number && data.port_number !== '443'" class="text-slate-400 shrink-0">
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

          <!-- License & Version / Distribution -->
          <Column field="iiko_version" header="Лицензия / Версия" :sortable="true" style="min-width: 180px; white-space: nowrap">
            <template #body="{ data }">
              <div class="flex items-center gap-1.5 text-xs whitespace-nowrap">
                <span v-if="data.software_type !== 'ROSTA'" class="font-medium text-slate-700">
                  {{ data.licence_type || '—' }} • {{ data.iiko_version || '—' }}
                </span>
                <span v-else class="text-emerald-600 font-semibold">
                  {{ data.licence_type || 'Rosta' }}
                </span>

                <!-- Copy Distribution Link Button (for iiko with distribution_link) -->
                <button
                  v-if="data.software_type !== 'ROSTA' && data.iiko_version"
                  type="button"
                  @click.stop="copyDistributionLink(data)"
                  :title="data.distribution_link ? `Скопировать ссылку на дистрибутив (${data.iiko_version})` : `Ссылка на дистрибутив (${data.iiko_version}) не найдена`"
                  class="inline-flex items-center justify-center w-6 h-6 rounded-md transition shrink-0 cursor-pointer"
                  :class="data.distribution_link ? 'text-blue-500 hover:text-blue-700 hover:bg-blue-50' : 'text-slate-300 opacity-40 hover:bg-slate-100'"
                >
                  <i class="pi pi-copy text-xs"></i>
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

          <!-- Row Action Buttons -->
          <Column header="Действия" style="min-width: 120px; text-align: right">
            <template #body="{ data }">
              <div class="flex items-center justify-end gap-1" @click.stop>
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

                <!-- Open Details Drawer -->
                <Button
                  icon="pi pi-chevron-right"
                  text
                  rounded
                  size="small"
                  severity="secondary"
                  title="Подробно"
                  @click="openDetails(data.id)"
                />

                <!-- Delete (only if canEdit) -->
                <Button
                  v-if="authStore.canEdit"
                  icon="pi pi-trash"
                  text
                  rounded
                  size="small"
                  severity="danger"
                  title="Удалить заведение"
                  @click="deleteCompany(data)"
                />
              </div>
            </template>
          </Column>
        </DataTable>

        <!-- Pagination -->
        <div class="p-3 border-t border-slate-200 flex flex-col md:flex-row justify-between items-center gap-3 text-xs text-slate-600 bg-slate-50">
          <div class="flex items-center gap-3 flex-wrap">
            <span class="whitespace-nowrap font-medium">Показано {{ companies.length }} из {{ totalCount }} заведений</span>
            <div class="flex items-center gap-1.5 border-l border-slate-200 pl-3">
              <span class="text-slate-500 whitespace-nowrap">Показывать по:</span>
              <Select
                v-model="pageSize"
                :options="pageSizeOptions"
                optionLabel="label"
                optionValue="value"
                size="small"
                class="w-24 text-xs bg-white font-medium"
                @change="onPageSizeChange"
              />
            </div>
          </div>

          <!-- Page Navigation with Numbers (1, 2, 3, 4 ... 19) -->
          <div class="flex items-center gap-1 flex-wrap justify-center">
            <!-- First Page Button -->
            <button
              type="button"
              class="w-8 h-8 flex items-center justify-center rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-200 disabled:opacity-30 disabled:pointer-events-none transition cursor-pointer"
              :disabled="currentPage <= 1"
              @click="changePage(1)"
              title="Первая страница"
            >
              <i class="pi pi-angle-double-left text-xs"></i>
            </button>

            <!-- Previous Page Button -->
            <button
              type="button"
              class="w-8 h-8 flex items-center justify-center rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-200 disabled:opacity-30 disabled:pointer-events-none transition cursor-pointer"
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
                class="w-6 h-8 flex items-center justify-center text-slate-400 font-mono select-none"
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
                  : 'text-slate-700 hover:bg-slate-200 hover:text-blue-600'"
              >
                {{ p }}
              </button>
            </template>

            <!-- Next Page Button -->
            <button
              type="button"
              class="w-8 h-8 flex items-center justify-center rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-200 disabled:opacity-30 disabled:pointer-events-none transition cursor-pointer"
              :disabled="currentPage >= totalPages"
              @click="changePage(currentPage + 1)"
              title="Следующая страница"
            >
              <i class="pi pi-chevron-right text-xs"></i>
            </button>

            <!-- Last Page Button -->
            <button
              type="button"
              class="w-8 h-8 flex items-center justify-center rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-200 disabled:opacity-30 disabled:pointer-events-none transition cursor-pointer"
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

    <!-- Quick Anydesk Launch Modal -->
    <AnydeskVersionSelectModal
      v-model="showQuickAnydeskModal"
      :station="quickAnydeskStation"
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
import Select from 'primevue/select'
import Tag from 'primevue/tag'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { useAuthStore } from '../stores/auth'
import { useCompanionStore } from '../stores/companion'
import { companiesApi } from '../api/companies'
import Navbar from '../components/Navbar.vue'
import QuickCopyBtn from '../components/QuickCopyBtn.vue'
import CompanyDetailDrawer from '../components/CompanyDetailDrawer.vue'
import AnydeskVersionSelectModal from '../components/AnydeskVersionSelectModal.vue'
import { anydeskApi } from '../api/anydesk'
import {
  getDaysRemaining,
  getExpirationBadgeClass,
  getExpirationTextClass,
  getExpirationIcon,
  getItsTooltip,
  formatDaysRemaining,
  formatDate,
} from '../utils/expiration'

const toast = useToast()
const confirm = useConfirm()
const authStore = useAuthStore()
const companionStore = useCompanionStore()

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
const selectedOrdering = ref('chain_smart')
const orderingOptions = [
  { label: 'По сетям (новые сначала)', value: 'chain_smart' },
  { label: 'По версии iiko (новые сначала)', value: '-iiko_version' },
  { label: 'По версии iiko (старые сначала)', value: 'iiko_version' },
  { label: 'Сначала новые (по дате)', value: '-created_at' },
  { label: 'По названию (А-Я)', value: 'place_name' },
  { label: 'По названию (Я-А)', value: '-place_name' },
  { label: 'По городу (А-Я)', value: 'city' },
]

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
  if (data.helpdesk_its === 'Да') {
    return 'bg-emerald-50/30 hover:!bg-emerald-50/70 border-l-4 border-l-emerald-600 transition-colors'
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
    if (selectedCity.value) params.city = selectedCity.value
    if (selectedStatus.value !== null && selectedStatus.value !== undefined && selectedStatus.value !== '') {
      params.status = selectedStatus.value
    }
    if (selectedIts.value) params.its = selectedIts.value
    if (selectedBusinessType.value) params.business_type = selectedBusinessType.value
    if (selectedOrdering.value) params.ordering = selectedOrdering.value

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
      summary: 'Дистрибутив не найден',
      detail: `Для версии '${company.iiko_version || '—'}' нет ссылки в реестре дистрибутивов`,
      life: 3000,
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

onMounted(() => {
  loadFilterOptions()
  loadCompanies()
})
</script>
