<script>
import axios from "axios";
import { API_BASE_URL } from "@/API.js";
import OrgChartFlat from "./OrgChartFlat.vue";

const ORG_DETAIL_URL = `${API_BASE_URL}api/organizations/`;

export default {
  name: "OrganizationDetail",
  components: { OrgChartFlat },
  props: {
    slug: { type: String, required: true },
    isDark: { type: Boolean, default: false },
  },
  data() {
    return { loading: false, error: "", org: null };
  },
  computed: {
    themeClass() {
      return this.isDark ? "dark" : "";
    },
    avatarText() {
      if (!this.org || this.org.logo) return "";
      const initials = (this.org.name || "")
        .split(/\s+/)
        .map((w) => w[0])
        .join("")
        .slice(0, 2)
        .toUpperCase();
      return initials || "🏦";
    },
  },
  async mounted() {
    await this.fetchDetail();
  },
  watch: {
    slug: {
      async handler() {
        await this.fetchDetail();
      },
    },
  },
  methods: {
    async fetchDetail() {
      try {
        this.loading = true;
        this.error = "";
        const { data } = await axios.get(`${ORG_DETAIL_URL}${this.slug}/`);

        // 🔧 Нормализуем возможные варианты поля со структурой:
        const rawTree =
          data.units_tree ?? data.units ?? data.unitsTree ?? data.tree ?? data.structure ?? [];

        // превращаем в массив (если бек вернул один объект)
        const asArray = Array.isArray(rawTree) ? rawTree : rawTree ? [rawTree] : [];

        // записываем обратно, не меняя остальную разметку/стили
        this.org = { ...data, units_tree: asArray };
      } catch (e) {
        console.error(e);
        this.error = "Не удалось загрузить организацию";
      } finally {
        this.loading = false;
      }
    },
    goBack() {
      this.$router.back();
    },
    tel(h) {
      return h ? `tel:${String(h).replace(/\s+/g, "")}` : "#";
    },
    mail(m) {
      return m ? `mailto:${m}` : "#";
    },
    mapLink(addr) {
      return addr ? `https://maps.google.com/?q=${encodeURIComponent(addr)}` : "#";
    },
    abs(url) {
      if (!url) return "";
      if (/^https?:\/\//i.test(url)) return url;
      return `${API_BASE_URL.replace(/\/$/, "")}${url.startsWith("/") ? "" : "/"}${url}`;
    },
  },
};
</script>

<template>
  <div class="scene" :class="themeClass">
    <header class="hero">
      <div class="hero-left">
        <button class="btn ghost" @click="goBack">← Назад</button>
        <h1 class="title">{{ org?.name || "Организация" }}</h1>
        <div class="subtitle">
          <span class="pill">{{ org?.category_name || org?.category_slug || "Категория" }}</span>
          <span class="muted">·</span>
          <span class="muted"
            ><code>{{ org?.slug || slug }}</code></span
          >
        </div>
      </div>
    </header>

    <p v-if="error" class="error">{{ error }}</p>

    <section v-if="org" class="grid">
      <!-- Профиль -->
      <article class="card profile">
        <div class="card-inner">
          <div class="row head">
            <div class="avatar">
              <img v-if="org.logo" :src="abs(org.logo)" alt="" />
              <span v-else>{{ avatarText }}</span>
            </div>
            <div class="info">
              <div class="name">{{ org.name }}</div>
              <div class="tags">
                <span class="tag">{{ org.category_name || org.category_slug }}</span>
                <span class="tag ghost">ID: {{ org.id }}</span>
                <span class="tag ghost">Категория ID: {{ org.category }}</span>
              </div>
            </div>
          </div>

          <p v-if="org.description" class="desc">{{ org.description }}</p>

          <div class="details">
            <div>
              <strong>Адрес</strong>
              <a :href="mapLink(org.address)" target="_blank" class="muted link">{{
                org.address || "—"
              }}</a>
            </div>
            <div>
              <strong>Lotus</strong>
              <span class="muted">{{ org.lotus || "—" }}</span>
            </div>
            <div>
              <strong>Телефон</strong>
              <a :href="tel(org.phone)" class="muted link">{{ org.phone || "—" }}</a>
            </div>
            <div>
              <strong>Email</strong>
              <a :href="mail(org.email)" class="muted link">{{ org.email || "—" }}</a>
            </div>
            <div>
              <strong>Slug</strong>
              <code>{{ org.slug }}</code>
            </div>
            <div>
              <strong>Создано</strong>
              <span class="muted">{{ org.time_create }}</span>
            </div>
            <div>
              <strong>Обновлено</strong>
              <span class="muted">{{ org.updated }}</span>
            </div>
          </div>
        </div>
      </article>

      <!-- Ответственные -->
      <article class="card responsibles" v-if="org.responsibles && org.responsibles.length">
        <div class="card-inner">
          <h3 class="block-title">Ответственные</h3>
          <ul class="resp-list">
            <li v-for="(r, i) in org.responsibles" :key="i" class="resp-item">
              <div class="resp-avatar small">{{ (r.fio || r.username || "👤")[0] }}</div>
              <div class="resp-info">
                <div class="resp-name">{{ r.fio || r.username }}</div>
                <div class="resp-sub">
                  <span class="pill small">{{ r.role }}</span>
                  <span class="dot">•</span>
                  <span class="muted">Источник: {{ r.source }}</span>
                  <span class="dot">•</span>
                  <span class="muted">{{
                    r.can_edit ? "может редактировать" : "только чтение"
                  }}</span>
                </div>
                <div class="resp-contacts">
                  <span class="muted" v-if="r.phone">☎ {{ r.phone }}</span>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </article>

      <!-- Оргструктура -->
      <article class="card-width span-full">
        <div class="card-inner">
          <div class="structure-head">
            <h3 class="block-title">Оргструктура</h3>
            <div class="muted">
              {{ (org.units_tree && org.units_tree.length) || 0 }} корневых подразделения
            </div>
          </div>
          <div v-if="org.units_tree && org.units_tree.length" class="units-tree">
            <OrgChartFlat v-if="org?.units_tree?.length" :tree="org.units_tree" />
          </div>
          <p v-else class="muted">Структура не задана.</p>
        </div>
      </article>
    </section>

    <!-- Скелет -->
    <section v-else-if="loading" class="grid">
      <article class="card profile"><div class="card-inner skeleton"></div></article>
      <article class="card responsibles"><div class="card-inner skeleton"></div></article>
      <article class="card"><div class="card-inner skeleton"></div></article>
    </section>
  </div>
</template>

<style scoped>
/* — темы, профиль, карточки, списки ответственых —
   оставлены без изменений; стили самого узла вынесены в UnitNode.vue */

.scene {
  --bg: #f6f7fb;
  --panel: #fff;
  --ink: #0f141a;
  --muted: #6b7280;
  --primary: #19c46d;
  --primary-ink: #0ea95b;
  --line: #e6e8ee;
  --ring: rgba(25, 196, 109, 0.24);
  min-height: calc(100vh - 64px);
  background: radial-gradient(1200px 600px at 70% -100px, rgba(25, 196, 109, 0.1), transparent 60%),
    var(--bg);
  color: var(--ink);
}
.scene.dark {
  --bg: #0f1118;
  --panel: #151b22;
  --ink: #eaf0f6;
  --muted: #94a3b8;
  --primary: #2bdf83;
  --primary-ink: #17b469;
  --line: #222a36;
  --ring: rgba(43, 223, 131, 0.18);
  background: radial-gradient(1300px 700px at 70% -120px, rgba(43, 223, 131, 0.1), transparent 60%),
    var(--bg);
}

.hero {
  display: grid;
  min-height: 300px;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 18px;
  align-items: center;
  padding: 20px 22px 6px;
}
@media (max-width: 980px) {
  .hero {
    grid-template-columns: 1fr;
  }
}
.title {
  margin: 8px 0 4px;
  font-size: 32px;
  line-height: 1.1;
}
.subtitle {
  display: flex;
  align-items: center;
  gap: 10px;
}
.pill {
  display: inline-flex;
  align-items: center;
  height: 24px;
  padding: 0 10px;
  border-radius: 999px;
  background: rgba(25, 196, 109, 0.15);
  color: var(--primary);
  border: 1px solid rgba(25, 196, 109, 0.25);
  font-weight: 800;
  font-size: 12px;
}
.pill.small {
  height: 20px;
  font-size: 11px;
}
.muted {
  color: var(--muted);
}
.btn {
  margin-bottom: 20px;
  height: 38px;
  padding: 0 12px;
  border-radius: 12px;
  border: 1px solid var(--line);
  background: transparent;
  color: var(--ink);
  font-weight: 800;
  cursor: pointer;
}

.grid {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 18px;
  padding: 10px 22px 24px;
}
@media (max-width: 980px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
.card {
  perspective: 900px;
}
.card-width {
  perspective: 1200px;
  width: 100%;
}
.card-width .card-inner {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0)),
    var(--panel);
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 16px;
  transform-style: preserve-3d;
  transition: transform 0.22s ease, box-shadow 0.22s ease;
  box-shadow: 0 18px 38px rgba(0, 0, 0, 0.12);
}
.card .card-inner {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0)),
    var(--panel);
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 16px;
  transform-style: preserve-3d;
  transition: transform 0.22s ease, box-shadow 0.22s ease;
  box-shadow: 0 18px 38px rgba(0, 0, 0, 0.12);
}

.row.head {
  display: flex;
  gap: 14px;
  align-items: center;
  margin-bottom: 8px;
}
.avatar {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  border: 1px solid var(--line);
  display: grid;
  place-items: center;
  background: linear-gradient(180deg, rgba(25, 196, 109, 0.18), rgba(25, 196, 109, 0.08));
  font-weight: 900;
  font-size: 20px;
  color: #fff;
  text-shadow: 0 1px 12px rgba(0, 0, 0, 0.25);
}
.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 16px;
}
.info .name {
  font-size: 20px;
  font-weight: 900;
  margin-bottom: 4px;
}
.tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.tag {
  display: inline-flex;
  align-items: center;
  height: 24px;
  padding: 0 10px;
  border-radius: 999px;
  background: rgba(25, 196, 109, 0.15);
  color: var(--primary);
  border: 1px solid rgba(25, 196, 109, 0.25);
  font-weight: 800;
  font-size: 12px;
}
.tag.ghost {
  background: transparent;
  color: var(--muted);
  border-color: var(--line);
}
.desc {
  margin: 50px 0 10px;
  color: var(--muted);
}
.details {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: 8px;
}
.details .link {
  text-decoration: none;
}
.details strong {
  display: block;
  font-size: 12px;
  color: var(--muted);
}
.details span,
.details a {
  font-size: 14px;
}

.block-title {
  margin: 0 0 10px;
}
.resp-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 10px;
}
.resp-item {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 10px;
  align-items: flex-start;
}
.resp-avatar {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  background: rgba(25, 196, 109, 0.18);
  color: #fff;
  font-weight: 900;
  border: 1px solid var(--line);
  font-size: 12px;
}
.resp-info {
  display: grid;
  gap: 4px;
}
.resp-name {
  font-weight: 800;
}
.resp-sub {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
}
.dot {
  color: var(--muted);
}
.resp-contacts {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.link {
  color: var(--ink);
}

.structure-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}
.units-tree {
  display: grid;
  gap: 8px;
}

.skeleton {
  min-height: 180px;
  background: linear-gradient(90deg, rgba(0, 0, 0, 0.06), rgba(0, 0, 0, 0.02), rgba(0, 0, 0, 0.06));
  background-size: 200% 100%;
  animation: shimmer 1.2s infinite;
}
@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
.span-full {
  grid-column: 1 / -1;
  margin-bottom: 70px;
}

.error {
  color: #ef4444;
  margin: 8px 22px;
}
</style>
