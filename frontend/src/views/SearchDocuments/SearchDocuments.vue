<script>
import SearchLetter from './SearchLetter.vue'
import AddLetter from './AddLetter.vue'

export default {
  name: 'SearchDocuments',
  components: { AddLetter, SearchLetter },
  data() {
    return {
      activeTab: 'search', // 'search' | 'add'
    }
  },
}
</script>

<template>
  <div class="docs-page">
    <div class="docs-inner">
      <!-- Верхняя шапка страницы -->
      <div class="docs-header">
        <div class="docs-header-left">
          <div class="docs-icon">
            <span class="icon-dot" />
          </div>
          <div>
            <div class="docs-title">Документы</div>
            <div class="docs-subtitle">
              Поиск и добавление входящих писем
            </div>
          </div>
        </div>

        <div class="docs-tabs">
          <button
            class="docs-tab"
            :class="{ active: activeTab === 'search' }"
            @click="activeTab = 'search'"
          >
            Искать письмо
          </button>

          <button
            class="docs-tab"
            :class="{ active: activeTab === 'add' }"
            @click="activeTab = 'add'"
          >
            Добавить письмо
          </button>
        </div>
      </div>

      <!-- Основной контент -->
      <div class="docs-body">
        <SearchLetter v-if="activeTab === 'search'" />
        <AddLetter v-else />
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Фон страницы */
.docs-page {
  width: 100%;
  min-height: 100vh;
  padding: 32px 24px;
  margin-top: 60px;
  box-sizing: border-box;
  background: #f4f6fb;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'SF Pro Text',
    'Segoe UI', sans-serif;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

/* Белая панель на всю ширину контента */
.docs-inner {
  width: 100%;
  background: #ffffff;
  border-radius: 7px;
  box-shadow:
    0 18px 40px rgba(15, 23, 42, 0.08),
    0 0 0 1px rgba(148, 163, 184, 0.1);
  padding: 20px 24px 24px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

/* Шапка */
.docs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}
.docs-header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}
.docs-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, #22c55e, #16a3ff);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 12px 24px rgba(34, 197, 94, 0.4);
}
.icon-dot {
  width: 18px;
  height: 18px;
  border-radius: 999px;
  background: #ffffff;
}
.docs-title {
  font-size: 20px;
  font-weight: 700;
  color: #020617;
}
.docs-subtitle {
  font-size: 12px;
  color: #6b7280;
}

/* Табы в шапке */
.docs-tabs {
  display: flex;
  gap: 8px;
}
.docs-tab {
  padding: 8px 16px;
  border-radius: 9px;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  color: #111827;
  transition: all 0.16s ease;
}
.docs-tab.active {
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: #ffffff;
  border-color: transparent;
  box-shadow: 0 12px 22px rgba(34, 197, 94, 0.35);
}

/* Контент */
.docs-body {
  width: 100%;
}
</style>
