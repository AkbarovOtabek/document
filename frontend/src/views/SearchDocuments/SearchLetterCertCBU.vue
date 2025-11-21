<template>
  <div class="search-card">
    <!-- ФОРМА ФИЛЬТРОВ -->
    <form @submit.prevent="submit">
      <div class="grid">
        <div class="col">
          <label>Номер письма</label>
          <input
            v-model.trim="filters.number"
            type="text"
            placeholder="Например: CERT/24-01"
          />
        </div>
        <div class="col">
          <label>Дата с</label>
          <input v-model="filters.date_from" type="date" />
        </div>
        <div class="col">
          <label>Дата по</label>
          <input v-model="filters.date_to" type="date" />
        </div>
      </div>

      <div class="grid">
        <div class="col">
          <label>Тема / титул</label>
          <input
            v-model.trim="filters.subject"
            type="text"
            placeholder="Поиск по теме"
          />
        </div>

        <div class="col">
          <label>Исполнитель</label>
          <select v-model="filters.performer">
            <option value="">— Все исполнители —</option>
            <option
              v-for="person in performerOptions"
              :key="person.id"
              :value="person.id"
            >
              {{ person.full_name }} — {{ person.position }}
            </option>
          </select>

          <small v-if="loadingPerformers" class="hint">
            Загрузка списка сотрудников…
          </small>
        </div>

        <div class="col">
          <label class="deadline-label">
            <input type="checkbox" v-model="filters.only_with_deadline" />
            Только с установленным сроком
          </label>
          <input
            v-model="filters.deadline_to"
            type="date"
            :disabled="!filters.only_with_deadline"
            placeholder="Срок до"
          />
        </div>
      </div>

      <div class="row">
        <label>Описание / требуемые действия</label>
        <input
          v-model.trim="filters.query"
          type="text"
          placeholder="Поиск по описанию"
        />
      </div>

      <div class="actions">
        <button type="button" class="btn ghost" @click="reset">
          Сбросить
        </button>
        <button type="submit" class="btn primary">Применить</button>
      </div>
    </form>

    <!-- СПИСОК ПИСЕМ CERT-CBU -->
    <div class="letters-block">
      <div class="letters-head">
        <div class="letters-title">
          Письма CERT-CBU
        </div>
        <div class="letters-meta" v-if="count">
          Найдено: {{ count }} письм(а)
        </div>
      </div>

      <div v-if="loadingLetters" class="letters-loading">
        Загрузка писем…
      </div>

      <div v-else-if="errorLetters" class="letters-error">
        {{ errorLetters }}
      </div>

      <div v-else>
        <div
          v-for="letter in letters"
          :key="letter.id"
          class="letter-item"
        >
          <div class="letter-main">
            <div class="letter-number">
              {{ letter.number || letter.letter_number || '—' }}
            </div>
            <div class="letter-subject">
              {{ letter.title || letter.subject || 'Без темы' }}
            </div>
          </div>

          <div class="letter-meta-row">
            <span class="tag">
              {{ formatDate(letter.registration_date || letter.date || letter.created_at) }}
            </span>

            <span v-if="letter.performer_name || letter.performer" class="tag">
              Исполнитель: {{ letter.performer_name || letter.performer }}
            </span>

            <span v-if="letter.deadline" class="tag">
              Срок: {{ formatDate(letter.deadline) }}
            </span>
          </div>

          <!-- КНОПКА "ПРОСМОТРЕТЬ ДЕТАЛЬНО" -->
          <div class="letter-actions">
            <button
              type="button"
              class="btn small"
              @click="$emit('open-detail', letter)"
            >
              Просмотреть детально
            </button>
          </div>
        </div>

        <div
          v-if="!letters.length && !loadingLetters && !errorLetters"
          class="letters-empty"
        >
          По выбранным фильтрам писем нет.
        </div>
      </div>

      <!-- ПАГИНАЦИЯ -->
      <div v-if="count > pageSize" class="pagination">
        <button
          type="button"
          class="btn small ghost"
          :disabled="page <= 1"
          @click="changePage(page - 1)"
        >
          ‹ Предыдущая
        </button>
        <div class="pagination-info">
          Страница {{ page }} из {{ totalPages }}
        </div>
        <button
          type="button"
          class="btn small ghost"
          :disabled="page >= totalPages"
          @click="changePage(page + 1)"
        >
          Следующая ›
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { API_BASE_URL } from '@/API'

const CERT_LETTERS_URL = `${API_BASE_URL}api/cert-documents/letters/`

export default {
  name: 'SearchLetterCertCBU',

  data() {
    return {
      // фильтры формы
      filters: {
        number: '',
        date_from: '',
        date_to: '',
        subject: '',
        performer: '',
        only_with_deadline: false,
        deadline_to: '',
        query: '',
      },

      // исполнители
      performerOptions: [],
      loadingPerformers: false,

      // письма CERT
      letters: [],
      loadingLetters: false,
      errorLetters: '',
      page: 1,
      pageSize: 15,
      count: 0,
    }
  },

  computed: {
    totalPages() {
      if (!this.count) return 1
      return Math.max(1, Math.ceil(this.count / this.pageSize))
    },
  },

  async created() {
    await this.loadPerformers()
    await this.fetchLetters()
  },

  methods: {
    /** Загрузка списка сотрудников */
    async loadPerformers() {
      this.loadingPerformers = true
      try {
        const { data } = await axios.get(
          `${API_BASE_URL}api/staff/users/`
        )

        const items = Array.isArray(data)
          ? data
          : Array.isArray(data.results)
          ? data.results
          : []

        this.performerOptions = items.map(person => {
          const full_name =
            person.full_name ||
            person.fio ||
            [person.last_name, person.first_name, person.middle_name]
              .filter(Boolean)
              .join(' ') ||
            '—'

          const position =
            person.position || person.role || person.job_title || '—'

          return {
            id: person.id,
            full_name,
            position,
          }
        })
      } catch (e) {
        console.error('Ошибка загрузки сотрудников', e)
        this.performerOptions = []
      } finally {
        this.loadingPerformers = false
      }
    },

    /** Загрузка писем CERT-CBU с учётом фильтров */
    async fetchLetters() {
      this.loadingLetters = true
      this.errorLetters = ''
      try {
        const params = {
          page: this.page,
          page_size: this.pageSize,
          // сортируем по дате письма (в твоём ответе поле называлось date)
          ordering: '-date',
          // чтобы точно брать только CERT-CBU
          system: 'CERT-CBU',
        }

        // Мэппинг фильтров формы → параметры API
        if (this.filters.number) {
          params.number = this.filters.number
        }
        if (this.filters.date_from) {
          // если на бэке фильтр называется по другому — здесь легко поменять
          params.date_from = this.filters.date_from
        }
        if (this.filters.date_to) {
          params.date_to = this.filters.date_to
        }
        if (this.filters.subject) {
          params.subject = this.filters.subject
        }
        if (this.filters.performer) {
          params.performer = this.filters.performer
        }
        if (this.filters.only_with_deadline) {
          // в данных есть поле has_deadline: true/false
          params.has_deadline = true
        }
        if (this.filters.deadline_to) {
          // например, фильтрация писем со сроком до даты
          params.deadline_to = this.filters.deadline_to
        }
        if (this.filters.query) {
          // общий текстовый поиск
          params.search = this.filters.query
        }

        const { data } = await axios.get(CERT_LETTERS_URL, { params })

        if (Array.isArray(data)) {
          this.letters = data
          this.count = data.length
        } else {
          this.letters = data.results || []
          this.count = data.count ?? this.letters.length
        }
      } catch (e) {
        console.error('Ошибка загрузки писем CERT-CBU', e)
        this.errorLetters = 'Ошибка загрузки писем. Попробуйте позже.'
        this.letters = []
        this.count = 0
      } finally {
        this.loadingLetters = false
      }
    },

    /** Применение фильтров */
    submit() {
      this.page = 1
      this.fetchLetters()
    },

    /** Сброс фильтров */
    reset() {
      this.filters = {
        number: '',
        date_from: '',
        date_to: '',
        subject: '',
        performer: '',
        only_with_deadline: false,
        deadline_to: '',
        query: '',
      }

      this.page = 1
      this.fetchLetters()
    },

    /** Переход по страницам */
    changePage(newPage) {
      if (newPage < 1 || newPage > this.totalPages) return
      this.page = newPage
      this.fetchLetters()
    },

    /** Форматирование даты */
    formatDate(value) {
      if (!value) return '—'
      try {
        const d = new Date(value)
        if (Number.isNaN(d.getTime())) return value
        const dd = String(d.getDate()).padStart(2, '0')
        const mm = String(d.getMonth() + 1).padStart(2, '0')
        const yyyy = d.getFullYear()
        return `${dd}.${mm}.${yyyy}`
      } catch (e) {
        return value
      }
    },
  },
}
</script>

<style scoped>
.search-card {
  border-radius: 7px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  padding: 10px 12px 12px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.grid {
  display: grid;
  grid-template-columns: 1.2fr 1fr 1fr;
  gap: 10px;
}
.row {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.col {
  display: flex;
  flex-direction: column;
  gap: 6px;
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

.deadline-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #4b5563;
}

.hint {
  font-size: 11px;
  color: #9ca3af;
  margin-top: 2px;
}

/* Блок писем */
.letters-block {
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px dashed #e5e7eb;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.letters-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.letters-title {
  font-size: 13px;
  font-weight: 600;
  color: #111827;
}
.letters-meta {
  font-size: 12px;
  color: #6b7280;
}

.letters-loading,
.letters-error,
.letters-empty {
  font-size: 13px;
  color: #6b7280;
}

.letters-error {
  color: #b91c1c;
}

.letter-item {
  padding: 8px 10px;
  border-radius: 7px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 6px;
}

.letter-main {
  display: flex;
  gap: 8px;
  align-items: baseline;
}

.letter-number {
  font-weight: 600;
  font-size: 13px;
  color: #111827;
  white-space: nowrap;
}

.letter-subject {
  font-size: 13px;
  color: #374151;
}

.letter-meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 2px;
}

.tag {
  font-size: 11px;
  border-radius: 999px;
  padding: 3px 8px;
  background: #f3f4ff;
  color: #4b5563;
}

.letter-actions {
  margin-top: 4px;
  display: flex;
  justify-content: flex-end;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: 6px;
}

.pagination-info {
  font-size: 12px;
  color: #4b5563;
}
</style>
