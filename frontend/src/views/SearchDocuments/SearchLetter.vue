<template>
  <div class="search-wrapper">
    <!-- Tabs -->
    <div class="tabs">
      <button
        v-for="cat in categories"
        :key="cat.value"
        type="button"
        class="tab"
        :class="{ active: activeMode === 'external' && activeCategoryId === cat.value }"
        @click="setExternalCategory(cat.value)"
      >
        {{ cat.label }}
      </button>

      <button
        type="button"
        class="tab"
        :class="{ active: activeMode === 'cert' }"
        @click="setTabCert"
      >
        Письма CERT-CBU
      </button>
    </div>

    <!-- Детальный просмотр External -->
    <SearchLetterDetailOther
      v-if="activeMode === 'external' && showDetail && selectedLetter"
      :letter="selectedLetter"
      @close="closeDetail"
    />

    <!-- Детальный просмотр CERT-CBU -->
    <SearchLetterDetailCertCBU
      v-if="activeMode === 'cert' && showDetail && selectedLetter"
      :letter="selectedLetter"
      @close="closeDetail"
    />

    <!-- Списки (когда детальный просмотр скрыт) -->
    <div v-if="!showDetail" class="tab-body">
      <SearchLetterOther
        v-if="activeMode === 'external'"
        :category-id="activeCategoryId"
        @open-detail="openDetail"
      />

      <SearchLetterCertCBU
        v-if="activeMode === 'cert'"
        @open-detail="openDetail"
      />
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { API_BASE_URL } from '@/API'

import SearchLetterOther from './SearchLetterOther.vue'
import SearchLetterCertCBU from './SearchLetterCertCBU.vue'
import SearchLetterDetailOther from './SearchLetterDetailOther.vue'
import SearchLetterDetailCertCBU from './SearchLetterDetailCertCBU.vue'

export default {
  name: 'SearchLetter',

  components: {
    SearchLetterOther,
    SearchLetterCertCBU,
    SearchLetterDetailOther,
    SearchLetterDetailCertCBU,
  },

  data() {
    return {
      activeMode: 'external',      // 'external' | 'cert'
      activeCategoryId: null,
      categories: [],

      selectedLetter: null,        // объект письма (и external, и cert)
      showDetail: false,

      loadingCategories: false,
    }
  },

  computed: {
    activeCategoryLabel() {
      const f = this.categories.find(c => c.value === this.activeCategoryId)
      return f ? f.label : ''
    },
  },

  async created() {
    await this.loadCategories()
  },

  methods: {
    async loadCategories() {
      this.loadingCategories = true
      try {
        const { data } = await axios.get(
          `${API_BASE_URL}api/external-letters/categories/`
        )
        const items = Array.isArray(data?.results) ? data.results : data

        this.categories = (items || []).map(cat => ({
          value: cat.id,
          label: cat.name || cat.title || cat.slug || `Категория #${cat.id}`,
        }))

        if (this.categories.length && !this.activeCategoryId) {
          this.activeCategoryId = this.categories[0].value
        }
      } catch (e) {
        console.error('Ошибка загрузки категорий', e)
      } finally {
        this.loadingCategories = false
      }
    },

    // Приходит объект letter (и от external, и от cert)
    openDetail(letter) {
      this.selectedLetter = letter
      this.showDetail = true
    },

    closeDetail() {
      this.selectedLetter = null
      this.showDetail = false
    },

    setExternalCategory(id) {
      this.activeMode = 'external'
      this.activeCategoryId = id
      this.showDetail = false
      this.selectedLetter = null
    },

    setTabCert() {
      this.activeMode = 'cert'
      this.showDetail = false
      this.selectedLetter = null
    },
  },
}
</script>

<style scoped>
.search-wrapper {
  width: 100%;
  border-radius: 7px;
  border: 1px solid #e5e7eb;
  background: #ffffff;
  padding: 10px;
  box-sizing: border-box;
}

.tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 10px;
}

.tab {
  padding: 7px 14px;
  border-radius: 999px;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
  cursor: pointer;
  font-size: 13px;
}

.tab.active {
  background: #111;
  color: #fff;
  border-color: #111;
}

.tab-body {
  margin-top: 10px;
}
</style>
