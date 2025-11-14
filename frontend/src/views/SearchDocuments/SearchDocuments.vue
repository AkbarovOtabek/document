<script>
import SearchLetter from './SearchLetter.vue'
import AddLetter from './AddLetter.vue'

export default {
  name: 'SearchDocuments',
  components: { AddLetter, SearchLetter },
  data() {
    return {
      activeTab: 'search',   // 'search' или 'add'
    }
  },
}
</script>

<template>
  <div class="docs-page">

    <!-- Верхние кнопки -->
    <div class="topnav">
      <button
        class="tab"
        :class="{ active: activeTab === 'search' }"
        @click="activeTab = 'search'"
      >
        Искать письмо
      </button>

      <button
        class="tab"
        :class="{ active: activeTab === 'add' }"
        @click="activeTab = 'add'"
      >
        Добавить письмо
      </button>
    </div>

    <div class="panel">
      <!-- Поиск писем -->
      <SearchLetter v-if="activeTab === 'search'" />

      <!-- Добавить письмо -->
      <AddLetter v-else />
    </div>

  </div>
</template>

<style scoped>
.docs-page {
  margin-top: 100px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

/* Кнопки сверху */
.topnav {
  display: flex;
  gap: 10px;
}

.tab {
  padding: 10px 16px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  background: #f7f8fb;
  font-weight: 700;
  cursor: pointer;
  transition: 0.2s;
}

.tab.active {
  background: #2563eb;
  color: white;
  border-color: #2563eb;
}

.panel {
  background: white;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}
</style>
