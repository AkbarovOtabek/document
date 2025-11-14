<script>
import axios from 'axios'
import { API_BASE_URL } from '@/API' // как в других компонентах

export default {
  name: 'AddLetterCertCBU',
  data() {
    return {
      // варианты "куда отправлено" с backend
      destOptions: [],
      loadingDestinations: false,

      form: {
        system: 'CERT-CBU',      // фиксировано

        // основные реквизиты
        number: '',              // номер письма
        date: '',                // дата выхода письма (ручной ввод)
        subject: '',             // титул / тема письма

        // ответственный
        performer: '',           // исполнитель письма

        description: '',         // описание / требуемые действия

        // срок письма
        has_deadline: false,     // есть ли срок письма (checkbox)
        deadline: '',            // если есть — дата срока

        // индикаторы / IOC
        indicators: '',          // IOC/ссылки/хэши
        // получатели (id категорий из /api/categories/list/)
        sent_to: [],             // куда отправлено (мульти-выбор, массив id)

        // файлы
        files: [],               // вложения

        // метаданные (кто добавил / кто изменил)
        created_by: '',          // кто добавил на сайт (заполнит backend)
        updated_by: '',          // кто изменил данные (заполнит backend)
      },
      uploading: false,
    }
  },
  async created() {
    await this.loadDestinations()
  },
  methods: {
    async loadDestinations() {
      this.loadingDestinations = true
      try {
        // /api/categories/list/
        const { data } = await axios.get(`${API_BASE_URL}api/categories/list/`)

        // поддержим и пагинацию, и простой список
        const items = Array.isArray(data?.results) ? data.results : data

        this.destOptions = (items || []).map(cat => ({
          value: cat.id,
          label: cat.name || cat.title || cat.slug || `Категория #${cat.id}`,
        }))
      } catch (e) {
        console.error('Ошибка загрузки категорий (куда отправлено)', e)
      } finally {
        this.loadingDestinations = false
      }
    },

    onFiles(e) {
      this.form.files = Array.from(e.target.files || [])
    },

    async submit() {
      this.uploading = true
      try {
        // здесь будет реальный запрос к backend cert_documents
        // const fd = new FormData()
        //
        // Object.entries(this.form).forEach(([k, v]) => {
        //   if (k === 'files') {
        //     v.forEach(f => fd.append('files', f))
        //   } else if (k === 'sent_to') {
        //     // sent_to — массив id категорий
        //     v.forEach(id => fd.append('sent_to', id))
        //   } else if (k === 'has_deadline') {
        //     fd.append('has_deadline', v ? 'true' : 'false')
        //   } else {
        //     fd.append(k, v ?? '')
        //   }
        // })
        //
        // await axios.post(`${API_BASE_URL}api/cert-documents/letters/`, fd, {
        //   headers: { 'Content-Type': 'multipart/form-data' },
        // })

        // пока демо:
        await new Promise(r => setTimeout(r, 700))
        alert('Письмо CERT-CBU добавлено (демо)')

        this.form = {
          system: 'CERT-CBU',
          number: '',
          date: '',
          subject: '',
          performer: '',
          description: '',
          has_deadline: false,
          deadline: '',
          indicators: '',
          sent_to: [],
          files: [],
          created_by: '',
          updated_by: '',
        }
      } finally {
        this.uploading = false
      }
    },
  },
}
</script>

<template>
  <form class="form" @submit.prevent="submit">
    <!-- Основные реквизиты -->
    <div class="grid">
      <div class="col">
        <label>Система</label>
        <input type="text" value="CERT-CBU" disabled />
      </div>
      <div class="col">
        <label>Номер письма</label>
        <input v-model.trim="form.number" type="text" required />
      </div>
      <div class="col">
        <label>Дата выхода письма</label>
        <input v-model="form.date" type="date" required />
      </div>
    </div>

    <div class="row">
      <label>Тема / титул</label>
      <input v-model.trim="form.subject" type="text" required />
    </div>

    <!-- Ответственный и затронутые -->
    <div class="grid">
      <div class="col">
        <label>Исполнитель (ответственный)</label>
        <input v-model.trim="form.performer" type="text" />
      </div>
      <div class="col deadline-col">
        <label class="deadline-label">
          <input
            type="checkbox"
            v-model="form.has_deadline"
          />
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

    <!-- Куда отправлено (категории с backend) -->
    <div class="row">
      <label>Куда отправлено (можно несколько)</label>
      <select
        v-model="form.sent_to"
        multiple
        :disabled="loadingDestinations || !destOptions.length"
      >
        <option
          v-for="opt in destOptions"
          :key="opt.value"
          :value="opt.value"
        >
          {{ opt.label }}
        </option>
      </select>
      <small class="hint">
        Выберите одну или несколько категорий получателей
        (категории загружаются из /api/categories/list/)
      </small>
    </div>

    <!-- Описание / действия -->
    <div class="row">
      <label>Описание / Требуемые действия</label>
      <textarea v-model.trim="form.description" rows="5" />
    </div>

    <!-- IOC -->
    <div class="row">
      <label>Индикаторы компрометации (IOC)</label>
      <textarea
        v-model.trim="form.indicators"
        rows="3"
        placeholder="URL, IP, домены, хэши…"
      />
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

    <!-- Метаданные (кто добавил / кто изменил) – только для отображения -->
    <div class="grid meta-grid">
      <div class="col">
        <label>Кто добавил (устанавливает система)</label>
        <input
          v-model="form.created_by"
          type="text"
          disabled
          placeholder="Определяется автоматически"
        />
      </div>
      <div class="col">
        <label>Кто изменил (устанавливает система)</label>
        <input
          v-model="form.updated_by"
          type="text"
          disabled
          placeholder="Определяется автоматически"
        />
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
.form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 10px;
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
label {
  font-size: 12px;
  opacity: 0.7;
}
input,
select,
textarea {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 8px 10px;
  min-height: 36px;
}
select[multiple] {
  min-height: 80px;
}
textarea {
  resize: vertical;
}
.files {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 6px;
}
.chip {
  background: #fff7ed;
  border: 1px solid #fdba74;
  color: #9a3412;
  border-radius: 9999px;
  padding: 4px 8px;
  font-size: 12px;
}
.actions {
  display: flex;
  justify-content: flex-end;
}
.btn {
  padding: 8px 14px;
  border-radius: 10px;
  border: 1px solid transparent;
  cursor: pointer;
  font-weight: 700;
}
.btn.primary {
  background: #2563eb;
  color: #fff;
}
.hint {
  font-size: 11px;
  opacity: 0.6;
}
.deadline-col input[type='date'] {
  margin-top: 4px;
}
.deadline-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  opacity: 0.8;
}
</style>
