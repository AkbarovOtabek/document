<script>
import axios from 'axios'
import { API_BASE_URL } from '@/API'
import AddAnswerLetterForOther from './AddAnswerLetterForOther.vue'

export default {
  name: 'AddLetterOther',
  components: {
    AddAnswerLetterForOther,
  },
  data() {
    return {
      // режим: create — создать письмо, reply — добавить ответ
      mode: 'create',

      categories: [],
      loadingCategories: false,
      form: {
        category_id: '',
        number: '',
        name: '',
        registration_date: '',
        incoming_date: '',
        performer: '',
        internal_letter_number: '',
        description: '',
        files: [],
      },
      uploading: false,
      submitStatus: null,
      submitMessage: '',
    }
  },
  async created() {
    await this.loadCategories()
  },
  methods: {
    async loadCategories() {
      this.loadingCategories = true
      try {
        const { data } = await axios.get(
          `${API_BASE_URL}/api/external-letters/categories/`
        )
        const rows = Array.isArray(data.results) ? data.results : data
        this.categories = rows

        if (!this.form.category_id && this.categories.length) {
          this.form.category_id = this.categories[0].id
        }
      } catch (e) {
        console.error('Ошибка загрузки категорий писем', e)
      } finally {
        this.loadingCategories = false
      }
    },

    onFiles(e) {
      this.form.files = Array.from(e.target.files || [])
    },

    async submit() {
      if (!this.form.category_id) {
        this.submitStatus = 'error'
        this.submitMessage = 'Выберите систему / категорию.'
        return
      }

      this.uploading = true
      this.submitStatus = null
      this.submitMessage = ''

      try {
        const fd = new FormData()
        fd.append('category_id', this.form.category_id)
        fd.append('title', this.form.name)
        fd.append('description', this.form.description || '')
        fd.append('letter_number', this.form.number || '')
        fd.append(
          'internal_letter_number',
          this.form.internal_letter_number || ''
        )
        fd.append('executor', this.form.performer || '')
        fd.append('registration_date', this.form.registration_date || '')
        fd.append('incoming_date', this.form.incoming_date || '')

        if (this.form.files[0]) {
          fd.append('file', this.form.files[0])
        }

        await axios.post(
          `${API_BASE_URL}/api/external-letters/letters/`,
          fd,
          {
            headers: { 'Content-Type': 'multipart/form-data' },
          }
        )

        this.submitStatus = 'success'
        this.submitMessage = 'Письмо успешно добавлено.'

        this.form = {
          category_id: this.categories[0] ? this.categories[0].id : '',
          number: '',
          name: '',
          registration_date: '',
          incoming_date: '',
          performer: '',
          internal_letter_number: '',
          description: '',
          files: [],
        }
      } catch (e) {
        console.error('Ошибка создания письма', e)
        this.submitStatus = 'error'
        this.submitMessage = 'Ошибка при создании письма.'
      } finally {
        this.uploading = false
      }
    },
  },
}
</script>

<template>
  <div class="other-card">
    <!-- Табы: создать / добавить ответ -->
    <div class="tabs">
      <button
        type="button"
        class="tab-btn"
        :class="{ active: mode === 'create' }"
        @click="mode = 'create'"
      >
        Создать письмо
      </button>
      <button
        type="button"
        class="tab-btn"
        :class="{ active: mode === 'reply' }"
        @click="mode = 'reply'"
      >
        Добавить ответное письмо
      </button>
    </div>

    <!-- Режим: СОЗДАТЬ ПИСЬМО -->
    <transition name="fade">
      <div v-if="mode === 'create'">
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
          <div class="grid">
            <div class="col">
              <label>Система / Категория</label>
              <select v-model="form.category_id" :disabled="loadingCategories">
                <option value="" disabled>Выберите категорию</option>
                <option
                  v-for="cat in categories"
                  :key="cat.id"
                  :value="cat.id"
                >
                  {{ cat.code || cat.name || cat.slug }}
                </option>
              </select>
            </div>

            <div class="col">
              <label>Номер письма</label>
              <input v-model.trim="form.number" type="text" required />
            </div>
            <div class="col">
              <label>Номер регистрации</label>
              <input
                v-model.trim="form.internal_letter_number"
                type="text"
                required
              />
            </div>
          </div>

          <div class="grid">
            <div class="col">
              <label>Дата регистрации</label>
              <input v-model="form.registration_date" type="date" required />
            </div>
            <div class="col">
              <label>Дата прихода письма</label>
              <input v-model="form.incoming_date" type="date" />
            </div>
            <div class="row">
              <label>Исполнитель</label>
              <input v-model.trim="form.performer" type="text" />
            </div>
          </div>

          <div class="row">
            <label>Имя / Тема</label>
            <input v-model.trim="form.name" type="text" required />
          </div>

          <div class="row">
            <label>Описание</label>
            <textarea v-model.trim="form.description" rows="4" />
          </div>

          <div class="row">
            <label>Файлы</label>
            <input type="file" multiple @change="onFiles" />
            <div class="files" v-if="form.files.length">
              <span v-for="(f, i) in form.files" :key="i" class="chip">
                {{ f.name }}
              </span>
            </div>
          </div>

          <div class="actions">
            <button type="submit" class="btn primary" :disabled="uploading">
              {{ uploading ? 'Сохранение…' : 'Сохранить' }}
            </button>
          </div>
        </form>
      </div>
    </transition>

    <!-- Режим: ДОБАВИТЬ ОТВЕТНОЕ ПИСЬМО -->
    <div v-if="mode === 'reply'" class="reply-wrapper">
      <AddAnswerLetterForOther />
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

/* табы */
.tabs {
  display: inline-flex;
  gap: 6px;
  background: #f3f4f6;
  padding: 4px;
  border-radius: 999px;
  margin-bottom: 10px;
}
.tab-btn {
  border-radius: 999px;
  border: 1px solid transparent;
  padding: 6px 14px;
  font-size: 13px;
  cursor: pointer;
  background: transparent;
  color: #4b5563;
}
.tab-btn.active {
  background: #ffffff;
  border-color: #22c55e;
  color: #065f46;
  box-shadow: 0 4px 10px rgba(34, 197, 94, 0.25);
}

.reply-wrapper {
  margin-top: 4px;
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

/* форма */
.form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 12px;
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

/* элементы ввода */
input,
select,
textarea {
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
select:focus,
textarea:focus {
  border-color: #22c55e;
  background-color: #ffffff;
  box-shadow: 0 0 0 1px rgba(34, 197, 94, 0.15);
}
textarea {
  resize: vertical;
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

/* кнопки */
.actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 4px;
}
.btn {
  padding: 9px 18px;
  border-radius: 7px;
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
</style>
