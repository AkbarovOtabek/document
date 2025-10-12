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
    <header class="toolbar">
      <h1>Аккаунт</h1>
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
          <div v-if="me.management" class="meta muted">
            <span><strong>Управление:</strong> {{ me.management.name }}</span>
          </div>
          <div v-if="me.department" class="meta muted">
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
                    lnk.organization_data?.category_name || lnk.organization_data?.category_slug
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
</template>

<style scoped>
/* ===== THEME ===== */
.scene {
  --bg: #f6f7fb;
  --panel: #fff;
  --ink: #0f141a;
  --muted: #6b7280;
  --primary: #19c46d;
  --primary-ink: #0ea95b;
  --line: #e6e8ee;
  --ring: rgba(25, 196, 109, 0.2);
  min-height: calc(100vh - 64px);
  background: radial-gradient(1200px 600px at 70% -120px, rgba(25, 196, 109, 0.1), transparent 60%),
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
  background: radial-gradient(1200px 600px at 70% -120px, rgba(43, 223, 131, 0.1), transparent 60%),
    var(--bg);
}

/* ===== LAYOUT ===== */
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 22px 8px;
}
.grid {
  padding: 12px 22px 24px;
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 18px;
}
@media (max-width: 980px) {
  .grid {
    grid-template-columns: 1fr;
  }
}

/* ===== CARDS ===== */
.card {
  perspective: 900px;
}
.card-inner {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.06), rgba(255, 255, 255, 0)),
    var(--panel);
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 16px;
  box-shadow: 0 18px 38px rgba(0, 0, 0, 0.14);
}
.profile .top {
  display: flex;
  gap: 14px;
  align-items: center;
}
.avatar {
  width: 72px;
  height: 72px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  color: #fff;
  font-weight: 900;
  font-size: 22px;
  background: linear-gradient(145deg, var(--primary), var(--primary-ink));
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
  background: rgba(25, 196, 109, 0.15);
  color: var(--primary);
  border: 1px solid rgba(25, 196, 109, 0.25);
  font-weight: 800;
  font-size: 12px;
}
.pill.ghost {
  background: transparent;
  color: var(--muted);
  border-color: var(--line);
}
.pill.tiny {
  height: 20px;
  font-size: 11px;
  padding: 0 8px;
  margin-left: 8px;
}
.meta {
  display: flex;
  gap: 16px;
  margin-top: 6px;
  flex-wrap: wrap;
}
.muted {
  color: var(--muted);
}
.link {
  text-decoration: none;
}
.grid2 {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: 14px;
}
.grid2 strong {
  font-size: 12px;
  color: var(--muted);
  display: block;
}

/* Orgs (router-links) */
.orgs {
  display: grid;
  gap: 10px;
}
.org {
  display: flex;
  gap: 10px;
  align-items: center;
  border: 1px dashed var(--line);
  padding: 10px;
  border-radius: 14px;
  transition: background 0.2s, transform 0.2s;
}
.org:hover {
  background: rgba(25, 196, 109, 0.08);
  transform: translateY(-2px);
}
.logo {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  object-fit: cover;
}
.logo.placeholder {
  display: grid;
  place-items: center;
  background: rgba(25, 196, 109, 0.18);
  color: #fff;
  font-weight: 900;
}
.o-name {
  font-weight: 800;
}
.o-meta {
  display: flex;
  gap: 8px;
  align-items: center;
}
.empty {
  border: 1px dashed var(--line);
  border-radius: 14px;
  padding: 14px;
  text-align: center;
}
.error {
  color: #ef4444;
  margin: 8px 22px;
}
</style>
