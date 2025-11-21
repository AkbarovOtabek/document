<script>
import axios from 'axios'
import { API_BASE_URL } from '@/API'

const CATEGORIES_URL = `${API_BASE_URL}/api/external-letters/categories/`
const LETTERS_URL = `${API_BASE_URL}/api/external-letters/letters/`
const REPLIES_URL = `${API_BASE_URL}/api/external-letters/replies/`
const EMPLOYEES_URL = `${API_BASE_URL}/api/staff/users/` // при необходимости поменяй

export default {
  name: 'AddAnswerLetterForOther',

  data() {
    return {
      // категории писем (ExternalLettersCategory)
      categories: [],
      loadingCategories: false,

      // письма ExternalLetter
      letters: [],
      loadingLetters: false,
      lettersError: '',

      // выбор/фильтрация
      selectedCategorySlug: '',
      letterSearch: '',
      selectedLetterId: '',

      // сотрудники (исполнители)
      employees: [],
      loadingEmployees: false,
      employeeSearch: '',

      // форма ответного письма
      form: {
        reply_number: '',
        internal_number: '',
        performer: '',  // ID сотрудника (если добавишь поле на бэке)
        sent_date: '',
        file: null,
      },

      saving: false,
      submitStatus: null,
      submitMessage: '',
      lastCreatedReply: null, // данные созданного ответа
      debounceTimer: null,
    }
  },

  computed: {
    currentLetter() {
      if (!this.selectedLetterId) return null
      return this.letters.find(l => l.id === Number(this.selectedLetterId)) || null
    },

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

    addedAtFormatted() {
      if (!this.lastCreatedReply || !this.lastCreatedReply.added_at) return ''
      const d = new Date(this.lastCreatedReply.added_at)
      if (Number.isNaN(d.getTime())) return this.lastCreatedReply.added_at
      return d.toLocaleString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    },
  },

  async created() {
    await Promise.all([
      this.loadCategories(),
      this.loadEmployees(),
    ])
    await this.fetchLetters()
  },

  methods: {
    shortText(text, maxLen = 50) {
      if (!text) return ''
      if (text.length <= maxLen) return text
      return text.slice(0, maxLen) + '…'
    },

    formatDate(val) {
      if (!val) return '—'
      const d = new Date(val)
      if (Number.isNaN(d.getTime())) return val
      return d.toLocaleDateString('ru-RU')
    },

    // ===== КАТЕГОРИИ =====
    async loadCategories() {
      this.loadingCategories = true
      try {
        const { data } = await axios.get(CATEGORIES_URL)
        const rows = Array.isArray(data.results) ? data.results : data
        this.categories = rows || []

        if (!this.selectedCategorySlug && this.categories.length) {
          this.selectedCategorySlug = this.categories[0].slug
        }
      } catch (e) {
        console.error('Ошибка загрузки категорий external_letters', e)
      } finally {
        this.loadingCategories = false
      }
    },

    // ===== СОТРУДНИКИ =====
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

    // ===== ПИСЬМА ExternalLetter =====
    async fetchLetters() {
      this.loadingLetters = true
      this.lettersError = ''
      try {
        const params = {
          page_size: 100,
          ordering: '-time_create',
        }

        if (this.selectedCategorySlug) {
          params['category__slug'] = this.selectedCategorySlug
        }
        if (this.letterSearch) {
          params.search = this.letterSearch
        }

        const { data } = await axios.get(LETTERS_URL, { params })
        if (Array.isArray(data)) {
          this.letters = data
        } else {
          this.letters = data.results || []
        }

        if (
          this.selectedLetterId &&
          !this.letters.some(l => l.id === Number(this.selectedLetterId))
        ) {
          this.selectedLetterId = ''
        }
      } catch (e) {
        console.error('Ошибка загрузки external_letters', e)
        this.lettersError = 'Не удалось загрузить письма.'
        this.letters = []
      } finally {
        this.loadingLetters = false
      }
    },

    onCategoryChange() {
      this.debouncedFetchLetters()
    },

    debouncedFetchLetters() {
      clearTimeout(this.debounceTimer)
      this.debounceTimer = setTimeout(() => {
        this.fetchLetters()
      }, 400)
    },

    onLetterChange() {
      this.submitStatus = null
      this.submitMessage = ''
      this.lastCreatedReply = null
    },

    onFileChange(e) {
      const file = e.target.files && e.target.files[0]
      this.form.file = file || null
    },

    resetForm() {
      this.form = {
        reply_number: '',
        internal_number: '',
        performer: '',
        sent_date: '',
        file: null,
      }
      this.submitStatus = null
      this.submitMessage = ''
      this.lastCreatedReply = null
    },

    async submit() {
      this.submitStatus = null
      this.submitMessage = ''
      this.lastCreatedReply = null

      if (!this.selectedLetterId) {
        this.submitStatus = 'error'
        this.submitMessage = 'Выберите входящее письмо.'
        return
      }
      if (!this.form.reply_number) {
        this.submitStatus = 'error'
        this.submitMessage = 'Укажите номер ответного письма.'
        return
      }
      if (!this.form.sent_date) {
        this.submitStatus = 'error'
        this.submitMessage = 'Укажите дату ответного письма.'
        return
      }
      if (!this.form.file) {
        this.submitStatus = 'error'
        this.submitMessage = 'Выберите файл ответного письма.'
        return
      }

      const fd = new FormData()
      fd.append('letter_id', this.selectedLetterId)
      fd.append('reply_number', this.form.reply_number || '')
      fd.append('internal_number', this.form.internal_number || '')
      fd.append('sent_date', this.form.sent_date || '')
      fd.append('file', this.form.file)

      // ⚠️ заработает только если добавишь поле performer на бэке
      if (this.form.performer) {
        fd.append('performer', this.form.performer)
      }

      this.saving = true
      try {
        const { data } = await axios.post(REPLIES_URL, fd, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })

        this.submitStatus = 'success'
        this.submitMessage = 'Ответное письмо успешно добавлено.'
        this.lastCreatedReply = data

        this.form.reply_number = ''
        this.form.internal_number = ''
        this.form.sent_date = ''
        this.form.file = null
        this.form.performer = ''
      } catch (e) {
        console.error('Ошибка сохранения ответного письма', e)
        this.submitStatus = 'error'
        this.submitMessage = 'Не удалось сохранить ответное письмо.'
      } finally {
        this.saving = false
      }
    },
  },
}
</script>

<template>
  <div class="other-card">
    <!-- уведомление -->
    <transition name="fade">
      <div
        v-if="submitStatus"
        class="alert"
        :class="submitStatus === 'success' ? 'alert-success' : 'alert-error'"
      >
        <div>{{ submitMessage }}</div>
        <div v-if="submitStatus === 'success' && addedAtFormatted" class="added-at">
          Добавлено в систему: {{ addedAtFormatted }}
        </div>
      </div>
    </transition>

    <div class="form">
      <!-- ШАГ 1: выбор входящего письма -->
      <div class="block">
        <div class="block-title">1. Выберите входящее письмо</div>

        <div class="grid">
          <div class="col">
            <label>Категория</label>
            <select
              v-model="selectedCategorySlug"
              :disabled="loadingCategories"
              @change="onCategoryChange"
            >
              <option value="">Все категории</option>
              <option
                v-for="cat in categories"
                :key="cat.id"
                :value="cat.slug"
              >
                {{ cat.name }}
              </option>
            </select>
          </div>

          <div class="col">
            <label>Поиск по номеру / теме</label>
            <input
              v-model.trim="letterSearch"
              type="text"
              placeholder="Номер, тема, внутренний номер…"
              @input="debouncedFetchLetters"
            />
          </div>

          <div class="col">
            <label>Письмо</label>
            <select v-model="selectedLetterId" @change="onLetterChange">
              <option value="">— Выберите письмо —</option>
              <option
                v-for="l in letters"
                :key="l.id"
                :value="l.id"
              >
                {{ l.letter_number || '№?' }} — {{ shortText(l.title) }}
                ({{ formatDate(l.registration_date || l.incoming_date || l.time_create) }})
              </option>
            </select>
          </div>
        </div>

        <div v-if="loadingLetters" class="hint">
          Загрузка писем…
        </div>
        <div v-if="lettersError" class="error-text">
          {{ lettersError }}
        </div>

        <!-- краткая информация о выбранном письме -->
        <div v-if="currentLetter" class="letter-summary">
          <div class="summary-row">
            <span class="summary-label">Номер:</span>
            <span class="summary-value">
              {{ currentLetter.letter_number || '—' }}
              <span v-if="currentLetter.internal_letter_number">
                (вн. {{ currentLetter.internal_letter_number }})
              </span>
            </span>
          </div>
          <div class="summary-row">
            <span class="summary-label">Категория:</span>
            <span class="summary-value">
              {{ currentLetter.category?.name || '—' }}
            </span>
          </div>
          <div class="summary-row">
            <span class="summary-label">Тема:</span>
            <span class="summary-value">
              {{ currentLetter.title }}
            </span>
          </div>
          <div class="summary-row">
            <span class="summary-label">Дата регистрации:</span>
            <span class="summary-value">
              {{ formatDate(currentLetter.registration_date || currentLetter.time_create) }}
            </span>
          </div>
        </div>
      </div>

      <!-- ШАГ 2: данные ответного письма -->
      <div class="block" v-if="currentLetter">
        <div class="block-title">2. Данные ответного письма</div>

        <div class="grid">
          <div class="col">
            <label>Номер нашего ответного письма</label>
            <input
              v-model.trim="form.reply_number"
              type="text"
              placeholder="Например: 01-17/1234"
            />
          </div>
          <div class="col">
            <label>Внутренний номер (если есть)</label>
            <input
              v-model.trim="form.internal_number"
              type="text"
              placeholder="Например: ВН-2025/07"
            />
          </div>
          <div class="col">
            <label>Дата письма (отправки)</label>
            <input
              v-model="form.sent_date"
              type="date"
            />
          </div>
        </div>

        <div class="grid">
          <div class="col">
            <label>Исполнитель</label>
            <input
              v-model.trim="employeeSearch"
              type="text"
              placeholder="Поиск по ФИО / username / email"
            />
            <select v-model="form.performer">
              <option value="">— Выберите исполнителя —</option>
              <option
                v-for="u in filteredEmployees"
                :key="u.id"
                :value="u.id"
              >
                {{ u.fio || u.full_name || u.username || u.email || ('ID ' + u.id) }}
              </option>
            </select>
            <small class="hint" v-if="loadingEmployees">
              Загрузка сотрудников…
            </small>
            <small
              v-else-if="!loadingEmployees && !filteredEmployees.length"
              class="hint"
            >
              Сотрудники не найдены
            </small>
          </div>

          <div class="col">
            <label>Файл ответного письма</label>
            <input type="file" @change="onFileChange" />
          </div>
        </div>

        <div class="hint">
          Дата добавления в систему и пользователь, добавивший ответ,
          проставляются автоматически на стороне сервера.
        </div>
      </div>

      <!-- КНОПКИ -->
      <div class="actions" v-if="currentLetter">
        <button
          type="button"
          class="btn ghost"
          @click="resetForm"
        >
          Сбросить форму
        </button>
        <button
          type="button"
          class="btn primary"
          :disabled="saving"
          @click="submit"
        >
          {{ saving ? 'Сохранение…' : 'Сохранить ответное письмо' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.other-card {
  width: 100%;
  background: #ffffff;
  border-radius: 7px;
  padding: 14px 14px 18px;
  border: 1px solid #e5e7eb;
  box-sizing: border-box;
}

/* уведомления */
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
.added-at {
  font-size: 11px;
  margin-top: 2px;
}

/* форма */
.form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.block {
  padding: 8px 10px;
  border-radius: 7px;
  border: 1px dashed #e5e7eb;
  background: #f9fafb;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.block-title {
  font-size: 13px;
  font-weight: 600;
  color: #111827;
}

/* сетка */
.grid {
  display: grid;
  grid-template-columns: 1.1fr 1.1fr 1.1fr;
  gap: 10px;
}
.col {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* подписи */
label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #9ca3af;
}

/* инпуты */
input,
select,
textarea {
  border-radius: 7px;
  padding: 8px 10px;
  min-height: 36px;
  border: 1px solid #e5e7eb;
  background: #ffffff;
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
select:focus,
textarea:focus {
  border-color: #22c55e;
  background-color: #ffffff;
  box-shadow: 0 0 0 1px rgba(34, 197, 94, 0.15);
}

/* кнопки */
.actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
.btn {
  padding: 8px 16px;
  border-radius: 999px;
  border: 1px solid #e5e7eb;
  cursor: pointer;
  font-weight: 600;
  font-size: 13px;
}
.btn.primary {
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: #ffffff;
  border-color: transparent;
}
.btn.ghost {
  background: #ffffff;
  color: #111827;
  border-color: #e5e7eb;
}

.hint {
  font-size: 11px;
  color: #6b7280;
}
.error-text {
  font-size: 12px;
  color: #b91c1c;
}

/* краткая инфа о письме */
.letter-summary {
  border-radius: 6px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  padding: 6px 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 12px;
}
.summary-row {
  display: flex;
  gap: 6px;
}
.summary-label {
  font-weight: 600;
  color: #4b5563;
}
.summary-value {
  color: #111827;
}
</style>
