<template>
  <component
    :is="asDrawer ? Drawer : Dialog"
    v-model:visible="visible"
    :modal="true"
    :position="asDrawer ? 'right' : undefined"
    :class="asDrawer ? '!w-full md:!w-[760px] lg:!w-[880px] xl:!w-[960px] 2xl:!w-[1020px]' : undefined"
    :style="!asDrawer ? { width: '960px', maxWidth: '96vw' } : undefined"
    :closable="true"
    :dismissable="true"
    :dismissable-mask="true"
  >
    <template #header>
      <div class="flex items-center justify-between w-full pr-6">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-amber-500/10 dark:bg-amber-400/10 flex items-center justify-center text-amber-600 dark:text-amber-400">
            <i class="pi pi-id-card text-xl"></i>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h3 class="font-bold text-lg text-slate-800 dark:text-white m-0">
                Текущие лицензии: {{ activeCompany?.place_name }}
              </h3>
              <Tag
                v-if="updating"
                severity="warn"
                icon="pi pi-spin pi-spinner"
                value="Парсинг лога..."
                class="text-xs"
              />
              <Tag
                v-else-if="expirationStatus"
                :severity="expirationStatus.severity"
                :value="expirationStatus.label"
                class="text-xs"
              />
            </div>
            <p class="text-xs text-slate-500 dark:text-slate-400 m-0">
              {{ activeCompany?.city ? activeCompany.city + ' • ' : '' }}CRM ID: {{ crmIdDisplay }} • UID: {{ uidDisplay }}
            </p>
          </div>
        </div>
      </div>
    </template>

    <div class="flex flex-col gap-3.5 py-1">
      <!-- Индикатор процесса парсинга и обновления -->
      <div
        v-if="updating"
        class="flex flex-col gap-2 p-3.5 rounded-xl bg-amber-500/10 dark:bg-amber-400/10 border border-amber-300 dark:border-amber-600/60 shadow-sm transition-all"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-lg bg-amber-500/20 dark:bg-amber-400/20 flex items-center justify-center text-amber-600 dark:text-amber-400 shrink-0">
              <i class="pi pi-spin pi-spinner text-base"></i>
            </div>
            <div>
              <div class="font-bold text-xs uppercase tracking-wider text-amber-900 dark:text-amber-200 flex items-center gap-2">
                <span>Выполняется обновление и парсинг лицензии</span>
                <span class="w-2 h-2 rounded-full bg-amber-500 animate-ping"></span>
              </div>
              <div class="text-xs text-amber-800 dark:text-amber-300 mt-0.5">
                {{ statusText || 'Запрос отправлен агенту. Ожидаем завершения и считывания лога CLEAR_bat...' }}
              </div>
            </div>
          </div>
          <Tag value="В процессе" severity="warn" class="text-[10px] shrink-0 font-bold" />
        </div>
        <ProgressBar mode="indeterminate" style="height: 4px;" class="mt-1" />
      </div>
      <!-- Error Alert (if last update failed) -->
      <div
        v-if="activeCompany?.last_license_error"
        class="flex items-start gap-3 p-3.5 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900/60 text-red-700 dark:text-red-300 text-sm"
      >
        <i class="pi pi-exclamation-triangle text-lg mt-0.5 text-red-500 shrink-0"></i>
        <div class="flex-1">
          <div class="font-semibold text-xs uppercase tracking-wider text-red-800 dark:text-red-200 mb-0.5">
            Ошибка последнего обновления с сервера iiko:
          </div>
          <div class="text-xs break-words">
            {{ activeCompany.last_license_error }}
          </div>
        </div>
      </div>

      <!-- Quick Summary Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-2.5">
        <!-- Card 1: Expiration -->
        <div class="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/80 flex flex-col justify-between">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Срок лицензии
            </span>
            <button
              type="button"
              class="w-6 h-6 rounded flex items-center justify-center text-slate-400 hover:text-indigo-600 hover:bg-slate-200/50 dark:hover:bg-slate-700 transition cursor-pointer"
              title="Настроить приоритет ключевых модулей для расчета срока лицензии"
              @click="openKeyModulesSettings"
            >
              <i class="pi pi-cog text-xs"></i>
            </button>
          </div>
          <div class="mt-1 flex flex-col gap-0.5">
            <div class="flex items-center gap-2 flex-wrap">
              <span class="font-bold text-base text-slate-900 dark:text-white">
                {{ expirationFormatted }}
              </span>
              <span
                v-if="effectiveLicenseInfo.source"
                class="text-[10px] font-mono font-medium text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/70 border border-indigo-200/60 dark:border-indigo-800/60 px-1.5 py-0.5 rounded truncate max-w-[190px]"
                :title="`Расчет по модулю: ${effectiveLicenseInfo.source}`"
              >
                {{ effectiveLicenseInfo.source }}
              </span>
            </div>
            <div class="text-xs text-slate-500 dark:text-slate-400">
              {{ daysRemainingText }}
            </div>
          </div>
        </div>

        <!-- Card 2: Version & Edition -->
        <div class="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/80 flex flex-col justify-between">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Версия и Редакция
            </span>
            <button
              type="button"
              class="w-6 h-6 rounded flex items-center justify-center text-slate-400 hover:text-indigo-600 hover:bg-slate-200/50 dark:hover:bg-slate-700 transition cursor-pointer"
              :class="{ 'text-indigo-600': syncingVersion }"
              :disabled="syncingVersion"
              title="Синхронизировать версию с реестром дистрибутивов"
              @click="handleSyncVersion"
            >
              <i class="pi pi-refresh text-xs" :class="{ 'pi-spin': syncingVersion }"></i>
            </button>
          </div>
          <div class="mt-1 flex flex-col gap-0.5">
            <div class="font-bold text-base text-slate-900 dark:text-white flex items-center gap-1.5">
              <span>{{ currentVersionDisplay }}</span>
              <!-- Copy Distribution Link Button with red/blue indicator -->
              <button
                v-if="currentVersionDisplay !== '—'"
                type="button"
                @click.stop="copyDistributionLinkFromModal"
                :title="activeCompany?.distribution_link ? `Скопировать ссылку на дистрибутив (${currentVersionDisplay})` : `Для версии '${currentVersionDisplay}' нет ссылки на скачивание в реестре дистрибутивов`"
                class="inline-flex items-center justify-center w-5 h-5 rounded transition shrink-0 cursor-pointer"
                :class="activeCompany?.distribution_link ? 'text-blue-500 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 hover:bg-blue-50 dark:hover:bg-slate-700' : 'text-red-500 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900/50 hover:bg-red-100 dark:hover:bg-red-900/60'"
              >
                <i class="pi pi-copy text-[11px]"></i>
              </button>
            </div>
            <div class="text-xs text-slate-500 dark:text-slate-400">
              {{ licenseData?.edition || 'IIKO_RMS' }}
            </div>
          </div>
        </div>

        <!-- Card 3: Last sync -->
        <div class="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/80 flex flex-col justify-between">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Синхронизация в базе
            </span>
          </div>
          <div class="mt-1 flex flex-col gap-0.5">
            <div class="font-bold text-sm text-slate-900 dark:text-white">
              {{ lastUpdatedFormatted }}
            </div>
            <div class="text-xs text-slate-500 dark:text-slate-400">
              генерация: {{ licenseData?.generated || '—' }}
            </div>
          </div>
        </div>
      </div>

      <!-- Блок: Список избранных лицензий (Pinned Modules Block) -->
      <div class="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/90 border border-slate-200 dark:border-slate-700/80">
        <div class="flex items-center justify-between mb-2.5">
          <div class="flex items-center gap-2">
            <span class="w-6 h-6 rounded-lg bg-amber-500/10 dark:bg-amber-400/10 flex items-center justify-center text-amber-500 dark:text-amber-400">
              <i class="pi pi-star-fill text-xs"></i>
            </span>
            <span class="text-xs font-bold uppercase tracking-wider text-slate-800 dark:text-slate-100">
              Список избранных лицензий
            </span>
            <span class="text-[11px] font-mono text-slate-400">({{ pinnedModulesList.length }})</span>
          </div>

          <Button
            label="Добавить"
            icon="pi pi-plus"
            size="small"
            severity="warning"
            outlined
            class="!py-1 !px-2.5 !text-xs !font-semibold"
            @click="showAddPinnedDialog = true"
          />
        </div>

        <!-- Grid of pinned cards -->
        <div v-if="pinnedModulesList.length" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2">
          <div
            v-for="item in pinnedModulesList"
            :key="item.name"
            class="flex items-center justify-between p-2.5 rounded-lg bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-700/80 hover:border-amber-400 dark:hover:border-amber-500/80 transition shadow-sm"
          >
            <div class="min-w-0 pr-2 flex-1">
              <div class="font-semibold text-xs text-slate-800 dark:text-slate-100 truncate" :title="item.name">
                {{ item.name }}
              </div>
              <div class="flex items-center justify-between gap-1.5 mt-1.5">
                <span
                  v-if="item.found"
                  class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300 border border-amber-200/80 dark:border-amber-900/60 shrink-0"
                >
                  {{ item.count }} шт.
                </span>
                <span v-else class="text-[10px] text-slate-400 italic shrink-0">
                  Не активирован
                </span>
                <span
                  v-if="item.found && item.to"
                  class="text-[10px] text-slate-500 dark:text-slate-400 font-mono whitespace-nowrap shrink-0"
                  :title="`Действует до ${item.to}`"
                >
                  до {{ item.to }}
                </span>
                <span
                  v-else-if="item.found && !item.to"
                  class="text-[10px] text-emerald-600 dark:text-emerald-400 font-medium whitespace-nowrap shrink-0"
                >
                  Бессрочно
                </span>
              </div>
            </div>
            <button
              type="button"
              class="w-6 h-6 rounded flex items-center justify-center text-slate-300 hover:text-red-500 hover:bg-red-50 dark:text-slate-600 dark:hover:text-red-400 dark:hover:bg-red-950/40 transition shrink-0 cursor-pointer"
              title="Убрать из избранных"
              @click="unpinModule(item.name)"
            >
              <i class="pi pi-times text-xs"></i>
            </button>
          </div>
        </div>

        <div v-else class="text-xs text-slate-400 py-2 text-center">
          Нет избранных лицензий. Нажмите «+ Добавить», чтобы выбрать модули для первоочередного просмотра (например, RMS Front Fast Food).
        </div>
      </div>

      <!-- Search & Filters Bar for General List -->
      <div class="flex items-center justify-between gap-3 pt-1">
        <IconField iconPosition="left" class="flex-1">
          <InputIcon class="pi pi-search text-slate-400 text-sm" />
          <InputText
            v-model="searchQuery"
            placeholder="Поиск по названию лицензии/модуля или ID из общего списка..."
            class="w-full text-sm"
          />
        </IconField>

        <Button
          icon="pi pi-refresh"
          label="Обновить из базы"
          severity="secondary"
          outlined
          size="small"
          :loading="reloadingDb"
          class="!text-xs shrink-0 !py-1.5"
          title="Получить актуальные данные лицензии из базы данных"
          @click="handleReloadFromDb"
        />

        <div class="text-xs text-slate-500 dark:text-slate-400 shrink-0">
          Найдено: <strong class="text-slate-800 dark:text-slate-200">{{ filteredModules.length }}</strong> из {{ modulesList.length }}
        </div>
      </div>

      <!-- General Modules Table -->
      <div class="border border-slate-200 dark:border-slate-700/80 rounded-xl overflow-hidden bg-white dark:bg-slate-800/50">
        <DataTable
          :value="filteredModules"
          :paginator="true"
          :rows="12"
          :rows-per-page-options="[12, 25, 50, 100]"
          :loading="updating || reloadingDb"
          size="small"
          striped-rows
          responsive-layout="scroll"
          class="p-datatable-sm"
        >
          <template #empty>
            <div class="text-center py-10 text-slate-400 dark:text-slate-500">
              <i class="pi pi-id-card text-4xl mb-3 block opacity-40"></i>
              <div v-if="modulesList.length && searchQuery">
                По запросу «{{ searchQuery }}» ничего не найдено.
              </div>
              <div v-else>
                Данные лицензии заведения отсутствуют в базе.<br>
                Нажмите <strong>«Обновить лицензию»</strong> для синхронизации сведений через ClearBat.
              </div>
            </div>
          </template>

          <!-- Pin/Favorite Column -->
          <Column style="width: 44px">
            <template #body="{ data }">
              <button
                type="button"
                class="w-6 h-6 rounded flex items-center justify-center transition cursor-pointer"
                :title="pinnedNames.includes(data.name) ? 'Убрать из избранных' : 'Добавить в избранное'"
                @click="togglePinModule(data.name)"
              >
                <i
                  class="pi text-xs transition"
                  :class="pinnedNames.includes(data.name) ? 'pi-star-fill text-amber-500' : 'pi-star text-slate-300 dark:text-slate-600 hover:text-amber-500'"
                ></i>
              </button>
            </template>
          </Column>

          <Column field="name" header="Название модуля" sortable>
            <template #body="{ data }">
              <span class="font-medium text-slate-800 dark:text-slate-100 text-xs">
                {{ data.name }}
              </span>
            </template>
          </Column>

          <Column field="id" header="ID" sortable style="width: 100px">
            <template #body="{ data }">
              <span class="font-mono text-xs text-slate-500 dark:text-slate-400">
                {{ data.id }}
              </span>
            </template>
          </Column>

          <Column field="count" header="Подключений" sortable style="width: 110px">
            <template #body="{ data }">
              <Tag
                :value="data.count"
                severity="info"
                class="font-mono text-xs px-2"
              />
            </template>
          </Column>

          <Column field="from" header="С даты" sortable style="width: 120px">
            <template #body="{ data }">
              <span class="text-xs text-slate-600 dark:text-slate-400">
                {{ data.from || '—' }}
              </span>
            </template>
          </Column>

          <Column field="to" header="По дату" sortable style="width: 130px">
            <template #body="{ data }">
              <span v-if="!data.to" class="text-xs text-emerald-600 dark:text-emerald-400 font-medium">
                Бессрочно
              </span>
              <span v-else :class="getModuleDateClass(data.to)" class="text-xs">
                {{ data.to }}
              </span>
            </template>
          </Column>

          <Column header="Статус" style="width: 110px">
            <template #body="{ data }">
              <Tag
                v-if="!data.to"
                severity="success"
                value="Бессрочно"
                class="text-[11px]"
              />
              <Tag
                v-else-if="isModuleExpired(data.to)"
                severity="danger"
                value="Истек"
                class="text-[11px]"
              />
              <Tag
                v-else
                severity="success"
                value="Активен"
                class="text-[11px]"
              />
            </template>
          </Column>
        </DataTable>
      </div>
    </div>

    <template #footer>
      <div class="flex items-center justify-between w-full pt-2">
        <div class="text-xs text-slate-500 dark:text-slate-400">
          <span v-if="companionStore.isOnline" class="flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400">
            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            Агент Companion онлайн
          </span>
          <span v-else class="text-slate-400">
            Агент Companion офлайн
          </span>
        </div>
        <div class="flex items-center gap-2">
          <Button
            label="Обновить лицензию"
            icon="pi pi-sync"
            severity="warning"
            size="small"
            :loading="updating"
            @click="handleRefreshLicense"
          />
          <Button
            label="Закрыть"
            icon="pi pi-times"
            severity="secondary"
            size="small"
            outlined
            @click="visible = false"
          />
        </div>
      </div>
    </template>
  </component>

  <!-- Add Pinned Module Dialog -->
  <Dialog
    v-model:visible="showAddPinnedDialog"
    header="Добавить лицензию в список избранных"
    :modal="true"
    :style="{ width: '460px', maxWidth: '95vw' }"
  >
    <div class="flex flex-col gap-3 py-2">
      <label class="text-xs font-semibold text-slate-600 dark:text-slate-300">
        Выберите лицензию/модуль из общего списка:
      </label>
      <Select
        v-model="selectedModuleToPin"
        :options="availableModulesToPin"
        option-label="name"
        option-value="name"
        placeholder="Поиск и выбор модуля..."
        filter
        class="w-full text-xs"
      >
        <template #option="{ option }">
          <div class="flex items-center justify-between w-full py-0.5">
            <span class="text-xs font-medium text-slate-800 dark:text-slate-100 truncate pr-2">
              {{ option.name }}
            </span>
            <Tag :value="`Кол-во: ${option.count}`" severity="info" class="text-[10px] shrink-0" />
          </div>
        </template>
      </Select>
    </div>
    <template #footer>
      <div class="flex justify-end gap-2 pt-2">
        <Button label="Отмена" severity="secondary" size="small" text @click="showAddPinnedDialog = false" />
        <Button
          label="В избранное (+)"
          icon="pi pi-check"
          size="small"
          severity="warning"
          :disabled="!selectedModuleToPin"
          @click="confirmAddPin"
        />
      </div>
    </template>
  </Dialog>

  <!-- Key Modules Settings Dialog for Expiration Date -->
  <Dialog
    v-model:visible="showKeyModulesDialog"
    header="Настройка ключевых модулей для расчета срока лицензии"
    :modal="true"
    :style="{ width: '560px', maxWidth: '95vw' }"
  >
    <div class="flex flex-col gap-3 py-1">
      <div class="p-2.5 rounded-lg bg-indigo-50/70 dark:bg-indigo-950/40 border border-indigo-200/80 dark:border-indigo-900/60 text-xs text-indigo-900 dark:text-indigo-200 leading-relaxed">
        Срок лицензии заведения определяется по первому совпавшему модулю из списка приоритетов (по умолчанию: <strong>ChainOperations (Chain)</strong> для сетей и <strong>RMS (Front Fast Food)</strong> для RMS). Если совпадений нет, используется общий срок из ответа ClearBat.
      </div>

      <!-- Current Priority List -->
      <div class="flex flex-col gap-1.5 mt-1">
        <label class="text-xs font-semibold text-slate-700 dark:text-slate-200">
          Приоритет расчета срока лицензии (сверху вниз):
        </label>
        <div class="flex flex-col gap-1.5 max-h-[220px] overflow-y-auto pr-1">
          <div
            v-for="(modName, index) in keyModulesList"
            :key="modName"
            class="flex items-center justify-between p-2 rounded-lg bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-xs"
          >
            <div class="flex items-center gap-2 min-w-0 pr-2">
              <span class="w-5 h-5 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center font-bold text-[10px] text-slate-700 dark:text-slate-200 shrink-0">
                {{ index + 1 }}
              </span>
              <span class="font-medium text-slate-800 dark:text-slate-100 truncate" :title="modName">
                {{ modName }}
              </span>
            </div>
            <div class="flex items-center gap-1 shrink-0">
              <button
                type="button"
                :disabled="index === 0"
                class="w-6 h-6 rounded flex items-center justify-center text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 disabled:opacity-20 cursor-pointer"
                title="Поднять выше"
                @click="moveKeyModuleUp(index)"
              >
                <i class="pi pi-arrow-up text-[10px]"></i>
              </button>
              <button
                type="button"
                :disabled="index === keyModulesList.length - 1"
                class="w-6 h-6 rounded flex items-center justify-center text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 disabled:opacity-20 cursor-pointer"
                title="Опустить ниже"
                @click="moveKeyModuleDown(index)"
              >
                <i class="pi pi-arrow-down text-[10px]"></i>
              </button>
              <button
                type="button"
                class="w-6 h-6 rounded flex items-center justify-center text-slate-300 hover:text-red-500 transition cursor-pointer ml-1"
                title="Удалить из списка"
                @click="removeKeyModule(index)"
              >
                <i class="pi pi-trash text-[11px]"></i>
              </button>
            </div>
          </div>
          <div v-if="!keyModulesList.length" class="text-xs text-slate-400 italic py-2 text-center">
            Список пуст (будет использоваться только общий срок).
          </div>
        </div>
      </div>

      <!-- Add Module Section -->
      <div class="flex flex-col gap-1.5 pt-2 border-t border-slate-200 dark:border-slate-700">
        <label class="text-xs font-semibold text-slate-700 dark:text-slate-200">
          Добавить модуль в список приоритетов:
        </label>
        <div class="flex items-center gap-2">
          <Select
            v-model="selectedNewKeyModule"
            :options="availableModulesForKeyList"
            option-label="name"
            option-value="name"
            placeholder="Выберите модуль из списка..."
            filter
            class="flex-1 text-xs"
          />
          <Button
            label="Добавить"
            icon="pi pi-plus"
            size="small"
            severity="primary"
            :disabled="!selectedNewKeyModule"
            class="!text-xs shrink-0 !py-1.5"
            @click="addKeyModule"
          />
        </div>
      </div>
    </div>

    <template #footer>
      <div class="flex items-center justify-between w-full pt-2">
        <Button
          label="Сбросить по умолчанию"
          icon="pi pi-replay"
          severity="secondary"
          size="small"
          text
          class="!text-xs"
          @click="resetKeyModulesToDefault"
        />
        <div class="flex items-center gap-2">
          <Button
            label="Отмена"
            severity="secondary"
            size="small"
            text
            @click="showKeyModulesDialog = false"
          />
          <Button
            label="Сохранить"
            icon="pi pi-check"
            severity="success"
            size="small"
            @click="saveKeyModulesSettings"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import Dialog from 'primevue/dialog'
import Drawer from 'primevue/drawer'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import Select from 'primevue/select'
import Tag from 'primevue/tag'
import ProgressBar from 'primevue/progressbar'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { useToast } from 'primevue/usetoast'
import { useCompanionStore } from '@/stores/companion'
import { companiesApi } from '@/api/companies'
import {
  DEFAULT_KEY_LICENSE_MODULES,
  getKeyLicenseModules,
  setKeyLicenseModules,
  getEffectiveLicenseInfo,
} from '@/utils/expiration'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  company: {
    type: Object,
    default: () => ({})
  },
  updating: {
    type: Boolean,
    default: false
  },
  statusText: {
    type: String,
    default: ''
  },
  asDrawer: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'refresh', 'reload'])

const toast = useToast()
const companionStore = useCompanionStore()
const searchQuery = ref('')
const showAddPinnedDialog = ref(false)
const selectedModuleToPin = ref('')
const reloadingDb = ref(false)
const localCompany = ref(null)

watch(() => props.company, (newVal) => {
  localCompany.value = newVal
}, { immediate: true })

const activeCompany = computed(() => {
  return localCompany.value || props.company || {}
})

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const licenseData = computed(() => {
  return activeCompany.value?.license_data || {}
})

const crmIdDisplay = computed(() => {
  return licenseData.value?.crm_id || activeCompany.value?.crm_id || 'Не указан'
})

const uidDisplay = computed(() => {
  return licenseData.value?.uid || activeCompany.value?.uid || 'Не указан'
})

const modulesList = computed(() => {
  const mods = licenseData.value?.modules
  if (Array.isArray(mods)) {
    return mods
  }
  return []
})

const permanentCount = computed(() => {
  return modulesList.value.filter(m => !m.to).length
})

// Pinned / Frequently viewed modules logic
const defaultPinnedNames = [
  'RMS (Front Fast Food)',
  'RMS (TableService)',
  'RMS (Office)',
  'FullEdition (Server)',
]

const loadPinnedNames = () => {
  try {
    const raw = localStorage.getItem('ksz_pinned_licenses')
    if (raw) {
      const parsed = JSON.parse(raw)
      if (Array.isArray(parsed) && parsed.length) {
        return parsed
      }
    }
  } catch (e) {}
  return [...defaultPinnedNames]
}

const pinnedNames = ref(loadPinnedNames())

const savePinnedNames = () => {
  try {
    localStorage.setItem('ksz_pinned_licenses', JSON.stringify(pinnedNames.value))
  } catch (e) {}
}

const pinnedModulesList = computed(() => {
  const map = new Map()
  for (const m of modulesList.value) {
    if (m.name) {
      map.set(m.name, m)
    }
  }

  return pinnedNames.value.map(name => {
    const foundModule = map.get(name)
    if (foundModule) {
      return {
        name,
        count: foundModule.count,
        from: foundModule.from,
        to: foundModule.to,
        id: foundModule.id,
        found: true
      }
    }
    return {
      name,
      count: 0,
      from: null,
      to: null,
      id: null,
      found: false
    }
  })
})

const availableModulesToPin = computed(() => {
  return modulesList.value.filter(m => !pinnedNames.value.includes(m.name))
})

const pinModule = (name) => {
  if (name && !pinnedNames.value.includes(name)) {
    pinnedNames.value.push(name)
    savePinnedNames()
  }
}

const unpinModule = (name) => {
  pinnedNames.value = pinnedNames.value.filter(n => n !== name)
  savePinnedNames()
}

const togglePinModule = (name) => {
  if (pinnedNames.value.includes(name)) {
    unpinModule(name)
  } else {
    pinModule(name)
  }
}

const confirmAddPin = () => {
  if (selectedModuleToPin.value) {
    pinModule(selectedModuleToPin.value)
    selectedModuleToPin.value = ''
    showAddPinnedDialog.value = false
  }
}

// General Search Filter
const filteredModules = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) {
    return modulesList.value
  }
  return modulesList.value.filter(m => {
    const nameMatch = m.name && m.name.toLowerCase().includes(q)
    const idMatch = m.id && String(m.id).toLowerCase().includes(q)
    const fromMatch = m.from && m.from.includes(q)
    const toMatch = m.to && m.to.includes(q)
    return nameMatch || idMatch || fromMatch || toMatch
  })
})

// Key Modules Settings Logic for Expiration calculation
const showKeyModulesDialog = ref(false)
const keyModulesList = ref(getKeyLicenseModules())
const selectedNewKeyModule = ref('')
const keyModulesTrigger = ref(0)

const onKeyModulesUpdated = () => {
  keyModulesTrigger.value++
  keyModulesList.value = getKeyLicenseModules()
}

onMounted(() => {
  window.addEventListener('ksz_key_modules_updated', onKeyModulesUpdated)
})

onUnmounted(() => {
  window.removeEventListener('ksz_key_modules_updated', onKeyModulesUpdated)
})

const openKeyModulesSettings = () => {
  keyModulesList.value = getKeyLicenseModules()
  selectedNewKeyModule.value = ''
  showKeyModulesDialog.value = true
}

const availableModulesForKeyList = computed(() => {
  return modulesList.value.filter(m => m.name && !keyModulesList.value.includes(m.name))
})

const addKeyModule = () => {
  if (selectedNewKeyModule.value && !keyModulesList.value.includes(selectedNewKeyModule.value)) {
    keyModulesList.value.push(selectedNewKeyModule.value)
    selectedNewKeyModule.value = ''
  }
}

const removeKeyModule = (index) => {
  keyModulesList.value.splice(index, 1)
}

const moveKeyModuleUp = (index) => {
  if (index > 0) {
    const item = keyModulesList.value[index]
    keyModulesList.value.splice(index, 1)
    keyModulesList.value.splice(index - 1, 0, item)
  }
}

const moveKeyModuleDown = (index) => {
  if (index < keyModulesList.value.length - 1) {
    const item = keyModulesList.value[index]
    keyModulesList.value.splice(index, 1)
    keyModulesList.value.splice(index + 1, 0, item)
  }
}

const resetKeyModulesToDefault = () => {
  keyModulesList.value = [...DEFAULT_KEY_LICENSE_MODULES]
}

const saveKeyModulesSettings = () => {
  setKeyLicenseModules(keyModulesList.value)
  keyModulesTrigger.value++
  window.dispatchEvent(new CustomEvent('ksz_key_modules_updated'))
  showKeyModulesDialog.value = false
  toast.add({
    severity: 'success',
    summary: 'Настройки сохранены',
    detail: 'Приоритет ключевых модулей для расчета срока лицензии обновлен',
    life: 3000
  })
}

const effectiveLicenseInfo = computed(() => {
  const _ = keyModulesTrigger.value
  return getEffectiveLicenseInfo(activeCompany.value)
})

const expirationFormatted = computed(() => {
  const info = effectiveLicenseInfo.value
  if (info.isPermanent) return 'Бессрочная'
  const exp = info.date
  if (!exp) return '—'
  try {
    const d = new Date(exp)
    if (!isNaN(d)) {
      return d.toLocaleDateString('ru-RU')
    }
  } catch (e) {}
  return exp
})

const lastUpdatedFormatted = computed(() => {
  const dt = activeCompany.value?.license_updated_at || licenseData.value?.parsed_at
  if (!dt) return 'Не обновлялось'
  try {
    const d = new Date(dt)
    if (!isNaN(d)) {
      return d.toLocaleString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  } catch (e) {}
  return dt
})

const daysRemaining = computed(() => {
  return effectiveLicenseInfo.value.daysRemaining
})

const daysRemainingText = computed(() => {
  const info = effectiveLicenseInfo.value
  if (info.isPermanent) return 'Бессрочная лицензия'
  const days = info.daysRemaining
  if (days === null) return 'Бессрочная / нет данных'
  if (days < 0) return `Истекла ${Math.abs(days)} дн. назад`
  if (days === 0) return 'Истекает сегодня'
  return `Осталось ${days} дн.`
})

const expirationStatus = computed(() => {
  const info = effectiveLicenseInfo.value
  if (info.status === 'error') {
    return { severity: 'danger', label: 'Ошибка лицензии' }
  }
  if (info.isPermanent) {
    return { severity: 'success', label: 'Бессрочная' }
  }
  const days = info.daysRemaining
  if (days === null) {
    if (!modulesList.value.length) return null
    return { severity: 'success', label: 'Бессрочная' }
  }
  if (days < 0) {
    return { severity: 'danger', label: 'Лицензия истекла' }
  }
  if (days <= 14) {
    return { severity: 'warn', label: `Истекает (${days} дн.)` }
  }
  return { severity: 'success', label: 'Лицензия активна' }
})

const isModuleExpired = (toDateStr) => {
  if (!toDateStr) return false
  const target = new Date(toDateStr)
  if (isNaN(target)) return false
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  target.setHours(0, 0, 0, 0)
  return target < today
}

const getModuleDateClass = (toDateStr) => {
  if (isModuleExpired(toDateStr)) {
    return 'text-red-600 dark:text-red-400 font-medium'
  }
  return 'text-slate-800 dark:text-slate-200'
}

const handleRefreshLicense = () => {
  emit('refresh')
}

const handleReloadFromDb = async () => {
  const compId = activeCompany.value?.id || props.company?.id
  if (!compId) return

  reloadingDb.value = true
  try {
    const res = await companiesApi.getCompany(compId)
    if (res.data) {
      localCompany.value = res.data
      emit('reload', res.data)
      toast.add({
        severity: 'success',
        summary: 'Обновлено из базы',
        detail: 'Данные лицензии заведения успешно загружены из базы данных',
        life: 3000
      })
    }
  } catch (e) {
    toast.add({
      severity: 'error',
      summary: 'Ошибка загрузки',
      detail: 'Не удалось получить актуальные данные из базы',
      life: 3000
    })
  } finally {
    reloadingDb.value = false
  }
}

const syncingVersion = ref(false)

const currentVersionDisplay = computed(() => {
  return licenseData.value?.iiko_version || activeCompany.value?.iiko_version || '—'
})

const handleSyncVersion = async () => {
  const compId = activeCompany.value?.id || props.company?.id
  if (!compId) return

  const ver = licenseData.value?.iiko_version || activeCompany.value?.iiko_version
  if (!ver) {
    toast.add({
      severity: 'warn',
      summary: 'Нет данных о версии',
      detail: 'В данных лицензии заведения отсутствует номер версии iiko для синхронизации',
      life: 4000
    })
    return
  }

  syncingVersion.value = true
  try {
    const res = await companiesApi.syncVersion(compId, { iiko_version: ver })
    if (res.data?.success && res.data?.company) {
      localCompany.value = res.data.company
      emit('reload', res.data.company)

      if (res.data.is_new_version) {
        toast.add({
          severity: 'warn',
          summary: 'Новая версия iiko!',
          detail: res.data.message || `Версия iiko новая (${res.data.iiko_version}) — добавлена в справочник дистрибутивов, необходимо заполнить поле со ссылкой!`,
          life: 8000
        })
      } else {
        toast.add({
          severity: 'success',
          summary: 'Версия синхронизирована',
          detail: res.data.message + (res.data.distribution_link ? ' • Ссылка на скачивание доступна' : ' • Ссылка на скачивание пока не заполнена'),
          life: 5000
        })
      }
    }
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Ошибка синхронизации',
      detail: err.response?.data?.error || err.message || 'Не удалось синхронизировать версию с реестром дистрибутивов',
      life: 4000
    })
  } finally {
    syncingVersion.value = false
  }
}

const copyDistributionLinkFromModal = async () => {
  const link = activeCompany.value?.distribution_link
  const ver = currentVersionDisplay.value
  if (!link) {
    toast.add({
      severity: 'warn',
      summary: 'Нет ссылки для этой версии',
      detail: `Для версии '${ver}' нет ссылки на скачивание в реестре дистрибутивов`,
      life: 4000
    })
    return
  }

  const server = (activeCompany.value?.server_name || '').trim()
  const copyText = server ? `${link}?=${server}` : link

  try {
    await navigator.clipboard.writeText(copyText)
    toast.add({
      severity: 'success',
      summary: 'Ссылка скопирована',
      detail: `Адрес ссылки: '${copyText}' на скачивание iiko Office скопирован в буфер обмена!`,
      life: 4000
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
      life: 4000
    })
  }
}
</script>
