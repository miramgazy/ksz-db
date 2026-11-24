<template>
  <Drawer
    v-model:visible="visible"
    position="right"
    class="!w-full md:!w-[640px] lg:!w-[760px] 2xl:!w-[880px]"
  >
    <template #header>
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-blue-100 dark:bg-blue-950/80 text-blue-700 dark:text-blue-300 flex items-center justify-center font-bold text-lg">
          <i class="pi pi-building"></i>
        </div>
        <div>
          <div v-if="!company?.id">
            <h2 class="text-lg font-bold text-slate-900 dark:text-slate-100 leading-tight">Создание нового заведения</h2>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Заполните реквизиты для добавления в базу данных</p>
          </div>
          <div v-else>
            <div class="flex flex-wrap items-center gap-2">
              <h2 class="text-lg font-bold text-slate-900 dark:text-slate-100 leading-tight">{{ company?.place_name }}</h2>
              <!-- Status Badge: Активный / Неактивный -->
              <Tag
                :value="company?.status ? 'Активный' : 'Неактивный'"
                :severity="company?.status ? 'success' : 'danger'"
                class="!text-[11px]"
              />
              <!-- System Badge: iiko / Rosta -->
              <Tag
                :value="company?.software_type || 'iiko'"
                :severity="company?.software_type === 'ROSTA' ? 'warn' : 'info'"
                class="!text-[10px]"
              />
              <!-- Node Type Badge: Chain / RMS -->
              <Tag
                v-if="company?.node_type === 'CHAIN'"
                :value="`iikoChain [CO] (${company?.branches_count || 0})`"
                severity="help"
                class="!text-[10px]"
              />
              <Tag
                v-else-if="company?.parent_chain_name"
                :value="`RMS ↳ ${company?.parent_chain_name}`"
                severity="secondary"
                class="!text-[10px]"
              />
              <!-- ITS Badge in Header -->
              <Tag
                v-if="company?.helpdesk_its === 'Да'"
                value="ИТС Сопровождение"
                severity="success"
                class="!text-[10px] !bg-emerald-600 !text-white font-bold"
                icon="pi pi-shield"
              />
            </div>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5 flex flex-wrap items-center gap-1.5">
              <span>{{ company?.company_name || 'Юр. лицо не указано' }}</span>
              <span>•</span>
              <span class="font-medium text-slate-700 dark:text-slate-300">{{ company?.city || 'Город не указан' }}</span>
              <template v-if="company?.created_at">
                <span class="text-slate-400">•</span>
                <span class="inline-flex items-center gap-1 text-slate-600 dark:text-slate-300 font-medium" title="Дата запуска (создания записи в базе)">
                  <i class="pi pi-calendar text-[11px] text-blue-600 dark:text-blue-400"></i>
                  Запуск: <span class="font-bold text-slate-800 dark:text-slate-200">{{ formatDate(company.created_at) }}</span>
                </span>
              </template>
            </p>
          </div>
        </div>
      </div>
    </template>

    <div v-if="loading" class="flex justify-center items-center py-20 text-slate-400">
      <i class="pi pi-spin pi-spinner text-3xl"></i>
    </div>

    <div v-else-if="company" class="flex flex-col gap-6 py-2">
      <!-- Quick Operational Action Buttons -->
      <div v-if="company?.id && !isEditing" class="p-4 bg-slate-100 dark:bg-slate-800/80 rounded-xl border border-slate-200 dark:border-slate-700">
        <div class="text-xs font-bold uppercase text-slate-500 dark:text-slate-400 mb-2.5 tracking-wider">Быстрые действия и запуск:</div>
        <div class="flex flex-wrap gap-2">
          <!-- BackOffice launch (for iiko) -->
          <Button
            v-if="company.software_type !== 'ROSTA'"
            label="Запустить BackOffice"
            icon="pi pi-play"
            severity="primary"
            size="small"
            @click="handleLaunchBackoffice"
          />

          <!-- Insert into ClearBat SQLite (for iiko) -->
          <Button
            v-if="company.software_type !== 'ROSTA'"
            label="Внести в ClearBat"
            icon="pi pi-database"
            severity="help"
            size="small"
            @click="handleInsertClearbat"
          />

          <!-- Update license -->
          <Button
            v-if="company.software_type !== 'ROSTA'"
            label="Обновить лицензию"
            icon="pi pi-sync"
            severity="secondary"
            size="small"
            :loading="updatingLicense"
            @click="handleLaunchLicense"
          />

          <!-- View current licenses -->
          <Button
            v-if="company.software_type !== 'ROSTA'"
            label="Текущие лицензии"
            :icon="company.last_license_error ? 'pi pi-exclamation-triangle' : 'pi pi-id-card'"
            :severity="licenseButtonSeverity"
            outlined
            size="small"
            :title="getLicenseTooltip(company)"
            @click="licenseDialogVisible = true"
          />

          <!-- iikoWeb link -->
          <Button
            v-if="company.software_type !== 'ROSTA'"
            label="iikoWeb"
            icon="pi pi-globe"
            severity="info"
            outlined
            size="small"
            @click="openIikoWeb"
          />

          <!-- Server link with auto-copy password -->
          <Button
            v-if="company.software_type !== 'ROSTA'"
            label="Server"
            icon="pi pi-external-link"
            severity="secondary"
            outlined
            size="small"
            title="Открыть Server и скопировать пароль администратора"
            @click="openServer"
          />

          <!-- Partner Portal with auto-copy UID -->
          <Button
            v-if="company.software_type !== 'ROSTA'"
            label="Partners Portal"
            icon="pi pi-user"
            severity="secondary"
            outlined
            size="small"
            title="Открыть Partners Portal и скопировать UID"
            @click="openPartnersPortal"
          />

          <!-- BG Image (CRM background image link) -->
          <Button
            v-if="company.crm_id"
            label="BG Image"
            icon="pi pi-image"
            severity="secondary"
            outlined
            size="small"
            title="Открыть BG Image"
            @click="openBgImage"
          />
        </div>
      </div>

      <!-- Mode Switch: View vs Edit -->
      <div class="flex justify-between items-center border-b border-slate-200 dark:border-slate-700 pb-2">
        <h3 class="text-sm font-bold uppercase tracking-wider text-slate-700 dark:text-slate-200">
          {{ !company?.id ? 'Параметры нового заведения' : 'Реквизиты заведения' }}
        </h3>
        <div v-if="authStore.canEdit">
          <Button
            v-if="!isEditing && company?.id"
            label="Редактировать"
            icon="pi pi-pencil"
            size="small"
            text
            @click="startEdit"
          />
          <div v-else class="flex gap-2">
            <Button label="Отмена" severity="secondary" size="small" text @click="cancelEdit" />
            <Button label="Сохранить" icon="pi pi-check" size="small" :loading="saving" @click="saveEdit" />
          </div>
        </div>
      </div>

      <!-- View Mode: Credentials & Properties with 1-Click Copy -->
      <div v-if="!isEditing" class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
        <div class="p-3 bg-white dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg">
          <div class="text-xs text-slate-500 dark:text-slate-400 font-medium">Сервер / IP:</div>
          <div class="mt-0.5">
            <QuickCopyBtn :text="company.server_name" label="Сервер" />
            <span v-if="company.port_number && company.port_number !== '443'" class="text-xs text-slate-400 font-mono">:{{ company.port_number }}</span>
          </div>
        </div>

        <div class="p-3 bg-white dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg">
          <div class="text-xs text-slate-500 dark:text-slate-400 font-medium">CRM ID / UID:</div>
          <div class="flex items-center gap-2 mt-0.5">
            <QuickCopyBtn :text="company.crm_id" label="CRM ID" />
            <span class="text-slate-300 dark:text-slate-600">|</span>
            <QuickCopyBtn :text="company.uid" label="UID" />
          </div>
        </div>

        <div class="p-3 bg-white dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg">
          <div class="text-xs text-slate-500 dark:text-slate-400 font-medium">Логин администратора:</div>
          <div class="mt-0.5">
            <QuickCopyBtn :text="company.system_admin_name" label="Логин" />
          </div>
        </div>

        <div class="p-3 bg-white dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg">
          <div class="text-xs text-slate-500 dark:text-slate-400 font-medium flex justify-between">
            <span>Пароль администратора:</span>
            <button
              type="button"
              class="text-xs text-blue-600 dark:text-blue-400 hover:underline cursor-pointer"
              @click="showPassword = !showPassword"
            >
              {{ showPassword ? 'Скрыть' : 'Показать' }}
            </button>
          </div>
          <div class="mt-0.5 flex items-center gap-1 font-mono">
            <QuickCopyBtn
              :text="company.system_admin_password"
              label="Пароль администратора"
            >
              {{ showPassword ? (company.system_admin_password || '—') : '••••••••' }}
            </QuickCopyBtn>
          </div>
        </div>

        <div class="p-3 bg-white dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg">
          <div class="text-xs text-slate-500 dark:text-slate-400 font-medium">Тип узла:</div>
          <div class="mt-0.5 font-semibold text-slate-800 dark:text-slate-100 flex items-center gap-2">
            <Tag
              :value="company.node_type === 'CHAIN' ? 'Chain' : 'RMS'"
              :severity="company.node_type === 'CHAIN' ? 'help' : 'info'"
              class="!text-xs font-bold"
            />
            <span v-if="company.node_type === 'CHAIN' && company.branches_count" class="text-xs text-slate-500 dark:text-slate-400 font-normal">
              ({{ company.branches_count }} филиалов)
            </span>
            <span v-else-if="company.parent_chain_name" class="text-xs text-indigo-700 dark:text-indigo-400 font-medium">
              ↳ {{ company.parent_chain_name }}
            </span>
          </div>
        </div>

        <div class="p-3 bg-white dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg flex items-center justify-between">
          <div>
            <div class="text-xs text-slate-500 dark:text-slate-400 font-medium">Лицензия & Версия:</div>
            <div class="mt-0.5 font-semibold text-slate-800 dark:text-slate-100">
              {{ company.licence_type || '—' }} • {{ company.iiko_version || '—' }}
            </div>
          </div>
          <Button
            v-if="company.distribution_link"
            icon="pi pi-copy"
            label="Дистрибутив"
            severity="secondary"
            text
            size="small"
            class="!text-xs text-blue-600 dark:text-blue-400"
            @click="copyDistributionLink(company)"
          />
        </div>

        <div class="p-3 bg-white dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg">
          <div class="text-xs text-slate-500 dark:text-slate-400 font-medium">Компания / Юр. лицо:</div>
          <div class="mt-0.5 font-semibold text-slate-800 dark:text-slate-100 truncate" :title="company.company_name">
            {{ company.company_name || '—' }}
          </div>
        </div>

        <div class="p-3 bg-white dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg">
          <div class="text-xs text-slate-500 dark:text-slate-400 font-medium">Тип бизнеса / Кабинет:</div>
          <div class="mt-0.5 text-slate-800 dark:text-slate-100">
            <span class="font-semibold">{{ company.business_type || '—' }}</span>
            <span class="text-slate-400 dark:text-slate-600 mx-1.5">•</span>
            <span class="font-medium text-slate-700 dark:text-slate-300">{{ company.cabinet_name || company.company_name || '—' }}</span>
          </div>
        </div>

        <!-- iikoWeb Address Block -->
        <div
          v-if="company.software_type !== 'ROSTA' || company.iiko_web_address"
          class="p-3 bg-white dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg col-span-1 md:col-span-2 flex items-center justify-between gap-3"
        >
          <div class="flex-1 min-w-0">
            <div class="text-xs text-slate-500 dark:text-slate-400 font-medium flex items-center gap-1.5">
              <i class="pi pi-globe text-xs text-blue-500 dark:text-blue-400"></i>
              <span>Адрес iikoWeb:</span>
            </div>
            <div class="mt-0.5 flex items-center gap-2 flex-wrap">
              <template v-if="company.iiko_web_address">
                <QuickCopyBtn :text="company.iiko_web_address" label="Адрес iikoWeb" class="max-w-md sm:max-w-xl">
                  <span class="truncate block max-w-xs sm:max-w-md text-xs font-mono">{{ company.iiko_web_address }}</span>
                </QuickCopyBtn>
                <a
                  :href="company.iiko_web_address.startsWith('http') ? company.iiko_web_address : `https://${company.iiko_web_address}`"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="inline-flex items-center gap-1 text-xs text-blue-600 dark:text-blue-400 hover:underline shrink-0 ml-1"
                  title="Открыть в браузере"
                >
                  <i class="pi pi-external-link text-[10px]"></i>
                  <span>Перейти</span>
                </a>
              </template>
              <span v-else class="text-slate-400 dark:text-slate-500 text-xs italic">
                Не указан
              </span>
            </div>
          </div>
          <Button
            v-if="company.iiko_web_address"
            icon="pi pi-external-link"
            label="Открыть"
            size="small"
            severity="secondary"
            outlined
            class="!text-xs shrink-0"
            @click="openIikoWeb"
          />
        </div>

        <!-- Connected Services Block (shown only if company has services) -->
        <div
          v-if="companyServicesList.length > 0 || company.helpdesk_its === 'Да'"
          class="p-3 bg-white dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg flex items-center justify-between col-span-1 md:col-span-2"
        >
          <div class="flex-1 min-w-0 pr-3">
            <div class="text-xs text-slate-500 dark:text-slate-400 font-medium flex items-center gap-1.5">
              <i class="pi pi-box text-xs text-indigo-600 dark:text-indigo-400"></i>
              Доп. услуги:
            </div>
            <div class="mt-1 flex items-center gap-1.5 flex-wrap">
              <template v-if="companyServicesList.length > 0">
                <span
                  v-for="srv in companyServicesList"
                  :key="srv.id"
                  class="inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-md border"
                  :class="srv.is_its || srv.service_code === 'ITS'
                    ? getExpirationBadgeClass(srv.days_remaining)
                    : (srv.service_code === 'NOIP' ? 'bg-blue-100 text-blue-900 border-blue-300 dark:bg-blue-950/80 dark:text-blue-300 dark:border-blue-800' : 'bg-slate-100 text-slate-800 border-slate-300 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700')"
                >
                  <i :class="['text-[10px]', getServiceIcon(srv)]"></i>
                  <span>{{ srv.service_name || 'Услуга' }}</span>
                  <span v-if="srv.expires_at" class="text-[10px] font-mono opacity-80">
                    (до {{ formatDate(srv.expires_at) }})
                  </span>
                </span>
              </template>
              <template v-else-if="company.helpdesk_its === 'Да'">
                <span
                  class="inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-md border"
                  :class="getExpirationBadgeClass(company.its_days_remaining ?? getDaysRemaining(company.its_expires_at))"
                >
                  <i class="pi pi-shield text-[10px] text-emerald-700"></i>
                  <span>ИТС</span>
                  <span v-if="company.its_expires_at" class="text-[10px] font-mono opacity-80">
                    (до {{ formatDate(company.its_expires_at) }})
                  </span>
                </span>
              </template>
              <span v-else class="text-xs text-slate-400 dark:text-slate-500 italic">
                Нет подключенных услуг
              </span>
            </div>
          </div>
          <Button
            label="Подробнее"
            icon="pi pi-info-circle"
            size="small"
            severity="secondary"
            outlined
            class="!text-xs shrink-0"
            @click="showServicesModal = true"
          />
        </div>

        <!-- Launch Date & Audit Block -->
        <div class="p-3 bg-white dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg col-span-1 md:col-span-2">
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <div class="text-xs text-slate-500 dark:text-slate-400 font-medium flex items-center gap-1">
                <i class="pi pi-calendar text-blue-600 dark:text-blue-400"></i>
                Дата запуска заведения:
              </div>
              <div class="mt-0.5 text-xs font-semibold text-slate-800 dark:text-slate-200 font-mono">
                {{ formatDateTime(company.created_at) }}
              </div>
            </div>
            <div>
              <div class="text-xs text-slate-500 dark:text-slate-400 font-medium flex items-center gap-1">
                <i class="pi pi-history text-indigo-600 dark:text-indigo-400"></i>
                Дата последнего обновления:
              </div>
              <div class="mt-0.5 text-xs font-semibold text-slate-800 dark:text-slate-200 font-mono">
                {{ formatDateTime(company.updated_at) }}
              </div>
            </div>
            <div>
              <div class="text-xs text-slate-500 dark:text-slate-400 font-medium flex items-center gap-1">
                <i class="pi pi-user text-slate-500 dark:text-slate-400"></i>
                Автор обновления:
              </div>
              <div class="mt-0.5 text-xs font-semibold text-slate-800 dark:text-slate-200">
                {{ company.updated_by_name || 'Не указан' }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Edit Mode: Form Inputs -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
        <!-- Launch & Update Audit Banner in Edit Mode -->
        <div v-if="company?.id" class="col-span-1 md:col-span-2 p-3 bg-blue-50/70 border border-blue-200 rounded-xl">
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs text-blue-900">
            <div>
              <div class="font-bold flex items-center gap-1 text-[11px] uppercase tracking-wider text-blue-950">
                <i class="pi pi-calendar text-blue-600"></i> Дата запуска
              </div>
              <div class="mt-0.5 font-mono font-medium">{{ formatDateTime(company.created_at) }}</div>
            </div>
            <div>
              <div class="font-bold flex items-center gap-1 text-[11px] uppercase tracking-wider text-blue-950">
                <i class="pi pi-history text-indigo-600"></i> Последнее обновление
              </div>
              <div class="mt-0.5 font-mono font-medium">{{ formatDateTime(company.updated_at) }}</div>
            </div>
            <div>
              <div class="font-bold flex items-center gap-1 text-[11px] uppercase tracking-wider text-blue-950">
                <i class="pi pi-user text-slate-600"></i> Автор обновления
              </div>
              <div class="mt-0.5 font-medium">{{ company.updated_by_name || 'Не указан' }}</div>
            </div>
          </div>
        </div>
        <!-- Software System Selector: iiko vs Rosta -->
        <div>
          <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Система автоматизации *</label>
          <Select
            v-model="editForm.software_type"
            :options="softwareOptions"
            optionLabel="label"
            optionValue="value"
            class="w-full text-xs"
          />
        </div>

        <!-- Node Type: Chain vs RMS -->
        <div>
          <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Тип узла *</label>
          <Select
            v-model="editForm.node_type"
            :options="nodeTypeOptions"
            optionLabel="label"
            optionValue="value"
            class="w-full text-xs"
          />
        </div>

        <!-- Parent Chain selector if RMS -->
        <div v-if="editForm.node_type === 'RMS'" class="col-span-1 md:col-span-2 p-3 bg-blue-50/60 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-900 rounded-xl">
          <label class="block text-xs font-bold text-blue-900 dark:text-blue-300 uppercase mb-1">
            Привязать к сети (Chain)
          </label>
          <Select
            v-model="editForm.parent_chain"
            :options="chainsList"
            optionLabel="place_name"
            optionValue="id"
            placeholder="Выберите головную организацию (или оставьте пустым для одиночного заведения)"
            showClear
            filter
            class="w-full text-xs"
          >
            <template #option="{ option }">
              <div class="flex justify-between items-center w-full">
                <span class="font-semibold">{{ option.place_name }}</span>
                <span class="text-xs text-slate-400 font-mono">{{ option.city || '' }} ({{ option.branches_count || 0 }} филиалов)</span>
              </div>
            </template>
          </Select>
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Название заведения *</label>
          <InputText v-model="editForm.place_name" class="w-full" />
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Юр. лицо</label>
          <InputText v-model="editForm.company_name" class="w-full text-sm" placeholder="ИП / ТОО..." />
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Название кабинета</label>
          <InputText v-model="editForm.cabinet_name" class="w-full text-sm" placeholder="Кабинет в iiko..." />
        </div>

        <!-- City Dropdown with Manage Cities Modal Trigger -->
        <div>
          <div class="flex justify-between items-center mb-1">
            <label class="block text-xs font-semibold text-slate-600 uppercase">Город</label>
            <Button
              label="Управление городами"
              icon="pi pi-cog"
              text
              size="small"
              class="!p-0 !text-xs text-blue-600"
              @click="showCityModal = true"
            />
          </div>
          <Select
            v-model="editForm.city"
            :options="citiesList"
            placeholder="Выберите город"
            editable
            filter
            class="w-full text-xs"
          />
        </div>

        <!-- Business Type Dropdown with Manage Modal Trigger -->
        <div>
          <div class="flex justify-between items-center mb-1">
            <label class="block text-xs font-semibold text-slate-600 uppercase">Тип заведения</label>
            <Button
              label="Управление типами"
              icon="pi pi-cog"
              text
              size="small"
              class="!p-0 !text-xs text-blue-600"
              @click="showBusinessTypeModal = true"
            />
          </div>
          <Select
            v-model="editForm.business_type"
            :options="businessTypesList"
            placeholder="Выберите тип заведения"
            editable
            filter
            class="w-full text-xs"
          />
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Сервер / IP</label>
          <InputText v-model="editForm.server_name" class="w-full font-mono text-sm" />
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Порт</label>
          <InputText v-model="editForm.port_number" class="w-full font-mono text-sm" />
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Логин сисадмина</label>
          <InputText v-model="editForm.system_admin_name" class="w-full font-mono text-sm" />
        </div>

        <div>
          <div class="flex justify-between items-center mb-1">
            <label class="block text-xs font-semibold text-slate-600 uppercase">Пароль сисадмина</label>
            <Button
              label="Сгенерировать"
              icon="pi pi-key"
              text
              size="small"
              class="!p-0 !text-xs text-blue-600"
              @click="showPassGen = true"
            />
          </div>
          <InputText v-model="editForm.system_admin_password" class="w-full font-mono text-sm" />
        </div>

        <div v-if="editForm.software_type !== 'ROSTA'">
          <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">CRM ID</label>
          <InputText v-model="editForm.crm_id" class="w-full font-mono text-sm" />
        </div>

        <div v-if="editForm.software_type !== 'ROSTA'">
          <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">UID</label>
          <InputText v-model="editForm.uid" class="w-full font-mono text-sm" />
        </div>

        <!-- Licence Type Dropdown with Manage Modal Trigger -->
        <div v-if="editForm.software_type !== 'ROSTA'">
          <div class="flex justify-between items-center mb-1">
            <label class="block text-xs font-semibold text-slate-600 uppercase">Тип лицензии</label>
            <Button
              label="Управление лицензиями"
              icon="pi pi-cog"
              text
              size="small"
              class="!p-0 !text-xs text-blue-600"
              @click="showLicenceTypeModal = true"
            />
          </div>
          <Select
            v-model="editForm.licence_type"
            :options="licenceTypesList"
            placeholder="Выберите тип лицензии"
            editable
            filter
            class="w-full text-xs"
          />
        </div>

        <!-- iiko Version Dropdown with link to Distributions -->
        <div v-if="editForm.software_type !== 'ROSTA'">
          <div class="flex justify-between items-center mb-1">
            <label class="block text-xs font-semibold text-slate-600 uppercase">Версия iiko</label>
            <router-link to="/distributions" class="text-[11px] text-blue-600 hover:underline flex items-center gap-1" target="_blank">
              <i class="pi pi-external-link text-[10px]"></i> Дистрибутивы
            </router-link>
          </div>
          <Select
            v-model="editForm.iiko_version"
            :options="iikoVersionsList"
            placeholder="Выберите версию iiko"
            editable
            filter
            class="w-full text-xs font-mono"
          />
        </div>

        <div class="col-span-1 md:col-span-2" v-if="editForm.software_type !== 'ROSTA'">
          <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Адрес iikoWeb</label>
          <InputText v-model="editForm.iiko_web_address" placeholder="https://..." class="w-full text-sm" />
        </div>

        <!-- Status Checkbox: Активный / Неактивный -->
        <div class="col-span-1 md:col-span-2 flex items-center gap-2 pt-2 border-t border-slate-100">
          <Checkbox v-model="editForm.status" :binary="true" inputId="status_cb" />
          <label for="status_cb" class="text-sm font-semibold text-slate-800 cursor-pointer">
            Активное заведение (статус: <span :class="editForm.status ? 'text-emerald-600' : 'text-rose-600'">{{ editForm.status ? 'Активный' : 'Неактивный' }}</span>)
          </label>
        </div>

        <!-- ITS Checkbox and Expiration Date -->
        <div class="col-span-1 md:col-span-2 flex flex-col gap-2 pt-1 border-t border-slate-100">
          <div class="flex items-center gap-2">
            <Checkbox v-model="editForm.is_its" :binary="true" inputId="its_cb" />
            <label for="its_cb" class="text-sm font-semibold text-slate-800 cursor-pointer flex items-center gap-1.5">
              <i class="pi pi-shield text-emerald-600 text-xs"></i>
              ИТС (<span :class="editForm.is_its ? 'text-emerald-700 font-bold' : 'text-slate-400'">{{ editForm.is_its ? 'Подключено' : 'Нет' }}</span>)
            </label>
          </div>
          <div v-if="editForm.is_its" class="flex items-center gap-3 pl-6">
            <label class="text-xs text-slate-600 dark:text-slate-400 font-semibold uppercase">Срок действия ИТС:</label>
            <input
              type="date"
              v-model="editForm.its_expires_at"
              class="px-2.5 py-1 text-xs border border-slate-300 dark:border-slate-700 dark:bg-slate-900 dark:text-white rounded-md font-mono"
            />
            <button
              type="button"
              class="text-[11px] text-blue-600 dark:text-blue-400 hover:underline cursor-pointer"
              @click="editForm.its_expires_at = '2026-12-31'"
            >
              31.12.2026
            </button>
          </div>
        </div>
      </div>

      <!-- AnyDesk Stations Section -->
      <div v-if="company?.id && !isEditing" class="pt-4 border-t border-slate-200 dark:border-slate-700">
        <div class="flex justify-between items-center mb-3">
          <div class="flex items-center gap-2">
            <i class="pi pi-desktop text-blue-600 dark:text-blue-400"></i>
            <h3 class="text-sm font-bold uppercase tracking-wider text-slate-700 dark:text-slate-200">
              Рабочие места AnyDesk ({{ company.anydesk_stations?.length || 0 }})
            </h3>
          </div>
          <Button
            v-if="authStore.canEdit"
            label="Добавить AnyDesk"
            icon="pi pi-plus"
            size="small"
            severity="primary"
            outlined
            @click="openAddStation"
          />
        </div>

        <div v-if="!company.anydesk_stations?.length" class="text-center py-6 bg-slate-50 dark:bg-slate-800/50 rounded-lg text-slate-400 dark:text-slate-500 text-sm">
          К этому заведению еще не привязано ни одного подключения AnyDesk.
        </div>

        <div v-else class="flex flex-col gap-2">
          <div
            v-for="st in company.anydesk_stations"
            :key="st.id"
            class="p-3 bg-white dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg flex items-center justify-between hover:border-blue-300 dark:hover:border-blue-600 transition"
          >
            <div class="flex flex-col">
              <span class="font-semibold text-slate-800 text-sm">{{ st.description || 'Рабочее место' }}</span>
              <div class="flex items-center gap-2 text-xs mt-0.5">
                <span class="text-slate-400">ID:</span>
                <QuickCopyBtn :text="st.anydesk_id" label="AnyDesk ID" />
                <span v-if="st.any_pass" class="text-slate-400 ml-2">Пароль:</span>
                <QuickCopyBtn v-if="st.any_pass" :text="st.any_pass" label="Пароль AnyDesk" />
              </div>
            </div>

            <div class="flex items-center gap-1">
              <Button
                icon="pi pi-external-link"
                label="Запустить"
                size="small"
                severity="success"
                text
                @click="openVersionSelect(st)"
                title="Выбрать профиль и запустить AnyDesk"
              />
              <Button
                icon="pi pi-chevron-down"
                size="small"
                severity="secondary"
                text
                rounded
                @click="openVersionSelect(st)"
                title="Выбрать профиль и запустить AnyDesk"
              />
              <Button
                v-if="authStore.canEdit"
                icon="pi pi-pencil"
                size="small"
                text
                severity="secondary"
                @click="openEditStation(st)"
                title="Редактировать"
              />
              <Button
                v-if="authStore.canEdit"
                icon="pi pi-trash"
                size="small"
                text
                severity="danger"
                @click="deleteStation(st)"
                title="Удалить"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <AnydeskStationModal
      v-model="showStationModal"
      :company-id="company?.id"
      :station="selectedStation"
      @saved="refreshCompany"
    />
    <PasswordGeneratorModal
      v-model="showPassGen"
      @selected="(p) => editForm.system_admin_password = p"
    />
    <CityManagementModal
      v-model="showCityModal"
      @updated="loadCities"
    />
    <BusinessTypeManagementModal
      v-model="showBusinessTypeModal"
      @updated="loadBusinessTypes"
    />
    <LicenceTypeManagementModal
      v-model="showLicenceTypeModal"
      @updated="loadLicenceTypes"
    />
    <AnydeskVersionSelectModal
      v-model="showVersionSelectModal"
      :station="selectedStationForLaunch"
    />

    <!-- Modal for Detailed Connected Services -->
    <Dialog
      v-model:visible="showServicesModal"
      modal
      :header="`Подключенные услуги: ${company?.place_name || ''}`"
      :style="{ width: '720px', maxWidth: '95vw' }"
      :dismissableMask="true"
    >
      <div class="flex flex-col gap-4 py-1">
        <div v-if="companyServicesList.length > 0" class="flex flex-col gap-2.5">
          <div
            v-for="srv in companyServicesList"
            :key="srv.id"
            class="p-3 bg-white dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl hover:border-slate-300 dark:hover:border-slate-600 transition flex flex-col gap-2 shadow-2xs"
          >
            <div class="flex items-center justify-between gap-2 flex-wrap">
              <div class="flex items-center gap-2">
                <span
                  class="w-7 h-7 rounded-lg flex items-center justify-center shrink-0"
                  :class="srv.is_its || srv.service_code === 'ITS' ? 'bg-emerald-100 dark:bg-emerald-950/80 text-emerald-800 dark:text-emerald-300' : (srv.service_code === 'NOIP' ? 'bg-blue-100 dark:bg-blue-950/80 text-blue-800 dark:text-blue-300' : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300')"
                >
                  <i :class="['text-xs', getServiceIcon(srv)]"></i>
                </span>
                <div>
                  <div class="font-bold text-slate-900 dark:text-white text-sm">
                    {{ srv.service_name || 'Услуга' }}
                  </div>
                  <div class="text-[11px] text-slate-500 dark:text-slate-400">
                    {{ getPeriodLabel(srv.period_type) }} • {{ srv.pricing_type === 'PER_RMS' ? `По точкам RMS (${srv.quantity || 1} шт.)` : (srv.pricing_type === 'PER_FRONT' ? `По кассам Front (${srv.quantity || 1} шт.)` : 'Фиксированный тариф') }}
                  </div>
                </div>
              </div>

              <div class="flex items-center gap-2">
                <Tag
                  :value="srv.status ? 'Активна' : 'Приостановлена'"
                  :severity="srv.status ? 'success' : 'secondary'"
                  class="!text-[10px]"
                />
              </div>
            </div>

            <div class="grid grid-cols-2 sm:grid-cols-3 gap-2 pt-2 border-t border-slate-100 dark:border-slate-700 text-xs">
              <div>
                <span class="text-slate-400 dark:text-slate-500 block text-[10px] uppercase font-semibold">Срок действия:</span>
                <span
                  class="inline-flex items-center gap-1 font-mono font-medium px-2 py-0.5 rounded border mt-0.5 text-xs"
                  :class="getExpirationBadgeClass(srv.days_remaining)"
                >
                  {{ formatDate(srv.expires_at) }}
                  <span class="text-[10px] font-sans font-bold">({{ formatDaysRemaining(srv.days_remaining) }})</span>
                </span>
              </div>

              <div v-if="authStore.canEdit">
                <span class="text-slate-400 dark:text-slate-500 block text-[10px] uppercase font-semibold">Стоимость:</span>
                <span class="font-mono font-bold text-slate-900 dark:text-white block mt-0.5">
                  {{ formatCurrency(srv.total_cost) }}
                </span>
              </div>

              <div v-if="srv.comment" class="col-span-2 sm:col-span-1">
                <span class="text-slate-400 dark:text-slate-500 block text-[10px] uppercase font-semibold">Примечание:</span>
                <span class="text-slate-600 dark:text-slate-300 truncate block mt-0.5" :title="srv.comment">{{ srv.comment }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Fallback if only helpdesk_its is on company without company_services record -->
        <div v-else-if="company?.helpdesk_its === 'Да'" class="p-4 bg-emerald-50/70 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 rounded-xl flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-lg bg-emerald-100 dark:bg-emerald-950/80 text-emerald-800 dark:text-emerald-300 flex items-center justify-center shrink-0">
              <i class="pi pi-shield text-sm"></i>
            </div>
            <div>
              <div class="font-bold text-emerald-950 dark:text-emerald-200 text-sm">ИТС (Базовое сопровождение)</div>
              <div class="text-xs text-emerald-800 dark:text-emerald-300 mt-0.5">
                Срок действия: до <span class="font-mono font-bold">{{ formatDate(company.its_expires_at) }}</span>
                <span v-if="company.its_days_remaining !== null" class="ml-1 font-semibold">({{ formatDaysRemaining(company.its_days_remaining) }})</span>
              </div>
            </div>
          </div>
          <Tag value="Активна" severity="success" class="!text-[10px]" />
        </div>

        <div v-else class="text-center py-8 text-slate-400 dark:text-slate-500 flex flex-col items-center gap-2">
          <i class="pi pi-box text-3xl text-slate-300 dark:text-slate-600"></i>
          <span>К данному заведению пока не подключено дополнительных услуг.</span>
        </div>
      </div>

      <template #footer>
        <div class="flex items-center justify-between w-full pt-2 border-t border-slate-100 dark:border-slate-800">
          <button
            type="button"
            class="inline-flex items-center gap-1.5 text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 hover:underline font-semibold cursor-pointer"
            @click="goToServices"
          >
            <i class="pi pi-cog text-xs"></i>
            Перейти в раздел «ИТС и Доп»
          </button>
          <Button label="Закрыть" severity="secondary" size="small" @click="showServicesModal = false" />
        </div>
      </template>
    </Dialog>

    <!-- Superadmin Delete Venue Footer in Drawer -->
    <template #footer v-if="company?.id && !isEditing && authStore.isSuperAdmin">
      <div class="flex items-center justify-end w-full py-1">
        <Button
          label="Удалить заведение"
          icon="pi pi-trash"
          severity="danger"
          outlined
          size="small"
          class="!text-xs font-semibold hover:!bg-red-50 dark:hover:!bg-red-950/40"
          @click="confirmDeleteCompany"
        />
      </div>
    </template>
    <!-- Company License Dialog -->
    <CompanyLicenseDialog
      v-model="licenseDialogVisible"
      :company="company"
      :updating="updatingLicense"
      :status-text="updatingStatusText"
      @refresh="handleLaunchLicense"
      @reload="handleLicenseReloadFromDb"
    />
  </Drawer>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import Drawer from 'primevue/drawer'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import Checkbox from 'primevue/checkbox'
import Tag from 'primevue/tag'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { useAuthStore } from '../stores/auth'
import { useCompanionStore } from '../stores/companion'
import { companiesApi } from '../api/companies'
import { anydeskApi } from '../api/anydesk'
import { citiesApi } from '../api/cities'
import { businessTypesApi } from '../api/businessTypes'
import { licenceTypesApi } from '../api/licenceTypes'
import { distributionsApi } from '../api/distributions'
import QuickCopyBtn from './QuickCopyBtn.vue'
import AnydeskStationModal from './AnydeskStationModal.vue'
import PasswordGeneratorModal from './PasswordGeneratorModal.vue'
import CityManagementModal from './CityManagementModal.vue'
import BusinessTypeManagementModal from './BusinessTypeManagementModal.vue'
import LicenceTypeManagementModal from './LicenceTypeManagementModal.vue'
import AnydeskVersionSelectModal from './AnydeskVersionSelectModal.vue'
import CompanyLicenseDialog from './CompanyLicenseDialog.vue'
import {
  getDaysRemaining,
  getExpirationBadgeClass,
  getExpirationTextClass,
  getExpirationIcon,
  getExpirationDrawerBg,
  formatDaysRemaining,
  getLicenseSeverity,
  getLicenseTooltip,
  getEffectiveLicenseInfo,
} from '../utils/expiration'

const props = defineProps({
  modelValue: Boolean,
  companyId: [Number, String],
})
const emit = defineEmits(['update:modelValue', 'updated', 'deleted'])

const toast = useToast()
const confirm = useConfirm()
const authStore = useAuthStore()
const companionStore = useCompanionStore()
const router = useRouter()

const updatingLicense = ref(false)
const updatingStatusText = ref('')
const licenseDialogVisible = ref(false)
const keyModulesVersion = ref(0)

const onKeyModulesUpdated = () => {
  keyModulesVersion.value++
}

onMounted(() => {
  window.addEventListener('ksz_key_modules_updated', onKeyModulesUpdated)
})

onUnmounted(() => {
  window.removeEventListener('ksz_key_modules_updated', onKeyModulesUpdated)
})

const effectiveLicense = computed(() => {
  const _ = keyModulesVersion.value
  return getEffectiveLicenseInfo(company.value)
})

const licenseButtonSeverity = computed(() => {
  if (effectiveLicense.value.status === 'error') return 'danger'
  if (effectiveLicense.value.status === 'active') return 'success'
  if (effectiveLicense.value.status === 'expired') return 'warn'
  return 'secondary'
})

const licenseButtonLabel = computed(() => {
  const c = company.value
  if (c?.last_license_error) {
    return 'Лицензия (Ошибка)'
  }
  const info = effectiveLicense.value
  if (info.isPermanent) {
    return 'Лицензия (Бессрочно)'
  }
  if (info.date) {
    try {
      const parts = info.date.split('-')
      if (parts.length === 3) {
        return `Лицензия (${parts[2]}.${parts[1]})`
      }
    } catch (e) {}
  }
  return 'Лицензия'
})

const visible = ref(props.modelValue)
watch(() => props.modelValue, async (val) => {
  visible.value = val
  if (val) {
    if (props.companyId) {
      await loadCompany(props.companyId)
    } else {
      // Creation mode for new company
      await loadAllOptions()
      company.value = {
        place_name: '',
        company_name: '',
        cabinet_name: '',
        status: true,
        is_its: false,
        software_type: 'IIKO',
        node_type: 'RMS',
        parent_chain: null,
      }
      editForm.value = {
        place_name: '',
        company_name: '',
        cabinet_name: '',
        city: '',
        business_type: '',
        server_name: '',
        port_number: '443',
        system_admin_name: 'iikoadm',
        system_admin_password: '',
        crm_id: '',
        uid: '',
        licence_type: '',
        iiko_version: '',
        iiko_web_address: '',
        status: true,
        is_its: false,
        software_type: 'IIKO',
        node_type: 'RMS',
        parent_chain: null,
      }
      isEditing.value = true
    }
  }
})
watch(visible, (val) => emit('update:modelValue', val))

const loading = ref(false)
const company = ref(null)
const isEditing = ref(false)
const saving = ref(false)
const showPassword = ref(false)
const showPassGen = ref(false)
const showCityModal = ref(false)
const showBusinessTypeModal = ref(false)
const showLicenceTypeModal = ref(false)
const showVersionSelectModal = ref(false)
const selectedStationForLaunch = ref(null)

const showStationModal = ref(false)
const selectedStation = ref(null)

const showServicesModal = ref(false)
const companyServicesList = computed(() => company.value?.company_services || [])

const getServiceIcon = (srv) => {
  if (!srv) return 'pi pi-box'
  if (srv.is_its || srv.service_code === 'ITS') return 'pi pi-shield text-emerald-700'
  if (srv.service_code === 'NOIP') return 'pi pi-server text-blue-700'
  if (srv.service_code === 'WHATSAPP') return 'pi pi-whatsapp text-green-700'
  return 'pi pi-box text-indigo-600'
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

const goToServices = () => {
  showServicesModal.value = false
  visible.value = false
  router.push('/services')
}

const chainsList = ref([])
const citiesList = ref([])
const businessTypesList = ref([])
const licenceTypesList = ref([])
const iikoVersionsList = ref([])

const softwareOptions = [
  { label: 'iiko', value: 'IIKO' },
  { label: 'Rosta', value: 'ROSTA' },
]

const nodeTypeOptions = [
  { label: 'Chain (Сеть / ГО)', value: 'CHAIN' },
  { label: 'RMS (Точка / Филиал)', value: 'RMS' },
]

const editForm = ref({})

const loadCities = async () => {
  try {
    const res = await citiesApi.getCities({ page_size: 200 })
    citiesList.value = (res.data.results || res.data).map(c => c.name)
  } catch (e) {}
}

const loadChains = async () => {
  try {
    const res = await companiesApi.getChains()
    chainsList.value = res.data
  } catch (e) {}
}

const loadBusinessTypes = async () => {
  try {
    const res = await businessTypesApi.getBusinessTypes({ page_size: 200 })
    businessTypesList.value = (res.data.results || res.data).map(b => b.name)
  } catch (e) {}
}

const loadLicenceTypes = async () => {
  try {
    const res = await licenceTypesApi.getLicenceTypes({ page_size: 200 })
    licenceTypesList.value = (res.data.results || res.data).map(l => l.name)
  } catch (e) {}
}

const loadIikoVersions = async () => {
  try {
    const res = await distributionsApi.getVersions()
    iikoVersionsList.value = res.data
  } catch (e) {}
}

const loadAllOptions = async () => {
  await Promise.all([
    loadCities(),
    loadChains(),
    loadBusinessTypes(),
    loadLicenceTypes(),
    loadIikoVersions(),
  ])
}

const loadCompany = async (id) => {
  loading.value = true
  isEditing.value = false
  try {
    const res = await companiesApi.getCompany(id)
    company.value = res.data
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Ошибка', detail: 'Не удалось загрузить данные заведения', life: 3000 })
  } finally {
    loading.value = false
  }
}

const refreshCompany = () => {
  if (company.value?.id) {
    loadCompany(company.value.id)
    emit('updated')
  }
}

const startEdit = async () => {
  await loadAllOptions()
  editForm.value = {
    ...company.value,
    cabinet_name: company.value.cabinet_name || '',
    is_its: company.value.helpdesk_its === 'Да',
    its_expires_at: company.value.its_expires_at || '2026-12-31',
    software_type: company.value.software_type || 'IIKO',
    node_type: company.value.node_type || 'RMS',
    parent_chain: company.value.parent_chain || null,
  }
  isEditing.value = true
}

const cancelEdit = () => {
  if (!company.value?.id) {
    visible.value = false
  } else {
    isEditing.value = false
  }
}

const saveEdit = async () => {
  if (!editForm.value.place_name?.trim()) {
    toast.add({ severity: 'warn', summary: 'Внимание', detail: 'Укажите название заведения', life: 3000 })
    return
  }
  saving.value = true
  try {
    const {
      id,
      branches_count,
      anydesk_stations,
      company_services,
      distribution_link,
      its_days_remaining,
      updated_by_name,
      created_at,
      updated_at,
      license_data,
      license_updated_at,
      last_license_error,
      its_cost,
      parent_chain_name,
      stations_count,
      is_its,
      ...cleanData
    } = editForm.value

    const payload = {
      ...cleanData,
      cabinet_name: editForm.value.cabinet_name || '',
      helpdesk_its: editForm.value.is_its ? 'Да' : 'Нет',
      its_expires_at: editForm.value.is_its ? (editForm.value.its_expires_at || '2026-12-31') : null,
    }
    let res
    if (company.value?.id) {
      res = await companiesApi.updateCompany(company.value.id, payload)
      toast.add({ severity: 'success', summary: 'Успешно', detail: 'Данные заведения сохранены', life: 2500 })
    } else {
      res = await companiesApi.createCompany(payload)
      toast.add({ severity: 'success', summary: 'Успешно', detail: 'Заведение успешно создано', life: 2500 })
    }
    company.value = res.data
    isEditing.value = false
    emit('updated')
  } catch (err) {
    const errorMsg = err.response?.data ? (typeof err.response.data === 'object' ? JSON.stringify(err.response.data) : err.response.data) : err.message
    toast.add({ severity: 'error', summary: 'Ошибка сохранения', detail: errorMsg, life: 4000 })
  } finally {
    saving.value = false
  }
}

// Handlers for Operational Launch
const handleLaunchBackoffice = async () => {
  const c = company.value
  if (!c.server_name) {
    toast.add({ severity: 'warn', summary: 'Внимание', detail: 'Адрес сервера не указан', life: 3000 })
    return
  }

  let clearbatUrl = ''
  let plainPass = c.system_admin_password || ''
  try {
    const p = await companiesApi.getClearbatParams(c.id)
    clearbatUrl = p.data.clearbat_url
    if (p.data && p.data.password) plainPass = p.data.password
  } catch (e) {}

  if (companionStore.isOnline) {
    companionStore.launchBackoffice({
      server: c.server_name,
      port: c.port_number || '443',
      login: c.system_admin_name || 'iikoadm',
      password: plainPass,
      clearbatUrl,
    })
  } else if (clearbatUrl) {
    window.location.href = clearbatUrl
  }

  toast.add({
    severity: 'info',
    summary: 'Запуск BackOffice',
    detail: 'Запрос на открытие отправлен...',
    life: 2500,
  })
}

const handleInsertClearbat = async () => {
  const c = company.value
  if (!c.server_name) {
    toast.add({
      severity: 'warn',
      summary: 'ClearBat',
      detail: 'Укажите адрес сервера (IP/домен) заведения перед добавлением в ClearBat',
      life: 3500,
    })
    return
  }

  let clearbatPass = ''
  try {
    const p = await companiesApi.getClearbatParams(c.id)
    if (p.data && p.data.clearbat_password) {
      clearbatPass = p.data.clearbat_password
    } else if (p.data && p.data.password) {
      clearbatPass = btoa(unescape(encodeURIComponent(p.data.password)))
    }
  } catch (e) {}

  const res = await companionStore.insertClearbat({
    company_id: c.id,
    name: c.place_name,
    server: c.server_name,
    port: c.port_number || '443',
    login: c.system_admin_name || 'iikoadm',
    password: clearbatPass,
  })

  toast.add({
    severity: res.success ? 'success' : 'warn',
    summary: res.success ? 'ClearBat' : 'Ошибка ClearBat',
    detail: res.message,
    life: 4000,
  })
}

const handleLaunchLicense = async () => {
  const c = company.value
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
        // Запускаем асинхронный опрос (интервал 4 сек, до 8 попыток = до 32 сек)
        const pollRes = await companionStore.pollLicenseTaskStatus(taskId, c.id, {
          maxAttempts: 8,
          intervalMs: 4000,
          onAttempt: (attempt, max) => {
            const elapsedSec = (attempt - 1) * 4
            if (elapsedSec < 6) {
              updatingStatusText.value = `Запуск ClearBat и подключение к серверу iiko... (${attempt}/${max})`
            } else if (elapsedSec < 18) {
              updatingStatusText.value = `Ожидание формирования лицензий сервером iiko... (${attempt}/${max})`
            } else {
              updatingStatusText.value = `Завершение синхронизации сведений о лицензии... (${attempt}/${max})`
            }
          }
        })

        if (pollRes.success) {
          // Успех! Перезапрашиваем данные заведения
          try {
            const compRes = await companiesApi.get(c.id)
            if (compRes.data) {
              company.value = compRes.data
            }
          } catch (e) {}

          const modCount = pollRes.data?.modules_count || company.value?.license_data?.modules?.length || 0
          toast.add({
            severity: 'success',
            summary: 'Лицензия обновлена',
            detail: `Данные лицензии успешно сохранены в базе! Активных модулей: ${modCount}`,
            life: 5000,
          })
          emit('updated', company.value)
        } else if (pollRes.error && !pollRes.timeout) {
          // Ошибка сервера (досрочно)
          try {
            const compRes = await companiesApi.get(c.id)
            if (compRes.data) {
              company.value = compRes.data
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

const handleLicenseReloadFromDb = (freshCompany) => {
  if (freshCompany) {
    company.value = freshCompany
    emit('updated', freshCompany)
  }
}

const openIikoWeb = () => {
  let url = company.value.iiko_web_address || (company.value.server_name ? `https://${company.value.server_name}:443/navigator/index.html#/auth/login` : '')
  if (url && !url.startsWith('http://') && !url.startsWith('https://')) {
    url = `https://${url}`
  }
  if (url) {
    window.open(url, '_blank')
  }
}

const copyToClipboard = async (text, label) => {
  if (!text) return
  try {
    if (navigator?.clipboard?.writeText) {
      await navigator.clipboard.writeText(text)
    } else {
      const textArea = document.createElement('textarea')
      textArea.value = text
      document.body.appendChild(textArea)
      textArea.select()
      document.execCommand('copy')
      document.body.removeChild(textArea)
    }
    toast.add({
      severity: 'info',
      summary: 'Скопировано в буфер',
      detail: `${label}: '${text}'`,
      life: 2500,
    })
  } catch (e) {
    console.error('Copy error:', e)
  }
}

const openServer = async () => {
  if (company.value?.system_admin_password) {
    await copyToClipboard(company.value.system_admin_password, 'Пароль администратора')
  }
  const port = company.value.port_number || '443'
  const url = `https://${company.value.server_name}:${port}/resto`
  window.open(url, '_blank')
}

const openPartnersPortal = async () => {
  if (company.value?.uid) {
    await copyToClipboard(company.value.uid, 'UID')
  }
  window.open('https://pp.iiko.ru/ru/cabinet/clients.html', '_blank')
}

const openBgImage = () => {
  window.open(`https://bg.mevent.kz?text=${company.value.crm_id}`, '_blank')
}

const openVersionSelect = (st) => {
  selectedStationForLaunch.value = st
  showVersionSelectModal.value = true
}

const quickLaunchAnydesk = async (station) => {
  const res = await companionStore.launchAnydesk({
    anydesk_id: station.anydesk_id,
    any_pass: station.any_pass,
  })
  toast.add({
    severity: res.success ? 'success' : 'warn',
    summary: 'AnyDesk',
    detail: res.message,
    life: 3500,
  })
}

const openAddStation = () => {
  selectedStation.value = null
  showStationModal.value = true
}

const openEditStation = (st) => {
  selectedStation.value = st
  showStationModal.value = true
}

const deleteStation = (st) => {
  confirm.require({
    message: `Вы уверены, что хотите удалить подключение '${st.description || st.anydesk_id}'?`,
    header: 'Подтверждение удаления',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Удалить',
    rejectLabel: 'Отмена',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await anydeskApi.deleteAnydeskStation(st.id)
        toast.add({ severity: 'success', summary: 'Успешно', detail: 'Подключение AnyDesk удалено', life: 2500 })
        refreshCompany()
      } catch (err) {
        toast.add({ severity: 'error', summary: 'Ошибка', detail: err.message, life: 3000 })
      }
    },
  })
}

const confirmDeleteCompany = () => {
  if (!company.value?.id) return
  confirm.require({
    message: `Вы действительно хотите безвозвратно удалить заведение «${company.value.place_name}»? Все связанные подключения AnyDesk и подключенные услуги также будут удалены.`,
    header: 'Удаление заведения',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Удалить заведение',
    rejectLabel: 'Отмена',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await companiesApi.deleteCompany(company.value.id)
        toast.add({
          severity: 'success',
          summary: 'Заведение удалено',
          detail: `Заведение «${company.value.place_name}» успешно удалено`,
          life: 3000,
        })
        visible.value = false
        emit('deleted', company.value.id)
        emit('updated')
      } catch (err) {
        toast.add({
          severity: 'error',
          summary: 'Ошибка удаления',
          detail: err.response?.data?.detail || err.message || 'Не удалось удалить заведение',
          life: 4000,
        })
      }
    },
  })
}

const formatCurrency = (val) => {
  if (val === null || val === undefined || isNaN(val)) return '—'
  return new Intl.NumberFormat('ru-RU').format(Math.round(val)) + ' ₸'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  const d = new Date(dateStr)
  return d.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '—'
  const d = new Date(dateStr)
  return d.toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const copyDistributionLink = async (comp) => {
  const link = comp.distribution_link
  if (!link) {
    toast.add({
      severity: 'warn',
      summary: 'Дистрибутив не найден',
      detail: `Для версии '${comp.iiko_version || '—'}' нет ссылки в реестре`,
      life: 3000,
    })
    return
  }

  // Follow Form_Company_list.md logic: link & "?=" & server_name
  const server = (comp.server_name || '').trim()
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

onMounted(() => {
  loadAllOptions()
})
</script>
