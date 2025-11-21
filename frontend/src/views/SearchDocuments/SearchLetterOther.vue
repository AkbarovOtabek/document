<template>
  <div class="search-card">
    <form @submit.prevent="submit">
      <div class="grid">
        <div class="col">
          <label>Номер письма</label>
          <input
            v-model.trim="filters.number"
            type="text"
            placeholder="Например: 12-34/567"
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
          <label>Тема / предмет</label>
          <input
            v-model.trim="filters.subject"
            type="text"
            placeholder="Поиск по теме"
          />
        </div>
        <div class="col">
          <label>От кого (организация)</label>
          <input
            v-model.trim="filters.from_org"
            type="text"
            placeholder="Например: ЦБ РУз"
          />
        </div>
        <div class="col">
          <label>Кому (организация)</label>
          <input
            v-model.trim="filters.to_org"
            type="text"
            placeholder="Например: Наш банк"
          />
        </div>
      </div>

      <div class="row">
        <label>Текст письма / описание</label>
        <input
          v-model.trim="filters.query"
          type="text"
          placeholder="Поиск по тексту/описанию"
        />
      </div>

      <div class="actions">
        <button type="button" class="btn ghost" @click="reset">
          Сбросить
        </button>
        <button type="submit" class="btn primary">
          Применить
        </button>
      </div>
    </form>

    <!-- СПИСОК ПИСЕМ -->
    <div v-if="loading" class="letters-loading">Загрузка писем...</div>

    <div v-else-if="error" class="letters-error">
      {{ error }}
    </div>

    <div v-else>
      <div
        v-for="letter in letters"
        :key="letter.id"
        class="letter-item"
      >
        <div class="letter-main">
          <div class="letter-number">
            {{ letter.letter_number || letter.internal_letter_number || '—' }}
          </div>
          <div class="letter-subject">
            {{ letter.title || 'Без темы' }}
          </div>
        </div>

        <div class="letter-meta-row">
          <span class="tag">
            {{ formatDate(letter.registration_date || letter.incoming_date) }}
          </span>

          <span v-if="letter.executor" class="tag">
            Исполнитель: {{ letter.executor }}
          </span>

          <span v-if="letter.slug" class="tag">
            Слаг: {{ letter.slug }}
          </span>

          <span v-if="letter.category" class="tag">
            Категория: {{ letter.category.name }}
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

      <div v-if="!letters.length && !loading && !error" class="letters-empty">
        По выбранным фильтрам писем нет.
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { API_BASE_URL } from '@/API'

const EXTERNAL_LETTERS_URL = `${API_BASE_URL}api/external-letters/letters/`

export default {
  name: 'SearchLetterOther',
  props: {
    // id категории (Markaziy Bank Qarorlari / Nazorat Qumita Qarorlari ...)
    categoryId: {
      type: [Number, String],
      default: null,
    },
  },
  data() {
    return {
      filters: {
        number: '',
        date_from: '',
        date_to: '',
        subject: '',
        from_org: '',
        to_org: '',
        query: '',
      },

      allLetters: [], // все письма с backend
      letters: [],    // отфильтрованные по категории
      loading: false,
      error: '',
      pageSize: 15,
      count: 0,
    }
  },
  watch: {
    // при смене категории просто пере-фильтруем уже загруженный список
    categoryId() {
      this.applyCategoryFilter()
    },
  },
  async created() {
    await this.fetchLetters()
  },
  methods: {
    async fetchLetters() {
      this.loading = true
      this.error = ''
      try {
        const params = {
          ordering: '-registration_date', // последние сверху
        }

        // сюда НЕ передаём category — фильтруем на фронте
        Object.keys(this.filters).forEach((k) => {
          const v = this.filters[k]
          if (v !== '' && v != null) {
            params[k] = v
          }
        })

        const { data } = await axios.get(EXTERNAL_LETTERS_URL, { params })

        let items
        if (Array.isArray(data)) {
          items = data
        } else {
          items = data.results || []
        }

        this.allLetters = items
        this.applyCategoryFilter()
      } catch (e) {
        console.error('Ошибка загрузки писем external_letters', e)
        this.error = 'Ошибка загрузки писем. Попробуйте обновить страницу.'
        this.allLetters = []
        this.letters = []
        this.count = 0
      } finally {
        this.loading = false
      }
    },

    applyCategoryFilter() {
      // фильтрация по категории
      const cid = this.categoryId != null ? String(this.categoryId) : null

      let filtered = this.allLetters
      if (cid) {
        filtered = this.allLetters.filter(
          (l) =>
            l.category &&
            String(l.category.id) === cid
        )
      }

      // считаем и показываем только первые 15 (как ты просил по умолчанию)
      this.count = filtered.length
      this.letters = filtered.slice(0, this.pageSize)
    },

    submit() {
      // при новом поиске снова забираем с backend
      this.fetchLetters()
    },

    reset() {
      this.filters = {
        number: '',
        date_from: '',
        date_to: '',
        subject: '',
        from_org: '',
        to_org: '',
        query: '',
      }
      this.fetchLetters()
      this.$emit('reset')
    },

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
/* твои стили, оставил без изменений */
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

input {
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
input:focus {
  border-color: #22c55e;
  background-color: #ffffff;
  box-shadow: 0 0 0 1px rgba(34, 197, 94, 0.15);
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 6px;
}

.btn {
  padding: 8px 16px;
  border-radius: 9px;
  border: 1px solid transparent;
  cursor: pointer;
  font-weight: 600;
  font-size: 13px;
}
.btn.primary {
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: #ffffff;
}
.btn.ghost {
  background: #ffffff;
  color: #111827;
  border-color: #e5e7eb;
}
.btn.small {
  padding: 6px 10px;
  font-size: 12px;
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

.letters-loading,
.letters-error,
.letters-empty {
  font-size: 13px;
  color: #6b7280;
}

.letters-error {
  color: #b91c1c;
}

.letter-actions {
  margin-top: 4px;
  display: flex;
  justify-content: flex-end;
}
</style>
