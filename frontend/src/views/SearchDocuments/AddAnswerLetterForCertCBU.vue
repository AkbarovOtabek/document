<template>
  <div class="card">
    <div class="card-head">
      <h3>Добавление ответа на письмо CERT-CBU</h3>
    </div>

    <div class="card-body">
      <!-- ШАГ 1: выбор письма CERT-CBU из базы -->
      <div class="block">
        <div class="block-title">1. Выберите письмо CERT-CBU</div>

        <div class="grid">
          <div class="col">
            <label>Поиск по номеру / теме</label>
            <input
              v-model.trim="searchQuery"
              type="text"
              placeholder="Например: 45-17/..."
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
                {{ l.number }} — {{ shortText(l.subject) }} ({{ formatDate(l.date) }})
              </option>
            </select>
          </div>
        </div>

        <div v-if="loadingLetters" class="hint">
          Загрузка писем…
        </div>
        <div v-if="errorLetters" class="error-text">
          {{ errorLetters }}
        </div>

        <!-- Краткая информация о выбранном письме -->
        <div
          v-if="currentLetter"
          class="letter-summary"
        >
          <div class="summary-row">
            <span class="summary-label">Номер:</span>
            <span class="summary-value">{{ currentLetter.number }}</span>
          </div>
          <div class="summary-row">
            <span class="summary-label">Дата:</span>
            <span class="summary-value">{{ formatDate(currentLetter.date) }}</span>
          </div>
          <div class="summary-row">
            <span class="summary-label">Тема:</span>
            <span class="summary-value">{{ currentLetter.subject }}</span>
          </div>
          <div class="summary-row">
            <span class="summary-label">Исполнитель:</span>
            <span class="summary-value">
              {{ currentLetter.performer_name || currentLetter.performer || '—' }}
            </span>
          </div>
        </div>
      </div>

      <!-- ШАГ 2: выбор организации-ответчика -->
      <div class="block" v-if="currentLetter">
        <div class="block-title">2. Организация, от которой пришёл ответ</div>

        <div class="grid">
          <div class="col">
            <label>Организация</label>
            <select v-model="form.organization">
              <option value="">— Выберите организацию —</option>
              <option
                v-for="org in recipientOrganizations"
                :key="org.id"
                :value="org.id"
              >
                {{ org.name }}
              </option>
            </select>
            <div v-if="selectedOrgTypeName" class="hint">
              Тип организации: {{ selectedOrgTypeName }}
            </div>
          </div>
        </div>

        <div v-if="!recipientOrganizations.length" class="hint">
          Для выбранного письма не найдено организаций в поле <code>dest_organizations</code>.
        </div>
      </div>

      <!-- ШАГ 3: данные по ответному письму -->
      <div class="block" v-if="currentLetter">
        <div class="block-title">3. Данные ответного письма</div>

        <!-- номер ответного письма + внутренний номер -->
        <div class="grid">
          <div class="col">
            <label>Номер ответного письма</label>
            <input
              v-model.trim="form.reply_number"
              type="text"
              placeholder="Например: 01-12/345"
            />
          </div>
          <div class="col">
            <label>Внутренний номер (если есть)</label>
            <input
              v-model.trim="form.internal_number"
              type="text"
              placeholder="Можно оставить пустым"
            />
          </div>
        </div>

        <!-- дата + файл -->
        <div class="grid">
          <div class="col">
            <label>Дата приёма ответа</label>
            <input
              v-model="form.received_date"
              type="date"
            />
          </div>

          <div class="col">
            <label>Файл ответного письма</label>
            <input type="file" @change="onFileChange" />
          </div>
        </div>

        <div class="hint">
          Пользователь, добавивший ответ, и дата добавления проставляются автоматически (на бэкенде).
        </div>
      </div>

      <!-- КНОПКИ СОХРАНЕНИЯ -->
      <div class="actions" v-if="currentLetter">
        <button
          type="button"
          class="btn ghost"
          @click="resetForm"
        >
          Сбросить
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

      <div v-if="errorSubmit" class="error-text">
        {{ errorSubmit }}
      </div>
      <div v-if="successMessage" class="success-text">
        {{ successMessage }}
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { API_BASE_URL } from '@/API'

const CERT_LETTERS_URL = `${API_BASE_URL}api/cert-documents/letters/`
const LETTER_REPLIES_URL = `${API_BASE_URL}api/cert-documents/letter-replies/`
const ORG_LIST_URL = `${API_BASE_URL}api/organizations/list`

export default {
  name: 'AddAnswerLetterForCertCBU',

  data() {
    return {
      // список писем CERT-CBU
      letters: [],
      loadingLetters: false,
      errorLetters: '',
      searchQuery: '',
      selectedLetterId: '',

      // полный список организаций для выбранного письма
      organizationsIndex: {}, // id -> объект org
      recipientOrganizations: [],

      // форма ответного письма
      form: {
        organization: '',
        reply_number: '',     // номер ответного письма
        internal_number: '',  // внутренний номер (может быть пустым)
        received_date: '',
        file: null,
      },

      saving: false,
      errorSubmit: '',
      successMessage: '',

      // внутренняя ссылка на таймер для debounce
      debounceTimer: null,
    }
  },

  computed: {
    currentLetter() {
      if (!this.selectedLetterId) return null
      return (
        this.letters.find((l) => l.id === Number(this.selectedLetterId)) || null
      )
    },

    selectedOrgTypeName() {
      const id = this.form.organization
      if (!id) return ''
      const org = this.recipientOrganizations.find(
        (o) => o.id === Number(id)
      )
      if (!org) return ''
      return (
        (org.organization_type && org.organization_type.name) ||
        (org.type && org.type.name) ||
        org.type_name ||
        (org.category && org.category.name) ||
        org.category_name ||
        ''
      )
    },
  },

  created() {
    this.fetchLetters()
  },

  watch: {
    // когда выбрали письмо — подгружаем организации по dest_organizations
    currentLetter: {
      immediate: false,
      handler(newVal) {
        if (!newVal) {
          this.recipientOrganizations = []
          this.organizationsIndex = {}
          this.form.organization = ''
          return
        }
        this.loadOrganizationsForLetter(newVal)
      },
    },
  },

  methods: {
    shortText(text, maxLen = 40) {
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

    // ---- Загрузка писем CERT-CBU ----
    async fetchLetters() {
      this.loadingLetters = true
      this.errorLetters = ''
      try {
        const params = {
          system: 'CERT-CBU',
          page_size: 100,
          ordering: '-date',
        }

        if (this.searchQuery) {
          // можно использовать search или number/subject
          params.search = this.searchQuery
        }

        const { data } = await axios.get(CERT_LETTERS_URL, { params })

        if (Array.isArray(data)) {
          this.letters = data
        } else {
          this.letters = data.results || []
        }
      } catch (e) {
        console.error('Ошибка загрузки писем CERT-CBU', e)
        this.errorLetters = 'Не удалось загрузить письма.'
        this.letters = []
      } finally {
        this.loadingLetters = false
      }
    },

    debouncedFetchLetters() {
      clearTimeout(this.debounceTimer)
      this.debounceTimer = setTimeout(() => {
        this.fetchLetters()
      }, 400)
    },

    onLetterChange() {
      this.successMessage = ''
      this.errorSubmit = ''
      // currentLetter в watch сам подгрузит организации
    },

    // ---- Загрузка организаций для выбранного письма ----
    async loadOrganizationsForLetter(letter) {
      const ids = Array.isArray(letter.dest_organizations)
        ? letter.dest_organizations
        : []

      if (!ids.length) {
        this.recipientOrganizations = []
        this.organizationsIndex = {}
        this.form.organization = ''
        return
      }

      try {
        const { data } = await axios.get(ORG_LIST_URL)

        const allItems = Array.isArray(data)
          ? data
          : Array.isArray(data.results)
          ? data.results
          : []

        const items = allItems.filter((org) => ids.includes(org.id))

        const index = {}
        items.forEach((org) => {
          if (org && org.id) {
            index[org.id] = org
          }
        })

        this.organizationsIndex = index
        this.recipientOrganizations = items
        // если одна организация — сразу подставим её
        if (items.length === 1) {
          this.form.organization = items[0].id
        } else {
          this.form.organization = ''
        }
      } catch (e) {
        console.error('Ошибка загрузки организаций для письма', e)
        this.recipientOrganizations = []
        this.organizationsIndex = {}
      }
    },

    onFileChange(e) {
      const file = e.target.files && e.target.files[0]
      this.form.file = file || null
    },

    resetForm() {
      this.form = {
        organization: '',
        reply_number: '',
        internal_number: '',
        received_date: '',
        file: null,
      }
      this.errorSubmit = ''
      this.successMessage = ''
    },

    async submit() {
      this.errorSubmit = ''
      this.successMessage = ''

      if (!this.currentLetter) {
        this.errorSubmit = 'Выберите письмо CERT-CBU.'
        return
      }
      if (!this.form.organization) {
        this.errorSubmit = 'Выберите организацию-ответчика.'
        return
      }
      if (!this.form.received_date) {
        this.errorSubmit = 'Укажите дату приёма ответного письма.'
        return
      }
      if (!this.form.file) {
        this.errorSubmit = 'Выберите файл ответного письма.'
        return
      }

      const fd = new FormData()
      fd.append('letter', this.currentLetter.id)
      fd.append('organization', this.form.organization)
      fd.append('received_date', this.form.received_date)
      fd.append('file', this.form.file)
      // новые поля — номер и внутренний номер
      fd.append('reply_number', this.form.reply_number || '')
      fd.append('internal_number', this.form.internal_number || '')

      this.saving = true
      try {
        await axios.post(LETTER_REPLIES_URL, fd, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })

        this.successMessage = 'Ответное письмо успешно добавлено.'
        this.resetForm()
        // можно эмитнуть событие наверх, если нужно обновить список
        this.$emit('reply-created')
      } catch (e) {
        console.error('Ошибка сохранения ответного письма', e)
        this.errorSubmit = 'Не удалось сохранить ответное письмо.'
      } finally {
        this.saving = false
      }
    },
  },
}
</script>

<style scoped>
.card {
  border-radius: 7px;
  border: 1px solid #e5e7eb;
  background: #ffffff;
  padding: 14px 16px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.card-head h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: ۱۲px;
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

.grid {
  display: grid;
  grid-template-columns: 1.2fr 1.2fr;
  gap: 10px;
}
.col {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #9ca3af;
}

input,
select {
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
input::placeholder {
  color: #9ca3af;
}
input:focus,
select:focus {
  border-color: #22c55e;
  background-color: #ffffff;
  box-shadow: 0 0 0 1px rgba(34, 197, 94, 0.15);
}

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

.success-text {
  font-size: 12px;
  color: #16a34a;
}

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
