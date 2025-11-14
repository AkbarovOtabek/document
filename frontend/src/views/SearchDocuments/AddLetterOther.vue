<script>
import axios from 'axios'
import { API_BASE_URL } from '@/API'          // как в остальных компонентах

export default {
  name: 'AddLetterOther',
  data() {
    return {
      categories: [],          // список категорий с backend
      loadingCategories: false,
      form: {
        category_id: '',       // выбранная категория (id)
        number: '',
        name: '',
        registration_date: '', // дата регистрации письма
        incoming_date: '',     // дата прихода письма
        performer: '',
        internal_letter_number:'',
        description: '',
        files: [],
      },
      uploading: false,
    }
  },
  async created() {
    await this.loadCategories()
  },
  methods: {
    async loadCategories() {
      this.loadingCategories = true
      try {
        const { data } = await axios.get(`${API_BASE_URL}/api/external-letters/categories/`)
        this.categories = data.results

        // по умолчанию выбираем первую категорию (например NQQ)
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
        alert('Выберите систему / категорию')
        return
      }

      this.uploading = true
      try {
        const fd = new FormData()

        // маппинг формы → поля backend
        fd.append('category_id', this.form.category_id)
        fd.append('title', this.form.name)                         // заголовок
        fd.append('description', this.form.description || '')
        fd.append('letter_number', this.form.number || '')
        fd.append('internal_letter_number', this.form.internal_letter_number || '')                    // если надо, потом добавим отдельное поле
        fd.append('executor', this.form.performer || '')
        fd.append('registration_date', this.form.registration_date || '')
        fd.append('incoming_date', this.form.incoming_date || '')

        // backend сейчас хранит один файл -> берём первый
        if (this.form.files[0]) {
          fd.append('file', this.form.files[0])
        }

        await axios.post(`${API_BASE_URL}/api/external-letters/letters/`, fd, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })

        alert('Письмо добавлено (Другие)')

        // сброс формы
        this.form = {
          category_id: this.categories[0] ? this.categories[0].id : '',
          number: '',
          name: '',
          registration_date: '',
          incoming_date: '',
          internal_letter_number:'',
          performer: '',
          description: '',
          files: [],
        }
      } catch (e) {
        console.error('Ошибка создания письма', e)
      } finally {
        this.uploading = false
      }
    },
  },
}
</script>

<template>
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
            <!-- если есть code — показываем его, иначе name/slug -->
            {{ cat.code || cat.name || cat.slug }}
          </option>
        </select>
      </div>

      <div class="col">
        <label>Номер письма</label>
        <input v-model.trim="form.number" type="text" required />
      </div>
      <div class="col">
        <label>Номер письма регистрации</label>
        <input v-model.trim="form.internal_letter_number" type="text" required />
      </div>

      <div class="col">
        <label>Дата регистрации</label>
        <input v-model="form.registration_date" type="date" required />
      </div>
    </div>

    <div class="grid">
      <div class="col">
        <label>Дата прихода письма</label>
        <input v-model="form.incoming_date" type="date" />
      </div>
    </div>

    <div class="row">
      <label>Имя / Тема</label>
      <input v-model.trim="form.name" type="text" required />
    </div>

    <div class="row">
      <label>Исполнитель</label>
      <input v-model.trim="form.performer" type="text" />
    </div>

    <div class="row">
      <label>Описание</label>
      <textarea v-model.trim="form.description" rows="4" />
    </div>

    <div class="row">
      <label>Файлы</label>
      <input type="file" multiple @change="onFiles" />
      <div class="files" v-if="form.files.length">
        <span v-for="(f,i) in form.files" :key="i" class="chip">{{ f.name }}</span>
      </div>
    </div>

    <div class="actions">
      <button type="submit" class="btn primary" :disabled="uploading">
        {{ uploading ? 'Сохранение…' : 'Сохранить' }}
      </button>
    </div>
  </form>
</template>

<style scoped>
.form{ display:flex; flex-direction:column; gap:12px; }
.grid{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px; }
.row,.col{ display:flex; flex-direction:column; gap:6px; }
label{ font-size:12px; opacity:.7; }
input,select,textarea{ border:1px solid #e5e7eb; border-radius:10px; padding:8px 10px; min-height:36px; }
textarea{ resize:vertical; }
.files{ display:flex; gap:6px; flex-wrap:wrap; margin-top:6px; }
.chip{ background:#eef2ff; border:1px solid #c7d2fe; color:#3730a3; border-radius:9999px; padding:4px 8px; font-size:12px; }
.actions{ display:flex; justify-content:flex-end; }
.btn{ padding:8px 14px; border-radius:10px; border:1px solid transparent; cursor:pointer; font-weight:700; }
.btn.primary{ background:#2563eb; color:#fff; }
</style>
