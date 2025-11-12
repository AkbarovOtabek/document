<script>
import SearchNQQ from './SearchNQQ.vue'
import SearchMBQ from './SearchMBQ.vue'
import SearchCERTCBU from './SearchCERTCBU.vue'
import AddLetter from './AddLetter.vue'

export default {
  name: 'SearchDocuments',
  components: { SearchNQQ, SearchMBQ, SearchCERTCBU, AddLetter },
  data() {
    return {
      activeMain: 'search',    
      activeSearchTab: 'NQQ',   
    }
  },
}
</script>

<template>
  <div class="search-docs">
    <!-- Верхняя навигация -->
    <div class="topnav">
      <button
        class="tab"
        :class="{ active: activeMain==='search' }"
        @click="activeMain='search'"
      >Искать письмо</button>

      <button
        class="tab"
        :class="{ active: activeMain==='add' }"
        @click="activeMain='add'"
      >Добавить письмо</button>
    </div>

    <!-- Содержимое -->
    <div v-if="activeMain==='search'" class="panel">
      <!-- Поднавигация: NQQ / MBQ / CERT-CBU -->
      <div class="subnav">
        <button
          class="subtab"
          :class="{ active: activeSearchTab==='NQQ' }"
          @click="activeSearchTab='NQQ'"
        >NQQ</button>
        <button
          class="subtab"
          :class="{ active: activeSearchTab==='MBQ' }"
          @click="activeSearchTab='MBQ'"
        >MBQ</button>
        <button
          class="subtab"
          :class="{ active: activeSearchTab==='CERT-CBU' }"
          @click="activeSearchTab='CERT-CBU'"
        >CERT-CBU</button>
      </div>

      <div class="content">
        <SearchNQQ v-if="activeSearchTab==='NQQ'" />
        <SearchMBQ v-else-if="activeSearchTab==='MBQ'" />
        <SearchCERTCBU v-else />
      </div>
    </div>

    <div v-else class="panel">
      <AddLetter />
    </div>
  </div>
</template>

<style scoped>
.search-docs{margin-top: 100px; display:flex; flex-direction:column; gap:14px; }
.topnav{ display:flex; gap:8px; }
.tab{
  padding:10px 14px; border-radius:12px; border:1px solid #e5e7eb;
  background:#f7f8fb; font-weight:700; cursor:pointer;
}
.tab.active{ background:#2563eb; color:#fff; border-color:#2563eb; }

.panel{ background:#fff; border:1px solid #e5e7eb; border-radius:12px; padding:12px; }
.subnav{ display:flex; gap:8px; margin-bottom:12px; }
.subtab{
  padding:8px 12px; border-radius:10px; border:1px solid #e5e7eb; background:#f3f4f6; cursor:pointer;
}
.subtab.active{ background:#111827; color:#fff; border-color:#111827; }

.content{ padding:4px; }
</style>
