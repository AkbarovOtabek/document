<script>
import axios from 'axios'
import { API_BASE_URL } from '@/API'

export default {
  name: 'SearchLetter',
  data() {
    return {
      // категории external_letters
      categories: [],
      loadingCategories: false,

      // активная "категория":
      // - slug обычной категории (nqq, mbq, ...)
      // - или спец-значение "__cert__" для CERT-CBU
      activeCategorySlug: null,

      // фильтры
      filters: {
        title: '',
        description: '',
        incoming_date: '',
        registration_date: '',
        letter_number: '',
        internal_letter_number: '',
        executor: '',
      },

      letters: [],
      loadingLetters: false,
      error: '',
      isSearchMode: false, // false = последние 10, true = результат фильтра
    }
  },

  async created() {
    await this.loadCategories()
  },

  methods: {
    /* ====== Загрузка категорий external_letters ====== */
    async loadCategories() {
      this.loadingCategories = true
      this.error = ''

      try {
        const { data } = await axios.get(
          `${API_BASE_URL}/api/external-letters/categories/`
        )

        const rows = Array.isArray(data.results) ? data.results : data
        this.categories = rows

        if (this.categories.length) {
          // по умолчанию — первая категория external_letters
          this.activeCategorySlug = this.categories[0].slug
          await this.loadLatestLetters()
        }
      } catch (e) {
        console.error('Ошибка загрузки категорий', e)
        this.error = 'Ошибка при загрузке категорий'
      } finally {
        this.loadingCategories = false
      }
    },

    /* ====== Универсальная загрузка последних 10 писем ======
       - если activeCategorySlug = обычный slug -> external_letters
       - если activeCategorySlug = "__cert__" -> cert_documents
    ========================================================== */
    async loadLatestLetters() {
      if (!this.activeCategorySlug) return

      this.loadingLetters = true
      this.error = ''
      this.isSearchMode = false
      this.letters = []

      try {
        let url = ''
        const params = {
          ordering: '-time_create',
        }

        if (this.activeCategorySlug === '__cert__') {
          // 🔸 CERT-CBU (новый backend cert_documents)
          // поменяешь путь при необходимости
          url = `${API_BASE_URL}/api/cert-documents/letters/`
        } else {
          // 🔹 обычные письма external_letters
          url = `${API_BASE_URL}/api/external-letters/letters/`
          params['category__slug'] = this.activeCategorySlug
        }

        const { data } = await axios.get(url, { params })
        const rows = Array.isArray(data.results) ? data.results : data

        // последние 10
        this.letters = rows.slice(0, 10)
      } catch (e) {
        console.error('Ошибка загрузки писем', e)
        this.error = 'Ошибка при загрузке писем'
      } finally {
        this.loadingLetters = false
      }
    },

    /* ====== Клик по обычной категории ====== */
    async onCategoryClick(slug) {
      if (this.activeCategorySlug === slug) return
      this.activeCategorySlug = slug
      await this.resetFiltersAndReload()
    },

    /* ====== Клик по CERT-CBU ====== */
    async onCertClick() {
      if (this.activeCategorySlug === '__cert__') return
      this.activeCategorySlug = '__cert__'
      await this.resetFiltersAndReload()
    },

    /* ====== Сброс фильтров + загрузка последних 10 по текущему источнику ====== */
    async resetFiltersAndReload() {
      this.filters = {
        title: '',
        description: '',
        incoming_date: '',
        registration_date: '',
        letter_number: '',
        internal_letter_number: '',
        executor: '',
      }
      await this.loadLatestLetters()
    },

    /* ====== Поиск по фильтрам ====== */
    async onSearch() {
      if (!this.activeCategorySlug) return

      this.loadingLetters = true
      this.error = ''
      this.isSearchMode = true
      this.letters = []

      try {
        let url = ''
        const params = {}

        if (this.activeCategorySlug === '__cert__') {
          // 🔸 поиск по CERT-CBU
          url = `${API_BASE_URL}/api/cert-documents/letters/`
          // тут можно добавлять свои спец-поля для CERT, если будут
        } else {
          // 🔹 поиск по обычным письмам
          url = `${API_BASE_URL}/api/external-letters/letters/`
          params['category__slug'] = this.activeCategorySlug
        }

        // Общие фильтры
        if (this.filters.title) {
          params['title__icontains'] = this.filters.title
        }
        if (this.filters.description) {
          params['description__icontains'] = this.filters.description
        }
        if (this.filters.letter_number) {
          params['letter_number__icontains'] = this.filters.letter_number
        }
        if (this.filters.internal_letter_number) {
          params['internal_letter_number__icontains'] =
            this.filters.internal_letter_number
        }
        if (this.filters.executor) {
          params['executor__icontains'] = this.filters.executor
        }
        if (this.filters.registration_date) {
          params['registration_date'] = this.filters.registration_date
        }
        if (this.filters.incoming_date) {
          params['incoming_date'] = this.filters.incoming_date
        }

        const { data } = await axios.get(url, { params })
        const rows = Array.isArray(data.results) ? data.results : data
        this.letters = rows
      } catch (e) {
        console.error('Ошибка поиска писем', e)
        this.error = 'Ошибка при поиске писем'
      } finally {
        this.loadingLetters = false
      }
    },

    async onReset() {
      this.isSearchMode = false
      await this.resetFiltersAndReload()
    },

    /* ====== Сборка ссылки на файл ====== */
    fileUrl(row) {
      if (!row.file) return null
      if (row.file.startsWith('http')) return row.file
      const base = API_BASE_URL.replace(/\/+$/, '')
      const path = String(row.file).replace(/^\/+/, '')
      return `${base}/${path}`
    },

    /* ====== Читаемое имя источника для шапки ====== */
    currentSourceLabel() {
      if (this.activeCategorySlug === '__cert__') return 'CERT-CBU'
      const cat = this.categories.find(c => c.slug === this.activeCategorySlug)
      return cat ? (cat.badge || cat.name || cat.slug) : this.activeCategorySlug
    },
  },
}
</script>

<template>
  <div class="search-letters">
    <h3>Поиск писем</h3>

    <!-- Категории + CERT-CBU -->
    <div class="categories">
      <button
        v-for="cat in categories"
        :key="cat.id"
        class="cat-btn"
        :class="{ active: cat.slug === activeCategorySlug }"
        @click="onCategoryClick(cat.slug)"
      >
        {{ cat.badge || cat.name || cat.slug }}
      </button>

      <!-- Отдельная кнопка для CERT-CBU -->
      <button
        class="cat-btn cert"
        :class="{ active: activeCategorySlug === '__cert__' }"
        @click="onCertClick"
      >
        CERT-CBU
      </button>
    </div>

    <!-- Фильтры -->
    <div class="filters">
      <div class="row">
        <div class="col">
          <label>Название / Тема (title)</label>
          <input
            v-model.trim="filters.title"
            type="text"
            placeholder="Название письма"
          />
        </div>
        <div class="col">
          <label>Номер письма (letter_number)</label>
          <input
            v-model.trim="filters.letter_number"
            type="text"
            placeholder="Внешний №"
          />
        </div>
        <div class="col">
          <label>Внутренний № (internal_letter_number)</label>
          <input
            v-model.trim="filters.internal_letter_number"
            type="text"
            placeholder="Внутренний номер"
          />
        </div>
      </div>

      <div class="row">
        <div class="col">
          <label>Исполнитель (executor)</label>
          <input
            v-model.trim="filters.executor"
            type="text"
            placeholder="ФИО исполнителя"
          />
        </div>
        <div class="col">
          <label>Дата регистрации (registration_date)</label>
          <input
            v-model="filters.registration_date"
            type="date"
          />
        </div>
        <div class="col">
          <label>Дата прихода (incoming_date)</label>
          <input
            v-model="filters.incoming_date"
            type="date"
          />
        </div>
      </div>

      <div class="row">
        <div class="col full">
          <label>Описание (description)</label>
          <input
            v-model.trim="filters.description"
            type="text"
            placeholder="Ключевые слова в описании"
          />
        </div>
      </div>

      <div class="actions">
        <button
          class="btn ghost"
          @click="onReset"
          :disabled="loadingLetters"
        >
          Сброс
        </button>
        <button
          class="btn primary"
          @click="onSearch"
          :disabled="loadingLetters"
        >
          {{ loadingLetters ? 'Поиск…' : 'Искать' }}
        </button>
      </div>
    </div>

    <!-- Ошибка -->
    <div v-if="error" class="error">
      {{ error }}
    </div>

    <!-- Таблица результатов -->
    <div class="results" v-if="letters.length && !error">
      <div class="results-header">
        <span v-if="!isSearchMode">
          Показаны последние 10 писем источника:
          <b>{{ currentSourceLabel() }}</b>
        </span>
        <span v-else>
          Результаты поиска (источник:
          <b>{{ currentSourceLabel() }}</b>)
        </span>
      </div>

      <table>
        <thead>
          <tr>
            <th>Источник</th>
            <th>Название</th>
            <th>Внешний №</th>
            <th>Внутренний №</th>
            <th>Исполнитель</th>
            <th>Рег. дата</th>
            <th>Дата прихода</th>
            <th>Файл</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="l in letters" :key="l.id">
            <td>
              <!-- для external_letters придёт объект category, для CERT-CBU можешь отдать своё поле -->
              {{ l.category?.badge || l.category?.name || (activeCategorySlug === '__cert__' ? 'CERT-CBU' : '-') }}
            </td>
            <td>{{ l.title }}</td>
            <td>{{ l.letter_number }}</td>
            <td>{{ l.internal_letter_number }}</td>
            <td>{{ l.executor }}</td>
            <td>{{ l.registration_date }}</td>
            <td>{{ l.incoming_date }}</td>
            <td>
              <a
                v-if="fileUrl(l)"
                :href="fileUrl(l)"
                target="_blank"
                rel="noopener noreferrer"
              >
                Открыть
              </a>
              <span v-else>-</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div
      v-else-if="!loadingLetters && !error"
      class="empty"
    >
      Нет писем для выбранного источника
    </div>
  </div>
</template>

<style scoped>
.search-letters {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

h3 {
  margin: 0 0 4px;
}

/* Категории */
.categories {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}

.cat-btn {
  padding: 6px 12px;
  border-radius: 9px;
  border: 1px solid #e5e7eb;
  background: #f3f4f6;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
}

.cat-btn.active {
  background: #111827;
  color: #fff;
  border-color: #111827;
}

.cat-btn.cert {
  border-style: dashed;
}

/* Фильтры */
.filters {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 10px;
  border-radius: 7px;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
}

.row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 10px;
}

.col {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.col.full {
  grid-column: 1 / 4;
}

label {
  font-size: 12px;
  opacity: 0.7;
}

input {
  height: 36px;
  border: 1px solid #e5e7eb;
  border-radius: 7px;
  padding: 6px 10px;
}

/* Кнопки действий */
.actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 6px;
}

.btn {
  padding: 8px 14px;
  border-radius: 7px;
  border: 1px solid transparent;
  cursor: pointer;
  font-weight: 700;
}

.btn.ghost {
  background: #f3f4f6;
}

.btn.primary {
  background: #2563eb;
  color: #fff;
}

/* Результаты */
.results {
  margin-top: 4px;
  overflow: auto;
}

.results-header {
  margin-bottom: 6px;
  font-size: 13px;
  opacity: 0.8;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 8px 10px;
  border-bottom: 1px solid #eef2f7;
  font-size: 13px;
  text-align: left;
}

.error {
  margin-top: 8px;
  font-size: 13px;
  color: #b91c1c;
}

.empty {
  margin-top: 10px;
  font-size: 13px;
  opacity: 0.6;
}
</style>
