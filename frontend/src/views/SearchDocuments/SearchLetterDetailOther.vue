<template>
  <div v-if="letter" class="detail-wrapper">
    <!-- КАРТОЧКА ВХОДЯЩЕГО ПИСЬМА -->
    <div class="detail-card">
      <div class="detail-head">
        <h3>Письмо (External)</h3>
        <button type="button" class="btn ghost small" @click="$emit('close')">
          ✕
        </button>
      </div>

      <div class="detail-body">
        <div class="row">
          <span class="label">Категория</span>
          <span class="value">
            {{ letter.category?.name || '—' }}
          </span>
        </div>

        <div class="row">
          <span class="label">Номер письма</span>
          <span class="value">
            {{ letter.letter_number || letter.internal_letter_number || '—' }}
          </span>
        </div>

        <div class="row">
          <span class="label">Тема</span>
          <span class="value">
            {{ letter.title || '—' }}
          </span>
        </div>

        <div class="row">
          <span class="label">Дата регистрации</span>
          <span class="value">
            {{ formatDate(letter.registration_date) }}
          </span>
        </div>

        <div class="row">
          <span class="label">Дата входящего</span>
          <span class="value">
            {{ formatDate(letter.incoming_date) }}
          </span>
        </div>

        <!-- Кому отправлено (если есть) -->
        <div class="row" v-if="recipients && recipients.length">
          <span class="label">Кому отправлено</span>
          <span class="value">
            <template v-for="(org, idx) in recipients" :key="idx">
              {{ org.name || org.title || org }}
              <span v-if="idx < recipients.length - 1">, </span>
            </template>
          </span>
        </div>

        <div class="row" v-if="letter.executor">
          <span class="label">Исполнитель</span>
          <span class="value">
            {{ letter.executor }}
          </span>
        </div>

        <div class="row" v-if="letter.description">
          <span class="label">Описание</span>
          <span class="value multiline">
            {{ letter.description }}
          </span>
        </div>

        <div class="row" v-if="letter.file">
          <span class="label">Файл</span>
          <span class="value">
            <a :href="letter.file" target="_blank" rel="noopener">
              Открыть файл
            </a>
          </span>
        </div>

        <div class="row">
          <span class="label">Создано</span>
          <span class="value">
            {{ formatDateTime(letter.time_create) }}
          </span>
        </div>

        <div class="row">
          <span class="label">Обновлено</span>
          <span class="value">
            {{ formatDateTime(letter.updated) }}
          </span>
        </div>
      </div>
    </div>

    <!-- КАРТОЧКА НАШИХ ОТВЕТНЫХ ПИСЕМ -->
    <div v-if="replies.length" class="reply-card">
      <div class="reply-head">
        <h4>Ответные письма нашей организации</h4>
      </div>

      <div class="reply-body">
        <div v-for="r in replies" :key="r.id" class="reply-item">
          <div class="reply-row">
            <span class="reply-label">Номер ответного письма</span>
            <span class="reply-value">
              {{ r.reply_number || '—' }}
            </span>
          </div>

          <div class="reply-row">
            <span class="reply-label">Внутренний номер</span>
            <span class="reply-value">
              {{ r.internal_number || '—' }}
            </span>
          </div>

          <div class="reply-row">
            <span class="reply-label">Дата отправки</span>
            <span class="reply-value">
              {{ formatDate(r.sent_date) }}
            </span>
          </div>

          <div class="reply-row" v-if="r.added_by_name || r.added_at">
            <span class="reply-label">Добавлено в систему</span>
            <span class="reply-value">
              <template v-if="r.added_by_name">
                Пользователь: {{ r.added_by_name }},
              </template>
              <template v-if="r.added_at">
                {{ formatDateTime(r.added_at) }}
              </template>
            </span>
          </div>

          <div class="reply-row" v-if="r.file">
            <span class="reply-label">Файл</span>
            <span class="reply-value">
              <a :href="r.file" target="_blank" rel="noopener">
                Открыть файл
              </a>
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SearchLetterDetailOther',
  props: {
    letter: {
      type: Object,
      required: true,
    },
  },

  computed: {
    // наши ответные письма (из ExternalLetterSerializer.replies)
    replies() {
      const l = this.letter
      if (!l || !Array.isArray(l.replies)) return []
      return l.replies
    },

    // универсальный сбор "кому отправлено"
    recipients() {
      const l = this.letter
      if (!l) return []

      if (Array.isArray(l.dest_organizations)) return l.dest_organizations
      if (Array.isArray(l.to_organizations)) return l.to_organizations
      if (Array.isArray(l.organizations)) return l.organizations

      if (l.to_organization) return [l.to_organization]
      if (l.organization) return [l.organization]

      if (Array.isArray(l.dest_org_ids)) return l.dest_org_ids

      return []
    },
  },

  methods: {
    formatDate(val) {
      if (!val) return '—'
      const d = new Date(val)
      if (Number.isNaN(d.getTime())) return val
      return d.toLocaleDateString('ru-RU')
    },
    formatDateTime(val) {
      if (!val) return '—'
      const d = new Date(val)
      if (Number.isNaN(d.getTime())) return val
      return d.toLocaleString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    },
  },
}
</script>

<style scoped>
.detail-wrapper {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* карточка входящего письма */
.detail-card {
  border-radius: 7px;
  border: 1px solid #e5e7eb;
  background: #ffffff;
  padding: 14px 16px;
  box-sizing: border-box;
}

.detail-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.detail-head h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
}

.detail-body {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.row {
  display: grid;
  grid-template-columns: 160px 1fr;
  gap: 6px;
  align-items: flex-start;
}

.label {
  font-size: 11px;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.value {
  font-size: 13px;
  color: #111827;
}

.multiline {
  white-space: pre-wrap;
}

/* карточка ответных писем */
.reply-card {
  border-radius: 7px;
  border: 1px solid #e5e7eb;
  background: #ffffff;
  padding: 12px 14px;
  box-sizing: border-box;
}

.reply-head {
  margin-bottom: 6px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.reply-head h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
}

.reply-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.reply-item {
  padding: 8px 10px;
  border-radius: 6px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
}

.reply-row {
  display: grid;
  grid-template-columns: 170px 1fr;
  gap: 4px;
  font-size: 12px;
}

.reply-label {
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.reply-value {
  color: #111827;
}

/* кнопки */
.btn {
  padding: 4px 10px;
  border-radius: 999px;
  border: 1px solid #e5e7eb;
  background: #ffffff;
  cursor: pointer;
  font-size: 12px;
}
.btn.ghost {
  background: #ffffff;
  color: #111827;
  border-color: #e5e7eb;
}
.btn.small {
  padding: 4px 10px;
  font-size: 12px;
}
</style>
