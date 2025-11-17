<script>
import axios from "axios";
import { API_BASE_URL } from "@/API.js";

const ME_URL = `${API_BASE_URL}api/staff/users/me/`;

export default {
  name: "Account",
  props: { isDark: { type: Boolean, default: false } },
  data() {
    return {
      loading: false,
      error: "",
      me: null,
    };
  },
  computed: {
    themeClass() {
      return this.isDark ? "dark" : "";
    },
    fullName() {
      return this.me?.fio || "";
    },
    roleName() {
      const map = {
        admin: "Администратор",
        manager: "Менеджер",
        curator: "Куратор",
        viewer: "Читатель",
      };
      return map[this.me?.role] || this.me?.role || "—";
    },
    positionName() {
      const map = {
        director: "Директор",
        deputy_director: "Зам. директора",
        head_of_management: "Начальник управления",
        head_of_department: "Начальник отдела",
        chief_expert: "Главный эксперт",
        leading_expert: "Ведущий эксперт",
        expert_1: "Эксперт I уровня",
        clerk: "Делопроизводитель",
        employee: "Сотрудник",
      };
      return map[this.me?.position] || this.me?.position || "—";
    },
  },
  mounted() {
    this.fetchMe();
  },
  methods: {
    async fetchMe() {
      try {
        this.loading = true;
        this.error = "";
        const token = localStorage.getItem("access");
        const { data } = await axios.get(ME_URL, {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        });
        this.me = data;
      } catch (e) {
        console.error(e);
        this.error = "Не удалось загрузить данные профиля";
      } finally {
        this.loading = false;
      }
    },
    tel(v) {
      return v ? `tel:${String(v).replace(/\s+/g, "")}` : "#";
    },
    mail(v) {
      return v ? `mailto:${v}` : "#";
    },
  },
};
</script>

<template>
  <div class="scene" :class="themeClass">
    <div class="page">

      <header class="toolbar">
        <div class="title-block">
          <div class="title-dot"></div>
          <div>
            <h1>Аккаунт</h1>
            <p class="subtitle">Ваш профиль и закреплённые организации</p>
          </div>
        </div>
      </header>

      <p v-if="error" class="error">{{ error }}</p>

      <section v-if="me" class="grid">
        <!-- Профиль -->
        <article class="card profile">
          <div class="card-inner">
            <div class="top">
              <div class="avatar">
                <span>{{ (me.first_name?.[0] || "") + (me.last_name?.[0] || "") }}</span>
              </div>
              <div class="info">
                <h2 class="name">{{ fullName }}</h2>
                <div class="badges">
                  <span class="pill">{{ roleName }}</span>
                  <span v-if="me.management_flag" class="pill ghost">Руководство</span>
                </div>
                <div class="meta muted">
                  <span><strong>Должность:</strong> {{ positionName }}</span>
                </div>
              </div>
            </div>

            <div v-if="me.management" class="meta muted mt8">
              <span><strong>Управление:</strong> {{ me.management.name }}</span>
            </div>
            <div v-if="me.department" class="meta muted mt4">
              <span><strong>Отдел:</strong> {{ me.department.name }}</span>
            </div>

            <div class="grid2">
              <div>
                <strong>Username</strong>
                <div class="muted">{{ me.username }}</div>
              </div>
              <div>
                <strong>Lotus</strong>
                <div class="muted">{{ me.lotus || "—" }}</div>
              </div>
              <div>
                <strong>Email (личный)</strong>
                <a class="muted link" :href="mail(me.email)">{{ me.email || "—" }}</a>
              </div>
              <div>
                <strong>Email (рабочий)</strong>
                <a class="muted link" :href="mail(me.work_email)">{{ me.work_email || "—" }}</a>
              </div>
              <div>
                <strong>Телефон (рабочий)</strong>
                <a class="muted link" :href="tel(me.phone)">{{ me.phone || "—" }}</a>
              </div>
              <div>
                <strong>Телефон (личный)</strong>
                <a class="muted link" :href="tel(me.work_phone)">{{ me.work_phone || "—" }}</a>
              </div>
            </div>
          </div>
        </article>

        <!-- Кураторства -->
        <article class="card curated">
          <div class="card-inner">
            <div class="head-row">
              <h3>Куратор организаций</h3>
              <span class="chip">{{ me.curated_orgs_count }} шт.</span>
            </div>

            <div v-if="me.links?.length" class="orgs">
              <router-link
                v-for="lnk in me.links"
                :key="lnk.id"
                :to="`/category/organizations/${lnk.organization_data?.slug}/detail/`"
                class="org"
              >
                <img
                  v-if="lnk.organization_data?.logo"
                  :src="lnk.organization_data.logo"
                  class="logo"
                  alt=""
                />
                <div v-else class="logo placeholder">
                  {{ (lnk.organization_data?.name || "—").slice(0, 1).toUpperCase() }}
                </div>
                <div class="o-texts">
                  <div class="o-name">{{ lnk.organization_data?.name || "—" }}</div>
                  <div class="o-meta muted">
                    <span>{{
                      lnk.organization_data?.category_name ||
                      lnk.organization_data?.category_slug
                    }}</span>
                    <span v-if="lnk.can_edit" class="pill tiny">может редактировать</span>
                  </div>
                </div>
              </router-link>
            </div>

            <div v-else class="empty muted">Пока нет закреплённых организаций.</div>
          </div>
        </article>
      </section>

      <section v-else-if="loading" class="grid">
        <article class="card"><div class="card-inner skeleton"></div></article>
        <article class="card"><div class="card-inner skeleton"></div></article>
      </section>

    </div>
  </div>
</template>

<style scoped>
/* ===== PAGE BACKGROUND (как в новом дашборде) ===== */
.scene {
  margin-top: 50px;
  min-height: 100vh;
  width: 100%;
  background: #f4f6fb;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text",
    "Segoe UI", sans-serif;
  color: #0f172a;
}

.scene.dark {
  background: #020617;
  color: #e5e7eb;
}

/* контейнер по центру */
.page {
  width: 100%;
  max-width: 1200px;
  padding: 32px 24px 28px;
  box-sizing: border-box;
}

/* ===== TOOLBAR ===== */
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.title-block {
  display: flex;
  align-items: center;
  gap: 10px;
}

.title-dot {
  width: 34px;
  height: 34px;
  border-radius: 12px;
  background: #ecfdf3;
  border: 1px solid #bbf7d0;
  box-shadow: 0 8px 18px rgba(34, 197, 94, 0.35);
}

h1 {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
}

.subtitle {
  margin: 2px 0 0;
  font-size: 12px;
  color: #9ca3af;
}

/* ===== GRID ===== */
.grid {
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  gap: 18px;
}

@media (max-width: 980px) {
  .grid {
    grid-template-columns: 1fr;
  }
}

/* ===== CARDS ===== */
.card-inner {
  background: #ffffff;
  border-radius: 22px;
  padding: 18px 18px 16px;
  border: 1px solid #e5e7eb;
  box-shadow:
    0 18px 40px rgba(15, 23, 42, 0.06),
    0 0 0 1px rgba(148, 163, 184, 0.04);
}

/* профиль */
.profile .top {
  display: flex;
  gap: 14px;
  align-items: center;
}

.avatar {
  width: 72px;
  height: 72px;
  border-radius: 22px;
  display: grid;
  place-items: center;
  color: #fff;
  font-weight: 800;
  font-size: 22px;
  background: linear-gradient(135deg, #22c55e, #16a34a);
  box-shadow: 0 18px 40px rgba(34, 197, 94, 0.35);
}

.info .name {
  margin: 0;
  font-size: 22px;
}

.badges {
  display: flex;
  gap: 8px;
  margin-top: 6px;
  flex-wrap: wrap;
}

.pill {
  display: inline-flex;
  align-items: center;
  height: 24px;
  padding: 0 10px;
  border-radius: 999px;
  background: #ecfdf3;
  color: #166534;
  border: 1px solid #bbf7d0;
  font-weight: 600;
  font-size: 12px;
}

.pill.ghost {
  background: #f9fafb;
  color: #6b7280;
  border-color: #e5e7eb;
}

.pill.tiny {
  height: 20px;
  font-size: 11px;
  padding: 0 8px;
  margin-left: 6px;
}

.meta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.mt8 { margin-top: 8px; }
.mt4 { margin-top: 4px; }

.muted {
  color: #6b7280;
}

.link {
  text-decoration: none;
  color: inherit;
}

/* сетка полей */
.grid2 {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: 16px;
}

.grid2 strong {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #9ca3af;
  display: block;
  margin-bottom: 2px;
}

/* ===== CURATED ORGS ===== */
.head-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.head-row h3 {
  margin: 0;
  font-size: 16px;
}

.chip {
  padding: 4px 10px;
  border-radius: 999px;
  background: #f1f5f9;
  font-size: 12px;
  color: #64748b;
}

/* список организаций */
.orgs {
  display: grid;
  gap: 10px;
}

.org {
  display: flex;
  gap: 10px;
  align-items: center;
  border-radius: 16px;
  border: 1px dashed #e5e7eb;
  padding: 8px 10px;
  text-decoration: none;
  color: inherit;
  background: #f9fafb;
  transition: background 0.18s ease, transform 0.18s ease,
    box-shadow 0.18s ease, border-color 0.18s ease;
}

.org:hover {
  background: #ffffff;
  border-color: #bbf7d0;
  box-shadow: 0 10px 22px rgba(15, 23, 42, 0.08);
  transform: translateY(-2px);
}

.logo {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  object-fit: cover;
}

.logo.placeholder {
  display: grid;
  place-items: center;
  background: #dcfce7;
  color: #166534;
  font-weight: 700;
}

.o-name {
  font-weight: 600;
  font-size: 14px;
}

.o-meta {
  display: flex;
  gap: 8px;
  align-items: center;
  font-size: 12px;
}

/* skeleton */
.skeleton {
  height: 180px;
  background: linear-gradient(90deg, #f3f4f6 25%, #e5e7eb 50%, #f3f4f6 75%);
  background-size: 400% 100%;
  animation: shimmer 1.4s infinite;
}

@keyframes shimmer {
  0% { background-position: 0% 0; }
  100% { background-position: -135% 0; }
}

/* empty + error */
.empty {
  border: 1px dashed #e5e7eb;
  border-radius: 16px;
  padding: 14px;
  text-align: center;
  font-size: 13px;
}

.error {
  color: #b91c1c;
  font-size: 13px;
  margin-bottom: 8px;
}
</style>
