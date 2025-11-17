<script>
import AddLetterOther from './AddLetterOther.vue'
import AddLetterCertCBU from './AddLetterCertCBU.vue'

export default {
  name: 'AddLetter',
  components: { AddLetterOther, AddLetterCertCBU },
  data() {
    return { tab: 'other' } // 'other' | 'cert'
  },
}
</script>

<template>
  <div class="add-card">
    <div class="add-header">
      <div>
        <div class="add-title">Добавить письмо</div>
        <div class="add-subtitle">
          Зарегистрируйте обычное письмо или письмо CERT-CBU
        </div>
      </div>

      <div class="add-tabs">
        <button
          class="add-tab"
          :class="{ active: tab === 'other' }"
          @click="tab = 'other'"
        >
          Другие письма
        </button>
        <button
          class="add-tab"
          :class="{ active: tab === 'cert' }"
          @click="tab = 'cert'"
        >
          Письмо CERT-CBU
        </button>
      </div>
    </div>

    <div class="add-body">
      <AddLetterOther v-if="tab === 'other'" />
      <AddLetterCertCBU v-else />
    </div>
  </div>
</template>

<style scoped>
.add-card {
  width: 100%;
  border-radius: 7px;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
  padding: 16px 16px 18px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.add-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.add-title {
  font-size: 18px;
  font-weight: 700;
  color: #111827;
}

.add-subtitle {
  font-size: 12px;
  color: #6b7280;
}

/* табы */
.add-tabs {
  display: flex;
  gap: 8px;
}
.add-tab {
  padding: 7px 14px;
  border-radius: 9px;
  border: 1px solid #e5e7eb;
  background: #ffffff;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  color: #111827;
  transition: all 0.16s ease;
}
.add-tab.active {
  background: #111827;
  color: #ffffff;
  border-color: #111827;
}

/* тело */
.add-body {
  margin-top: 4px;
}
</style>
