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
  <div class="wrap">
    <h3>Добавить письмо</h3>

    <div class="tabs">
      <button class="tab" :class="{active: tab==='other'}" @click="tab='other'">
        Добавить Другие письма
      </button>
      <button class="tab" :class="{active: tab==='cert'}" @click="tab='cert'">
        Добавить Письмо CERT-CBU
      </button>
    </div>

    <div class="panel">
      <AddLetterOther v-if="tab==='other'" />
      <AddLetterCertCBU v-else />
    </div>
  </div>
</template>

<style scoped>
.wrap{ display:flex; flex-direction:column; gap:12px; }
h3{ margin:0; }
.tabs{ display:flex; gap:8px; }
.tab{
  padding:8px 12px; border-radius:10px; border:1px solid #e5e7eb;
  background:#f7f8fb; cursor:pointer; font-weight:700;
}
.tab.active{ background:#111827; color:#fff; border-color:#111827; }
.panel{ background:#fff; border:1px solid #e5e7eb; border-radius:12px; padding:12px; }
</style>
