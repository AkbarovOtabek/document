<template>
  <div v-if="letter" class="detail-wrapper">
    <!-- ОСНОВНАЯ КАРТОЧКА ПИСЬМА -->
    <div class="detail-card">
      <div class="detail-head">
        <h3>Письмо</h3>
        <button type="button" class="btn ghost small" @click="$emit('close')">
          ✕
        </button>
      </div>

      <div class="detail-body">
        <!-- КАТЕГОРИЯ / СИСТЕМА -->
        <div class="row">
          <span class="label">Категория / система</span>
          <span class="value">
            {{ letter.category?.name || letter.system || letter.category_name || '—' }}
          </span>
        </div>

        <!-- НОМЕР ПИСЬМА -->
        <div class="row">
          <span class="label">Номер письма</span>
          <span class="value">
            {{ letter.letter_number || letter.internal_letter_number || letter.number || '—' }}
          </span>
        </div>

        <!-- ТЕМА -->
        <div class="row">
          <span class="label">Тема / предмет</span>
          <span class="value">
            {{ letter.title || letter.subject || '—' }}
          </span>
        </div>

        <!-- ДАТА РЕГИСТРАЦИИ -->
        <div class="row">
          <span class="label">Дата регистрации</span>
          <span class="value">
            {{ formatDate(letter.registration_date || letter.date || letter.created_at) }}
          </span>
        </div>

        <!-- ДАТА ВХОДЯЩЕГО -->
        <div class="row">
          <span class="label">Дата входящего</span>
          <span class="value">
            {{ formatDate(letter.incoming_date || letter.date) }}
          </span>
        </div>

        <!-- ИСПОЛНИТЕЛЬ -->
        <div class="row" v-if="letter.executor || letter.performer || letter.performer_name">
          <span class="label">Исполнитель</span>
          <span class="value">
            {{ letter.performer_name || letter.executor_name || letter.executor || letter.performer }}
          </span>
        </div>

        <!-- ОПИСАНИЕ -->
        <div class="row" v-if="letter.description || letter.text || letter.body">
          <span class="label">Описание</span>
          <span class="value multiline">
            {{ letter.description || letter.text || letter.body }}
          </span>
        </div>

        <!-- ФАЙЛЫ -->
        <div class="row" v-if="letter.file || (letter.files && letter.files.length)">
          <span class="label">Файл(ы)</span>
          <span class="value">
            <!-- старый external-формат: один file -->
            <template v-if="letter.file">
              <a :href="letter.file" target="_blank" rel="noopener">
                Открыть файл
              </a>
            </template>

            <!-- CERT-CBU: массив files[] -->
            <template v-else>
              <div
                v-for="f in letter.files"
                :key="f.id || f.file"
                class="file-link"
              >
                <a :href="f.file" target="_blank" rel="noopener">
                  {{ f.original_name || getFileName(f.file) }}
                </a>
              </div>
            </template>
          </span>
        </div>

        <!-- СОЗДАНО -->
        <div class="row">
          <span class="label">Создано</span>
          <span class="value">
            {{ formatDateTime(letter.time_create || letter.created_at) }}
          </span>
        </div>

        <!-- ОБНОВЛЕНО -->
        <div class="row">
          <span class="label">Обновлено</span>
          <span class="value">
            {{ formatDateTime(letter.updated || letter.updated_at) }}
          </span>
        </div>
      </div>
    </div>

    <!-- КАРТОЧКА: КОМУ ОТПРАВЛЕНО -->
    <div
      v-if="groupedRecipients.length"
      class="recipients-card"
    >
      <div class="recipients-head">
        <h4>Кому отправлено</h4>
        <div class="deadline-info" v-if="letter.has_deadline && letter.deadline">
          Срок ответа: {{ formatDate(letter.deadline) }}
        </div>
      </div>

      <div class="recipients-body">
        <div
          v-for="group in groupedRecipients"
          :key="group.type"
          class="recipient-group"
        >
          <div class="org-type">
            {{ group.type }}
          </div>

          <div class="org-list">
            <div
              v-for="(org, idx) in group.orgs"
              :key="org.id || idx"
              class="org-chip"
              :class="statusClassForOrg(org)"
              @click="openOrgModal(org)"
            >
              <div class="org-name">
                {{ org.name || org.title || ('Организация #' + org.id) }}
              </div>

              <div class="org-status-text">
                {{ statusTextForOrg(org) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="legend">
        <span class="legend-item legend-green">В срок</span>
        <span class="legend-item legend-red">Ответ с опозданием</span>
        <span class="legend-item legend-yellow">Ожидается ответ (до срока)</span>
        <span class="legend-item legend-grey">Нет ответа</span>
      </div>
    </div>

    <!-- МОДАЛЬНОЕ ОКНО ПО ОРГАНИЗАЦИИ -->
    <div v-if="showOrgModal && selectedOrg" class="modal-backdrop">
      <div class="modal-window">
        <div class="modal-head">
          <h3>{{ selectedOrg.name || selectedOrg.title || ('Организация #' + selectedOrg.id) }}</h3>
          <button class="btn ghost small" @click="closeOrgModal">✕</button>
        </div>

        <div class="modal-body">
          <!-- 1. ИНФОРМАЦИЯ ОБ ОРГАНИЗАЦИИ -->
          <section class="modal-section">
            <div class="modal-section-title">Информация об организации</div>

            <div class="modal-row">
              <span class="modal-label">Тип</span>
              <span class="modal-value">
                {{
                  (selectedOrg.organization_type && selectedOrg.organization_type.name) ||
                  (selectedOrg.type && selectedOrg.type.name) ||
                  selectedOrg.type_name ||
                  (selectedOrg.category && selectedOrg.category.name) ||
                  selectedOrg.category_name ||
                  '—'
                }}
              </span>
            </div>

            <div class="modal-row" v-if="curatorName">
              <span class="modal-label">Куратор</span>
              <span class="modal-value">{{ curatorName }}</span>
            </div>

            <!-- UNITS TREE -->
            <div class="modal-row" v-if="normalizedUnitTree && normalizedUnitTree.length">
              <span class="modal-label">Структура подразделений</span>
              <div class="modal-value">
                <div class="unit-tree">
                  <UnitNode
                    v-for="node in normalizedUnitTree"
                    :key="node.id"
                    :node="node"
                    :level="0"
                  />
                </div>
              </div>
            </div>

            <div class="modal-row" v-if="selectedOrg.inn || selectedOrg.inn_number">
              <span class="modal-label">ИНН</span>
              <span class="modal-value">
                {{ selectedOrg.inn || selectedOrg.inn_number }}
              </span>
            </div>

            <div class="modal-row" v-if="selectedOrg.mfo || selectedOrg.mfo_code">
              <span class="modal-label">МФО</span>
              <span class="modal-value">
                {{ selectedOrg.mfo || selectedOrg.mfo_code }}
              </span>
            </div>
          </section>

          <!-- 2. ИНФОРМАЦИЯ ПО ПИСЬМУ ДЛЯ ЭТОЙ ОРГАНИЗАЦИИ -->
          <section class="modal-section">
            <div class="modal-section-title">Информация по текущему письму</div>

            <div class="modal-row">
              <span class="modal-label">Номер письма CERT-CBU</span>
              <span class="modal-value">
                {{ letter.number || letter.letter_number || '—' }}
              </span>
            </div>

            <div class="modal-row">
              <span class="modal-label">Дата письма</span>
              <span class="modal-value">
                {{ formatDate(letter.date || letter.registration_date || letter.created_at) }}
              </span>
            </div>

            <div class="modal-row">
              <span class="modal-label">Срок ответа</span>
              <span class="modal-value">
                <template v-if="letter.has_deadline && letter.deadline">
                  {{ formatDate(letter.deadline) }}
                </template>
                <template v-else>
                  Не установлен
                </template>
              </span>
            </div>

            <div class="modal-row">
              <span class="modal-label">Статус по письму</span>
              <span class="modal-value">
                {{ currentOrgStatusText }}
              </span>
            </div>

            <div class="modal-row" v-if="currentOrgReply && currentOrgReply.received_date">
              <span class="modal-label">Дата получения ответа</span>
              <span class="modal-value">
                {{ formatDate(currentOrgReply.received_date) }}
              </span>
            </div>
          </section>

          <!-- 3. СПИСОК ОТВЕТНЫХ ПИСЕМ -->
          <section class="modal-section">
            <div class="modal-section-title">Ответные письма организации</div>

            <div v-if="orgReplies && orgReplies.length">
              <div
                v-for="reply in orgReplies"
                :key="reply.id"
                class="reply-item"
              >
                <div class="reply-row">
                  <span class="reply-label">Номер ответа</span>
                  <span class="reply-value">{{ reply.reply_number || '—' }}</span>
                </div>

                <div class="reply-row">
                  <span class="reply-label">Внутренний номер</span>
                  <span class="reply-value">{{ reply.internal_number || '—' }}</span>
                </div>

                <div class="reply-row">
                  <span class="reply-label">Дата получения</span>
                  <span class="reply-value">{{ formatDate(reply.received_date) }}</span>
                </div>

                <div class="reply-row" v-if="reply.added_by_name || reply.added_at">
                  <span class="reply-label">Добавлено в систему</span>
                  <span class="reply-value">
                    <template v-if="reply.added_by_name">
                      {{ reply.added_by_name }},
                    </template>
                    <template v-if="reply.added_at">
                      {{ formatDateTime(reply.added_at) }}
                    </template>
                  </span>
                </div>

                <div class="reply-row" v-if="reply.file">
                  <span class="reply-label">Файл</span>
                  <span class="reply-value">
                    <a :href="reply.file" target="_blank" rel="noopener">
                      Открыть файл
                    </a>
                  </span>
                </div>
              </div>
            </div>
            <div v-else class="no-replies">
              Ответов от этой организации нет.
            </div>
          </section>
        </div>

        <div class="modal-footer">
          <button class="btn small" @click="closeOrgModal">Закрыть</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import UnitNode from '@/components/UnitNode.vue'
import axios from 'axios'
import { API_BASE_URL } from '@/API'

export default {
  name: 'SearchLetterDetailCertCBU',

  components: {
    UnitNode,
  },

  props: {
    letter: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      organizationsIndex: {}, // id -> объект организации
      loadingOrgs: false,

      showOrgModal: false,
      selectedOrg: null,
    }
  },

  computed: {
    /** Ответы по письму (ожидаем формат CertLetterReplySerializer или id-шники) */
    repliesRaw() {
      const l = this.letter
      if (!l || !l.replies) return []

      // если приходит массив id-шников, то тут можно будет отдельно подгружать;
      // сейчас считаем, что уже приходят объекты
      if (Array.isArray(l.replies)) {
        return l.replies
      }

      return []
    },

    /** replies сгруппированы по id организации */
    repliesByOrgId() {
      const map = {}
      this.repliesRaw.forEach((r) => {
        const orgId =
          r.organization ||
          r.organization_id ||
          (r.organization && r.organization.id)

        if (!orgId) return
        if (!map[orgId]) map[orgId] = []
        map[orgId].push(r)
      })
      return map
    },

    // исходный список адресатов (после подгрузки из API)
    recipients() {
      const l = this.letter
      if (!l) return []

      // backend уже отдал объекты организаций
      if (
        Array.isArray(l.dest_organizations) &&
        l.dest_organizations.length &&
        typeof l.dest_organizations[0] === 'object'
      ) {
        return l.dest_organizations
      }

      // массив id-шников
      if (Array.isArray(l.dest_organizations)) {
        return l.dest_organizations.map((id) => {
          return this.organizationsIndex[id] || { id }
        })
      }

      return []
    },

    // сгруппировано по типу организации
    groupedRecipients() {
      const groupsMap = {}

      this.recipients.forEach((org) => {
        const typeName =
          (org.organization_type && org.organization_type.name) ||
          (org.type && org.type.name) ||
          org.type_name ||
          (org.category && org.category.name) ||
          org.category_name ||
          'Организации'

        if (!groupsMap[typeName]) {
          groupsMap[typeName] = []
        }
        groupsMap[typeName].push(org)
      })

      return Object.keys(groupsMap).map((type) => ({
        type,
        orgs: groupsMap[type],
      }))
    },

    /** Ответы для выбранной организации */
    orgReplies() {
      if (!this.selectedOrg || !this.selectedOrg.id) return []
      return this.repliesByOrgId[this.selectedOrg.id] || []
    },

    /** Основной ответ для выбранной организации */
    currentOrgReply() {
      if (!this.selectedOrg) return null
      return this.getReplyForOrg(this.selectedOrg)
    },

    /** Статус по письму для выбранной организации (текст) */
    currentOrgStatusText() {
      if (!this.selectedOrg) return '—'
      return this.statusTextForOrg(this.selectedOrg)
    },

    /** Куратор организации (разные варианты полей) */
    curatorName() {
      const org = this.selectedOrg
      if (!org) return null

      const curator =
        org.curator ||
        org.manager ||
        org.responsible ||
        null

      const curatorNameField =
        org.curator_name ||
        org.manager_name ||
        org.responsible_name ||
        null

      if (curatorNameField) return curatorNameField

      if (curator) {
        return (
          curator.full_name ||
          curator.fio ||
          [curator.last_name, curator.first_name, curator.middle_name]
            .filter(Boolean)
            .join(' ') ||
          curator.username ||
          null
        )
      }

      return null
    },

    /** Приведённое к нормальному виду дерево подразделений для выбранной организации */
    normalizedUnitTree() {
      const org = this.selectedOrg
      if (!org) return []

      let raw =
        org.units_tree ||
        org.units_tree_display ||
        org.unit_path ||
        null

      if (!raw) return []

      // если пришла строка — пробуем распарсить как JSON
      if (typeof raw === 'string') {
        try {
          raw = JSON.parse(raw)
        } catch (e) {
          console.error('Ошибка парсинга units_tree', e, raw)
          return []
        }
      }

      // если пришёл один объект, оборачиваем в массив
      if (!Array.isArray(raw)) {
        raw = [raw]
      }

      const normalizeNode = (n) => ({
        id: n.id,
        name: n.name || n.title || `Подразделение #${n.id}`,
        type: n.type || n.unit_type || 'unit',
        parent_id: n.parent_id ?? null,
        children: Array.isArray(n.children)
          ? n.children.map(normalizeNode)
          : [],
      })

      return raw.map(normalizeNode)
    },
  },

  watch: {
    // как только письмо изменилось — подгружаем инфо по организациям
    letter: {
      immediate: true,
      handler(newVal) {
        if (!newVal) return
        this.loadOrganizationsForLetter(newVal)
      },
    },
  },

  methods: {
    async loadOrganizationsForLetter(letter) {
      const ids = Array.isArray(letter.dest_organizations)
        ? letter.dest_organizations
        : []

      if (!ids.length) return

      this.loadingOrgs = true
      try {
        const { data } = await axios.get(
          `${API_BASE_URL}api/organizations/list`
        )

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
      } catch (e) {
        console.error('Ошибка загрузки организаций для письма', e)
        this.organizationsIndex = {}
      } finally {
        this.loadingOrgs = false
      }
    },

    /** Найти "основной" ответ для конкретной организации (берём первый по дате) */
    getReplyForOrg(org) {
      const orgId = org.id
      if (!orgId) return null
      const list = this.repliesByOrgId[orgId]
      if (!list || !list.length) return null

      const sorted = [...list]
        .filter((r) => r.received_date)
        .sort(
          (a, b) => new Date(a.received_date) - new Date(b.received_date)
        )
      return sorted[0] || list[0]
    },

    /** Класс цвета для организации */
    statusClassForOrg(org) {
      const reply = this.getReplyForOrg(org)
      const hasDeadline = !!this.letter.has_deadline && !!this.letter.deadline

      if (!hasDeadline && !reply) {
        return 'org-grey'
      }

      const today = new Date()
      const deadlineDate = hasDeadline ? new Date(this.letter.deadline) : null

      if (reply && reply.received_date) {
        if (!hasDeadline) {
          return 'org-green'
        }
        const received = new Date(reply.received_date)

        if (received <= deadlineDate) {
          return 'org-green'
        } else {
          return 'org-red'
        }
      }

      if (hasDeadline && !reply) {
        if (today <= deadlineDate) {
          return 'org-yellow'
        } else {
          return 'org-grey'
        }
      }

      return 'org-grey'
    },

    /** Текстовый статус под названием организации */
    statusTextForOrg(org) {
      const reply = this.getReplyForOrg(org)
      const hasDeadline = !!this.letter.has_deadline && !!this.letter.deadline

      if (reply && reply.received_date) {
        if (!hasDeadline) {
          return `Ответ получен ${this.formatDate(reply.received_date)}`
        }
        const deadlineDate = new Date(this.letter.deadline)
        const received = new Date(reply.received_date)

        if (received <= deadlineDate) {
          return `Ответ в срок (${this.formatDate(reply.received_date)})`
        } else {
          return `Ответ с опозданием (${this.formatDate(reply.received_date)})`
        }
      }

      if (hasDeadline && !reply) {
        const today = new Date()
        const deadlineDate = new Date(this.letter.deadline)
        if (today <= deadlineDate) {
          return 'Ожидается ответ'
        } else {
          return 'Ответ не получен'
        }
      }

      return 'Ответ не получен'
    },

    openOrgModal(org) {
      this.selectedOrg = org
      this.showOrgModal = true
    },

    closeOrgModal() {
      this.showOrgModal = false
      this.selectedOrg = null
    },

    getFileName(url) {
      if (!url) return ''
      try {
        return url.split('/').pop()
      } catch {
        return url
      }
    },

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

/* основная карточка */
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

.file-link + .file-link {
  margin-top: 2px;
}

/* карточка "Кому отправлено" */
.recipients-card {
  border-radius: 7px;
  border: 1px solid #e5e7eb;
  background: #ffffff;
  padding: 12px 14px;
  box-sizing: border-box;
}

.recipients-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.recipients-head h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
}

.deadline-info {
  font-size: 12px;
  color: #4b5563;
}

.recipients-body {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* группы адресатов */
.recipient-group + .recipient-group {
  margin-top: 4px;
}

.org-type {
  font-weight: 600;
  font-size: 12px;
  margin-bottom: 4px;
}

.org-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

/* чипы организаций */
.org-chip {
  min-width: 140px;
  max-width: 220px;
  border-radius: 8px;
  padding: 6px 8px;
  font-size: 12px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
  cursor: pointer;
}

.org-chip:hover {
  box-shadow: 0 0 0 1px rgba(34, 197, 94, 0.2);
}

.org-name {
  font-weight: 600;
}

.org-status-text {
  font-size: 11px;
}

/* цвета статусов */
.org-green {
  background: #ecfdf3;
  border-color: #4ade80;
  color: #166534;
}

.org-red {
  background: #fef2f2;
  border-color: #fecaca;
  color: #b91c1c;
}

.org-yellow {
  background: #fffbeb;
  border-color: #facc15;
  color: #92400e;
}

.org-grey {
  background: #f3f4f6;
  border-color: #e5e7eb;
  color: #4b5563;
}

/* легенда */
.legend {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  font-size: 11px;
}

.legend-item {
  padding: 3px 8px;
  border-radius: 999px;
  border: 1px solid #e5e7eb;
}

.legend-green {
  background: #ecfdf3;
  border-color: #4ade80;
  color: #166534;
}
.legend-red {
  background: #fef2f2;
  border-color: #fecaca;
  color: #b91c1c;
}
.legend-yellow {
  background: #fffbeb;
  border-color: #facc15;
  color: #92400e;
}
.legend-grey {
  background: #f3f4f6;
  border-color: #e5e7eb;
  color: #4b5563;
}

/* модальное окно */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
}

.modal-window {
  width: 620px;
  max-width: 95vw;
  background: #ffffff;
  border-radius: 10px;
  padding: 14px 16px 12px;
  box-shadow: 0 20px 40px rgba(15, 23, 42, 0.25);
  box-sizing: border-box;
}

.modal-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.modal-head h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
}

.modal-body {
  max-height: 65vh;
  overflow-y: auto;
  padding-right: 4px;
}

.modal-section {
  margin-bottom: 10px;
}

.modal-section-title {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 4px;
  color: #111827;
}

.modal-row {
  display: grid;
  grid-template-columns: 160px 1fr;
  gap: 4px;
  font-size: 12px;
  margin-bottom: 3px;
}

.modal-label {
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-size: 11px;
}

.modal-value {
  color: #111827;
}

.unit-tree {
  margin-top: 2px;
}

.modal-footer {
  margin-top: 8px;
  display: flex;
  justify-content: flex-end;
}

.reply-item {
  padding: 8px 10px;
  border-radius: 6px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  font-size: 12px;
  margin-bottom: 6px;
}

.reply-row {
  display: grid;
  grid-template-columns: 160px 1fr;
  gap: 4px;
  margin-bottom: 2px;
}

.reply-label {
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-size: 11px;
}

.reply-value {
  color: #111827;
}

.no-replies {
  font-size: 13px;
  color: #6b7280;
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
