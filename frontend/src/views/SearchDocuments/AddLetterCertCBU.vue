<script>
import axios from 'axios'
import { API_BASE_URL } from '@/API'
import AddAnswerLetterForCertCBU from './AddAnswerLetterForCertCBU.vue'

const EMPLOYEES_URL = `${API_BASE_URL}api/staff/users/`

export default {
  name: 'AddLetterCertCBU',

  components: {
    AddAnswerLetterForCertCBU,
  },

  data() {
    return {
      // режим: создание письма или добавление ответа
      mode: 'create', // 'create' | 'reply'

      destOptions: [],
      loadingDestinations: false,

      orgsByCategory: {},        // { [catId]: { items: [], loading: false } }
      activeCategoryId: null,
      selectedCategories: [],
      selectedOrgIds: [],

      // сотрудники
      employees: [],
      loadingEmployees: false,
      employeeSearch: '',

      form: {
        system: 'CERT-CBU',
        number: '',
        date: '',
        subject: '',
        performer: '',     // ID сотрудника
        description: '',
        has_deadline: false,
        deadline: '',
        files: [],
        created_by: '',
        updated_by: '',
      },

      uploading: false,
      submitStatus: null,
      submitMessage: '',
    }
  },

  async created() {
    await Promise.all([
      this.loadDestinations(),
      this.loadEmployees(),
    ])
  },

  computed: {
    filteredEmployees() {
      const q = this.employeeSearch.trim().toLowerCase()
      if (!q) return this.employees

      return (this.employees || []).filter(u => {
        const fio = (u.fio || u.full_name || '').toLowerCase()
        const username = (u.username || '').toLowerCase()
        const email = (u.email || '').toLowerCase()
        return (
          fio.includes(q) ||
          username.includes(q) ||
          email.includes(q)
        )
      })
    },
  },

  methods: {
    // будет вызываться из компонента добавления ответа (если нужно)
    onReplyCreated() {
      // тут можно показать тост, обновить список и т.п.
      console.log('Ответное письмо успешно добавлено')
    },

    // ===== сотрудники =====
    async loadEmployees() {
      this.loadingEmployees = true
      try {
        const { data } = await axios.get(EMPLOYEES_URL, {
          params: { is_active: true },
        })
        this.employees = Array.isArray(data) ? data : (data?.results || [])
      } catch (e) {
        console.error('Ошибка загрузки сотрудников', e)
        this.employees = []
      } finally {
        this.loadingEmployees = false
      }
    },

    // ===== категории / организации =====
    async loadDestinations() {
      this.loadingDestinations = true
      try {
        const { data } = await axios.get(`${API_BASE_URL}api/categories/list/`)
        const items = Array.isArray(data?.results) ? data.results : data

        this.destOptions = (items || []).map(cat => ({
          value: cat.id,
          label: cat.name || cat.title || cat.slug || `Категория #${cat.id}`,
        }))

        if (this.destOptions.length && !this.activeCategoryId) {
          const firstId = this.destOptions[0].value
          this.activeCategoryId = firstId
          if (!this.selectedCategories.includes(firstId)) {
            this.selectedCategories.push(firstId)
          }
          await this.ensureOrgsLoaded(firstId)
        }
      } catch (e) {
        console.error('Ошибка загрузки категорий (куда отправлено)', e)
      } finally {
        this.loadingDestinations = false
      }
    },

    async ensureOrgsLoaded(catId) {
      const bucket = this.orgsByCategory[catId]
      if (bucket && (bucket.items?.length || bucket.loading)) return

      this.orgsByCategory[catId] = { items: [], loading: true }

      try {
        const { data } = await axios.get(
          `${API_BASE_URL}api/organizations/list/`,
          { params: { category: catId } }
        )

        const items = Array.isArray(data?.results) ? data.results : data
        this.orgsByCategory[catId].items = items || []
      } catch (e) {
        console.error('Ошибка загрузки организаций для категории', catId, e)
        this.orgsByCategory[catId].items = []
      } finally {
        this.orgsByCategory[catId].loading = false
      }
    },

    async toggleCategory(catId) {
      const idx = this.selectedCategories.indexOf(catId)
      if (idx === -1) {
        this.selectedCategories.push(catId)
      } else {
        this.selectedCategories.splice(idx, 1)
        const bucket = this.orgsByCategory[catId]
        if (bucket?.items?.length) {
          const idsToRemove = bucket.items.map(o => o.id)
          this.selectedOrgIds = this.selectedOrgIds.filter(
            id => !idsToRemove.includes(id)
          )
        }
      }
      this.activeCategoryId = catId
      await this.ensureOrgsLoaded(catId)
    },

    isCategorySelected(catId) {
      return this.selectedCategories.includes(catId)
    },

    isOrgSelected(orgId) {
      return this.selectedOrgIds.includes(orgId)
    },

    toggleOrg(orgId) {
      const idx = this.selectedOrgIds.indexOf(orgId)
      if (idx === -1) this.selectedOrgIds.push(orgId)
      else this.selectedOrgIds.splice(idx, 1)
    },

    toggleSelectAllActive() {
      const bucket = this.orgsByCategory[this.activeCategoryId]
      if (!bucket || !bucket.items?.length) return

      const ids = bucket.items.map(o => o.id)
      const allSelected = ids.every(id => this.selectedOrgIds.includes(id))

      if (allSelected) {
        this.selectedOrgIds = this.selectedOrgIds.filter(
          id => !ids.includes(id)
        )
      } else {
        ids.forEach(id => {
          if (!this.selectedOrgIds.includes(id)) {
            this.selectedOrgIds.push(id)
          }
        })
      }
    },

    onFiles(e) {
      this.form.files = Array.from(e.target.files || [])
    },

    async submit() {
      this.uploading = true
      this.submitStatus = null
      this.submitMessage = ''

      try {
        const fd = new FormData()
        fd.append('system', this.form.system)
        fd.append('number', this.form.number || '')
        fd.append('date', this.form.date || '')
        fd.append('subject', this.form.subject || '')
        fd.append('performer', this.form.performer || '')  // ID сотрудника
        fd.append('description', this.form.description || '')
        fd.append('has_deadline', this.form.has_deadline ? 'true' : 'false')
        fd.append('deadline', this.form.deadline || '')

        this.selectedCategories.forEach(id =>
          fd.append('dest_categories', id)
        )
        this.selectedOrgIds.forEach(id =>
          fd.append('dest_organizations', id)
        )
        this.form.files.forEach(f => fd.append('files', f))

        await axios.post(
          `${API_BASE_URL}api/cert-documents/letters/`,
          fd,
          { headers: { 'Content-Type': 'multipart/form-data' } },
        )

        this.submitStatus = 'success'
        this.submitMessage = 'Письмо CERT-CBU успешно сохранено.'

        // сброс формы
        this.form = {
          system: 'CERT-CBU',
          number: '',
          date: '',
          subject: '',
          performer: '',
          description: '',
          has_deadline: false,
          deadline: '',
          files: [],
          created_by: '',
          updated_by: '',
        }
        this.selectedOrgIds = []
      } catch (e) {
        console.error('Ошибка сохранения письма CERT-CBU', e)
        this.submitStatus = 'error'
        this.submitMessage =
          'Ошибка при сохранении письма. Проверьте данные и попробуйте ещё раз.'
      } finally {
        this.uploading = false
      }
    },
  },
}
</script>

<template>
  <div class="cert-card">
    <!-- ТАБЫ: Создание / Добавление ответа -->
    <div class="tabs">
      <button
        type="button"
        class="tab-btn"
        :class="{ active: mode === 'create' }"
        @click="mode = 'create'"
      >
        Создание
      </button>
      <button
        type="button"
        class="tab-btn"
        :class="{ active: mode === 'reply' }"
        @click="mode = 'reply'"
      >
        Добавление ответа на письмо
      </button>
    </div>

    <!-- РЕЖИМ: СОЗДАНИЕ ПИСЬМА -->
    <div v-if="mode === 'create'">
      <!-- уведомление -->
      <transition name="fade">
        <div
          v-if="submitStatus"
          class="alert"
          :class="submitStatus === 'success' ? 'alert-success' : 'alert-error'"
        >
          {{ submitMessage }}
        </div>
      </transition>

      <form class="form" @submit.prevent="submit">
        <!-- Основные реквизиты -->
        <div class="grid">
          <div class="col">
            <label>Номер письма</label>
            <input v-model.trim="form.number" type="text" required />
          </div>
          <div class="col">
            <label>Дата выхода письма</label>
            <input v-model="form.date" type="date" required />
          </div>
          <!-- Файлы -->
          <div class="row">
            <label>Файлы</label>
            <input type="file" multiple @change="onFiles" />
            <div class="files" v-if="form.files.length">
              <span v-for="(f, i) in form.files" :key="i" class="chip">
                {{ f.name }}
              </span>
            </div>
          </div>
        </div>

        <div class="row">
          <label>Тема / титул</label>
          <input v-model.trim="form.subject" type="text" required />
        </div>

        <!-- Ответственный + срок -->
        <div class="grid">
          <div class="col">
            <label>Исполнитель (ответственный)</label>
            <!-- фильтр по сотрудникам -->
            <input
              v-model.trim="employeeSearch"
              type="text"
              placeholder="Поиск по ФИО / username / email"
            />
            <!-- выбор исполнителя -->
            <select v-model="form.performer">
              <option value="">Выберите исполнителя</option>
              <option
                v-for="u in filteredEmployees"
                :key="u.id"
                :value="u.id"
              >
                {{ u.fio || u.full_name || u.username || u.email || ('ID ' + u.id) }}
              </option>
            </select>
            <small class="hint" v-if="loadingEmployees">
              Загрузка списка сотрудников…
            </small>
            <small
              class="hint"
              v-else-if="!loadingEmployees && !filteredEmployees.length"
            >
              Сотрудники не найдены
            </small>
          </div>
          <div class="col deadline-col">
            <label class="deadline-label">
              <input type="checkbox" v-model="form.has_deadline" />
              Есть срок письма
            </label>
            <input
              v-model="form.deadline"
              type="date"
              :disabled="!form.has_deadline"
              placeholder="Дата срока"
            />
          </div>
        </div>

        <!-- Типы организаций -->
        <div class="row">
          <label>Куда отправлено (типы организаций)</label>
          <div class="dest-types">
            <button
              v-for="opt in destOptions"
              :key="opt.value"
              type="button"
              class="dest-pill"
              :class="{ active: isCategorySelected(opt.value) }"
              @click="toggleCategory(opt.value)"
            >
              {{ opt.label }}
            </button>
          </div>
          <small class="hint">
            Можно выбрать несколько типов организаций. Ниже появятся конкретные
            организации выбранного типа.
          </small>
        </div>

        <!-- Организации активного типа -->
        <div
          v-if="activeCategoryId && orgsByCategory[activeCategoryId]"
          class="org-list-block"
        >
          <div class="org-list-head">
            <div class="org-list-title">
              Организации:
              {{
                destOptions.find(o => o.value === activeCategoryId)?.label ||
                'Выбранный тип'
              }}
            </div>
            <button
              type="button"
              class="btn ghost small"
              @click="toggleSelectAllActive"
            >
              Выделить / снять всех
            </button>
          </div>

          <div
            v-if="orgsByCategory[activeCategoryId].loading"
            class="org-loading"
          >
            Загрузка организаций…
          </div>

          <div
            v-else-if="orgsByCategory[activeCategoryId].items.length"
            class="org-chips-wrap"
          >
            <label
              v-for="org in orgsByCategory[activeCategoryId].items"
              :key="org.id"
              class="org-chip"
            >
              <input
                type="checkbox"
                :checked="isOrgSelected(org.id)"
                @change.stop="toggleOrg(org.id)"
              />
              <span class="org-chip-label">
                {{ org.name || org.title || ('ID ' + org.id) }}
              </span>
            </label>
          </div>

          <div v-else class="org-empty">
            Для этого типа пока нет организаций.
          </div>
        </div>

        <!-- Описание -->
        <div class="row">
          <label>Описание / требуемые действия</label>
          <textarea v-model.trim="form.description" rows="4" />
        </div>

        <div class="actions">
          <button type="submit" class="btn primary" :disabled="uploading">
            {{ uploading ? 'Сохранение…' : 'Сохранить' }}
          </button>
        </div>
      </form>
    </div>

    <!-- РЕЖИМ: ДОБАВЛЕНИЕ ОТВЕТНОГО ПИСЬМА -->
    <div v-else>
      <AddAnswerLetterForCertCBU @reply-created="onReplyCreated" />
    </div>
  </div>
</template>

<style scoped>
.cert-card {
  width: 100%;
  background: #ffffff;
  border-radius: 7px;
  padding: 14px 14px 18px;
  box-sizing: border-box;
  border: 1px solid #e5e7eb;
}

/* ТАБЫ */
.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
}
.tab-btn {
  padding: 6px 14px;
  border-radius: 999px;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
  cursor: pointer;
  font-size: 13px;
  color: #374151;
  transition: all 0.16s ease;
}
.tab-btn.active {
  background: #22c55e;
  color: #ffffff;
  border-color: #16a34a;
}

/* уведомление */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.alert {
  border-radius: 7px;
  padding: 8px 12px;
  font-size: 13px;
  margin-bottom: 8px;
}
.alert-success {
  background: #ecfdf3;
  color: #166534;
  border: 1px solid #bbf7d0;
}
.alert-error {
  background: #fef2f2;
  color: #b91c1c;
  border: 1px solid #fecaca;
}

/* форма */
.form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* сетка */
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 12px;
}
.meta-grid {
  grid-template-columns: 1fr 1fr;
}
.row,
.col {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* подписи */
label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #9ca3af;
}

/* inputs/textarea/select */
input,
textarea,
select {
  border-radius: 7px;
  padding: 9px 12px;
  min-height: 38px;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
  color: #111827;
  font-size: 13px;
  outline: none;
  transition: border-color 0.16s ease, box-shadow 0.16s ease,
    background-color 0.16s ease;
}
input::placeholder,
textarea::placeholder {
  color: #9ca3af;
}
input:focus,
textarea:focus,
select:focus {
  border-color: #22c55e;
  background-color: #ffffff;
  box-shadow: 0 0 0 1px rgba(34, 197, 94, 0.15);
}
textarea {
  resize: vertical;
}

/* срок */
.deadline-col input[type='date'] {
  margin-top: 4px;
}
.deadline-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #4b5563;
}

/* типы организаций */
.dest-types {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.dest-pill {
  padding: 6px 12px;
  border-radius: 9px;
  border: 1px solid #e5e7eb;
  background: #ffffff;
  font-size: 12px;
  cursor: pointer;
  color: #374151;
  display: inline-flex;
  align-items: center;
  transition: all 0.16s ease;
}
.dest-pill.active {
  background: #ecfdf3;
  border-color: #4ade80;
  color: #166534;
  box-shadow: 0 8px 16px rgba(34, 197, 94, 0.25);
}

/* организации */
.org-list-block {
  margin-top: 4px;
  padding: 10px 12px;
  border-radius: 7px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
}
.org-list-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.org-list-title {
  font-size: 13px;
  font-weight: 600;
  color: #111827;
}
.org-chips-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.org-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 9px;
  border: 1px solid #e5e7eb;
  background: #ffffff;
  font-size: 12px;
  color: #111827;
}
.org-chip input[type='checkbox'] {
  cursor: pointer;
}
.org-chip-label {
  white-space: nowrap;
}
.org-loading,
.org-empty {
  font-size: 13px;
  color: #6b7280;
}

/* файлы */
.files {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 6px;
}
.chip {
  background: #f3f4ff;
  border: 1px solid #e5e7eb;
  color: #111827;
  border-radius: 9px;
  padding: 4px 8px;
  font-size: 12px;
}

/* подсказка */
.hint {
  font-size: 11px;
  color: #9ca3af;
}

/* кнопки */
.actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 4px;
}
.btn {
  padding: 9px 18px;
  border-radius: 9px;
  border: 1px solid transparent;
  cursor: pointer;
  font-weight: 600;
  font-size: 13px;
}
.btn.primary {
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: #ffffff;
  box-shadow: 0 12px 22px rgba(34, 197, 94, 0.35);
}
.btn.primary:disabled {
  opacity: 0.6;
  cursor: default;
  box-shadow: none;
}
.btn.small {
  padding: 6px 12px;
  font-size: 12px;
}
.btn.ghost {
  background: #ffffff;
  color: #111827;
  border-color: #e5e7eb;
}
</style>
