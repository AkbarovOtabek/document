<script>
import axios from "axios";
import { API_BASE_URL } from "@/API.js";

/** ====== JWT (как в Users.vue) ====== */
const ACCESS_KEY = "access";
const REFRESH_KEY = "refresh";
const token = {
  get access() { return localStorage.getItem(ACCESS_KEY); },
  get refresh() { return localStorage.getItem(REFRESH_KEY); },
  set({ access, refresh }) {
    if (access) localStorage.setItem(ACCESS_KEY, access);
    if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
  },
  clear() {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  }
};

const api = axios.create({ baseURL: API_BASE_URL });
api.interceptors.request.use((config) => {
  const a = token.access;
  if (a) config.headers.Authorization = `Bearer ${a}`;
  return config;
});

let isRefreshing = false;
let waiters = [];
const flushWaiters = (newAccess) => { waiters.forEach(cb => cb(newAccess)); waiters = []; };

api.interceptors.response.use(
  r => r,
  async (error) => {
    const original = error.config || {};
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      const refresh = token.refresh;
      if (!refresh) { token.clear(); return Promise.reject(error); }

      if (isRefreshing) {
        return new Promise((resolve) => {
          waiters.push((newAccess) => {
            original.headers.Authorization = `Bearer ${newAccess}`;
            resolve(api(original));
          });
        });
      }
      try {
        isRefreshing = true;
        const { data } = await axios.post(`${API_BASE_URL}api/auth/token/refresh/`, { refresh });
        token.set({ access: data.access });
        isRefreshing = false;
        flushWaiters(data.access);
        original.headers.Authorization = `Bearer ${data.access}`;
        return api(original);
      } catch (e) {
        isRefreshing = false;
        token.clear();
        return Promise.reject(e);
      }
    }
    return Promise.reject(error);
  }
);

/** Простая slugify для RU/UZ -> латиница */
function slugify(str = "") {
  const map = {
    а:"a", б:"b", в:"v", г:"g", д:"d", е:"e", ё:"yo", ж:"zh", з:"z", и:"i", й:"y",
    к:"k", л:"l", м:"m", н:"n", о:"o", п:"p", р:"r", с:"s", т:"t", у:"u", ф:"f",
    х:"h", ц:"ts", ч:"ch", ш:"sh", щ:"shch", ы:"y", э:"e", ю:"yu", я:"ya",
    ъ:"", ь:"", қ:"q", ғ:"g‘", ў:"o‘", ҳ:"h", ğ:"g", ı:"i", ş:"sh", ç:"ch",
    А:"a", Б:"b", В:"v", Г:"g", Д:"d", Е:"e", Ё:"yo", Ж:"zh", З:"z", И:"i", Й:"y",
    К:"k", Л:"l", М:"m", Н:"n", О:"o", П:"p", Р:"r", С:"s", Т:"t", У:"u", Ф:"f",
    Х:"h", Ц:"ts", Ч:"ch", Ш:"sh", Щ:"shch", Ы:"y", Э:"e", Ю:"yu", Я:"ya",
    Қ:"q", Ғ:"g", Ў:"o", Һ:"h"
  };
  return str
    .split("")
    .map(ch => map[ch] ?? ch)
    .join("")
    .toLowerCase()
    .replace(/['’`]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

const ORG_LIST_URL   = `api/organizations/list/`;
const ORG_DETAIL_URL = `api/organizations/`;
const CATEGORY_URL   = `api/categories/`;

/** Эндпоинт списка сотрудников для выбора куратора
 *  Поменяй при необходимости на свой:
 *  ожидается массив объектов с полями id, fio/username/email
 */
const EMPLOYEES_URL  = `api/staff/users/`; // <-- при необходимости замени
// Альтернативы: `api/users/list/` или `api/employees/`

export default {
  name: "OrganizationsList",
  props: {
    slug: { type: String, required: true }, // slug категории
    isDark: { type: Boolean, default: false },
  },
  data() {
    return {
      loading: false,
      error: "",
      items: [],         // организации
      categoryName: "",  // отображаемое имя категории
      categoryId: null,

      // сотрудники (для выбора куратора)
      employees: [],
      loadingEmployees: false,

      // UI
      showCreate: false,
      showEdit: false,
      saving: false,

      // формы
      createForm: {
        name: "",
        slug: "",
        autoSlug: true,      // автогенерация slug из name
        description: "",
        address: "",
        lotus: "",
        phone: "",
        email: "",
        logo: null,
        showAdvanced: false,

        // куратор
        hasCurator: false,
        curator: null, // id сотрудника
      },
      editSlug: null,
      editForm: {
        name: "",
        slug: "",
        description: "",
        address: "",
        lotus: "",
        phone: "",
        email: "",
        logo: null,   // новый файл
        keepLogo: true,

        // куратор
        hasCurator: false,
        curator: null, // id
      },
    };
  },
  async mounted() {
    await Promise.all([
      this.fetchOrganizations(),
      this.fetchCategoryNameSafe(),
      this.fetchEmployees(),
    ]);
  },
  watch: {
    slug: {
      async handler() {
        await Promise.all([this.fetchOrganizations(), this.fetchCategoryNameSafe()]);
      },
    },
    // авто-slug при вводе имени
    "createForm.name"(val) {
      if (this.createForm.autoSlug) this.createForm.slug = slugify(val);
    },
    "createForm.autoSlug"(on) {
      if (on) this.createForm.slug = slugify(this.createForm.name);
    }
  },
  computed: {
    themeClass() { return this.isDark ? "dark" : ""; },

    employeeOptions() {
      // Нормализуем список для селекта
      return (this.employees || []).map(u => {
        const name = u.fio || u.full_name || u.username || u.email || `ID ${u.id}`;
        const extra = u.email ? ` • ${u.email}` : "";
        return { id: u.id, label: `${name}${extra}` };
      });
    },
  },
  methods: {
    // ===== API =====
    async fetchOrganizations() {
      try {
        this.loading = true;
        this.error = "";
        const { data } = await api.get(ORG_LIST_URL, { params: { category__slug: this.slug } });
        this.items = Array.isArray(data) ? data : data?.results || [];
      } catch (e) {
        console.error(e);
        this.error = "Не удалось загрузить организации";
      } finally {
        this.loading = false;
      }
    },
    async fetchCategoryNameSafe() {
      try {
        const { data } = await api.get(`${CATEGORY_URL}${this.slug}/`);
        this.categoryName = data?.name || this.slug;
        this.categoryId = data?.id || null;
      } catch {
        this.categoryName = this.slug;
        this.categoryId = null;
      }
    },
    async fetchEmployees() {
      try {
        this.loadingEmployees = true;
        const { data } = await api.get(EMPLOYEES_URL, { params: { is_active: true } });
        // ожидаем массив, при пагинации — data.results
        this.employees = Array.isArray(data) ? data : (data?.results || []);
      } catch (e) {
        console.error(e);
        // не блокируем экран, просто пустой список
        this.employees = [];
      } finally {
        this.loadingEmployees = false;
      }
    },

    // ===== CREATE =====
    openCreate() {
      this.showCreate = true;
    },
    onCreateLogo(e) {
      this.createForm.logo = e.target.files?.[0] || null;
    },
    async createOrganization() {
      if (this.saving) return;
      try {
        this.saving = true;
        this.error = "";

        const fd = new FormData();
        fd.append("name", this.createForm.name.trim());

        // Категория — берём автоматически
        if (this.categoryId) fd.append("category", this.categoryId);
        else fd.append("category_slug", this.slug);

        if (this.createForm.description) fd.append("description", this.createForm.description.trim());
        if (this.createForm.address)     fd.append("address", this.createForm.address.trim());
        if (this.createForm.lotus)       fd.append("lotus", this.createForm.lotus.trim());
        if (this.createForm.phone)       fd.append("phone", this.createForm.phone.trim());
        if (this.createForm.email)       fd.append("email", this.createForm.email.trim());

        if (!this.createForm.autoSlug && this.createForm.slug) {
          fd.append("slug", this.createForm.slug.trim());
        }
        if (this.createForm.logo) fd.append("logo", this.createForm.logo);

        // Куратор (опционально)
        if (this.createForm.hasCurator && this.createForm.curator) {
          fd.append("curator", this.createForm.curator); // <-- поле на бэке должно называться именно так
        } else {
          // если на бэке нужно явно передать отсутствие куратора:
          // fd.append("curator", "");
        }

        await api.post(`api/organizations/create/`, fd, {
          headers: { "Content-Type": "multipart/form-data" },
        });

        this.showCreate = false;
        this.createForm = {
          name: "", slug: "", autoSlug: true,
          description: "", address: "", lotus: "",
          phone: "", email: "", logo: null, showAdvanced: false,
          hasCurator: false, curator: null,
        };
        await this.fetchOrganizations();
      } catch (e) {
        console.error(e);
        this.error = "Не удалось создать организацию";
      } finally {
        this.saving = false;
      }
    },

    // ===== UPDATE =====
    async openEdit(o) {
  this.editSlug = o.slug;

  // 1) тянем ПОДРОБНОСТИ, чтобы взять реального куратора
  let detail = {};
  try {
    const { data } = await api.get(`${ORG_DETAIL_URL}${o.slug}/`);
    detail = data || {};
  } catch (e) {
    console.warn("Не удалось получить детали организации, продолжаем с данными из списка", e);
    detail = o || {};
  }

  // 2) инициализируем форму
  const curId = detail.curator?.id ?? detail.curator ?? null; // поддержка id или объекта
  this.editForm = {
    name: detail.name || o.name || "",
    slug: detail.slug || o.slug || "",
    description: detail.description || o.description || "",
    address: detail.address || o.address || "",
    lotus: detail.lotus || o.lotus || "",
    phone: detail.phone || o.phone || "",
    email: detail.email || o.email || "",
    logo: null,
    keepLogo: true,

    hasCurator: curId != null,
    curator: curId,
    _initialCurator: curId, // запомним, был ли он изначально
  };

  this.showEdit = true;
},
    onEditLogo(e) {
      this.editForm.logo = e.target.files?.[0] || null;
      this.editForm.keepLogo = true;
    },
    async updateOrganization() {
  if (!this.editSlug || this.saving) return;
  try {
    this.saving = true;
    const fd = new FormData();
    fd.append("name", this.editForm.name.trim());
    fd.append("description", this.editForm.description.trim());
    fd.append("address", this.editForm.address.trim());
    fd.append("lotus", this.editForm.lotus.trim());
    fd.append("phone", this.editForm.phone.trim());
    fd.append("email", this.editForm.email.trim());

    if (this.editForm.slug && this.editForm.slug !== this.editSlug) {
      fd.append("slug", this.editForm.slug.trim());
    }

    if (this.editForm.logo) {
      fd.append("logo", this.editForm.logo);
    } else if (!this.editForm.keepLogo) {
      fd.append("logo", ""); // твоя логика удаления
    }

    // ⬇️ КУРАТОР
    if (this.editForm.hasCurator && this.editForm.curator) {
      // назначаем/меняем куратора
      fd.append("curator", this.editForm.curator);
    } else if (this.editForm._initialCurator != null && !this.editForm.hasCurator) {
      // пользователь именно снял галочку — очищаем поле на бэке
      // выбери тот формат, который ждёт сервер: "" или null
      fd.append("curator", ""); // или: fd.append("curator", null)
    }
    // иначе: ничего не отправляем — поле на бэке останется без изменений

    await api.patch(`${ORG_DETAIL_URL}${this.editSlug}/`, fd, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    this.showEdit = false;
    this.editSlug = null;
    await this.fetchOrganizations();
  } catch (e) {
    console.error(e);
    alert("Не удалось сохранить изменения");
  } finally {
    this.saving = false;
  }
},

    // ===== DELETE =====
    async removeOrganization(o) {
      if (!confirm(`Удалить «${o.name}»?`)) return;
      try {
        await api.delete(`${ORG_DETAIL_URL}${o.slug}/`);
        this.items = this.items.filter((x) => x.slug !== o.slug);
      } catch (e) {
        console.error(e);
        alert("Не удалось удалить организацию");
      }
    },

    // ===== FX: 3D cards & sparkline =====
    onTilt(e) {
      const card = e.currentTarget.querySelector(".card-inner");
      const r = e.currentTarget.getBoundingClientRect();
      const x = ((e.clientX - r.left) / r.width) * 2 - 1;
      const y = ((e.clientY - r.top) / r.height) * 2 - 1;
      card.style.transform = `rotateX(${-y * 8}deg) rotateY(${x * 8}deg) translateZ(6px)`;
      card.style.boxShadow = `${-x * 16}px ${y * 18}px 48px rgba(0,0,0,.25)`;
    },
    resetTilt(e) {
      const card = e.currentTarget.querySelector(".card-inner");
      card.style.transform = "";
      card.style.boxShadow = "";
    },
    spark(points = 16) {
      const arr = Array.from({ length: points }, (_, i) =>
        Math.round(20 + Math.sin(i / 2.3) * 10 + (i % 3 ? 5 : -3) + Math.random() * 6)
      );
      const max = Math.max(...arr), min = Math.min(...arr);
      const norm = (v) => 28 - ((v - min) / Math.max(1, max - min)) * 26;
      const step = 100 / (points - 1);
      return arr.map((v, i) => `${i * step},${norm(v)}`).join(" ");
    },

    goBack() { this.$router.back(); },
  },
};
</script>

<template>
  <div class="scene" :class="themeClass">
    <!-- Topbar -->
    <header class="toolbar">
      <div class="left">
        <button class="btn ghost" @click="goBack">← Назад</button>
        <h2 class="title">
          Организации: <span class="hl">{{ categoryName }}</span>
        </h2>
      </div>
      <div class="right">
        <button class="btn primary" @click="openCreate">+ Создать</button>
        <span v-if="loading" class="chip">Загрузка…</span>
        <span v-else class="chip">{{ items.length }} шт.</span>
      </div>
    </header>

    <p v-if="error" class="error">{{ error }}</p>

    <!-- GRID -->
    <section class="cards">
      <article
        v-for="o in items"
        :key="o.slug || o.id"
        class="card"
        @mousemove="onTilt"
        @mouseleave="resetTilt"
      >
        <div
          class="card-inner"
          @click="$router.push({ name: 'org-detail', params: { slug: o.slug } })"
          style="cursor: pointer"
        >
          <div class="card-top">
            <div class="left-meta">
              <img v-if="o.logo" :src="o.logo" class="logo" alt="" />
              <span class="badge">{{ o.category_name || "Категория" }}</span>
            </div>
            <div class="dots"><span></span><span></span><span></span></div>
          </div>

          <h3 class="name-3d">
            <span class="front">{{ o.name }}</span>
            <span class="shadow">{{ o.name }}</span>
          </h3>

          <p class="muted">{{ o.description || "Описание отсутствует." }}</p>

          <div class="grid2">
            <div><strong>Адрес:</strong> <span class="muted">{{ o.address || "—" }}</span></div>
            <div><strong>Lotus:</strong> <span class="muted">{{ o.lotus || "—" }}</span></div>
            <div><strong>Тел.:</strong> <span class="muted">{{ o.phone || "—" }}</span></div>
            <div><strong>Email:</strong> <span class="muted">{{ o.email || "—" }}</span></div>
          </div>

          <div class="chart">
            <svg viewBox="0 0 100 30" preserveAspectRatio="none">
              <polyline :points="spark(18)" class="line" />
            </svg>
          </div>

          <div class="card-actions">
            <button class="btn subtle" @click.stop="openEdit(o)">Редактировать</button>
            <button class="btn danger ghost" @click.stop="removeOrganization(o)">Удалить</button>
            <button class="btn subtle" @click.stop="$router.push({ name: 'org-detail', params: { slug: o.slug } })">
              Подробнее
            </button>
          </div>
        </div>
      </article>

      <div v-if="!loading && items.length === 0" class="empty card">
        <p>Организаций в этой категории пока нет.</p>
      </div>
    </section>

    <!-- CREATE MODAL -->
    <transition name="fade">
      <div class="modal" v-if="showCreate" @click.self="showCreate = false">
        <div class="modal-card" @mousemove="onTilt" @mouseleave="resetTilt">
          <div class="modal-inner card-inner">
            <h3 class="modal-title">Новая организация</h3>

            <div class="row">
              <label>Название *</label>
              <input v-model="createForm.name" class="input" type="text" placeholder="Название…" />
            </div>

            <!-- Куратор -->
            <div class="row">
              <label class="check">
                <input type="checkbox" v-model="createForm.hasCurator" />
                Есть куратор
              </label>
              <div v-if="createForm.hasCurator">
                <select v-model="createForm.curator" class="input">
                  <option :value="null" disabled>Выберите сотрудника…</option>
                  <option v-for="u in employeeOptions" :key="u.id" :value="u.id">
                    {{ u.label }}
                  </option>
                </select>
                <small class="muted" v-if="loadingEmployees">Загрузка списка сотрудников…</small>
                <small class="muted" v-else-if="!employeeOptions.length">Сотрудники не найдены</small>
              </div>
            </div>

            <details class="adv">
              <summary @click.prevent="createForm.showAdvanced = !createForm.showAdvanced">
                Доп. поля
              </summary>
              <div v-if="createForm.showAdvanced">
                <div class="row">
                  <label>
                    <input type="checkbox" v-model="createForm.autoSlug" />
                    Авто-slug из названия
                  </label>
                </div>
                <div class="row">
                  <label>Slug (если нужно вручную)</label>
                  <input v-model="createForm.slug" class="input" type="text" :disabled="createForm.autoSlug" />
                </div>
              </div>
            </details>

            <div class="row">
              <label>Описание</label>
              <textarea
                v-model="createForm.description"
                class="input area"
                rows="3"
                placeholder="Короткое описание"
              ></textarea>
            </div>

            <div class="grid2 form-grid">
              <div class="row"><label>Адрес</label><input v-model="createForm.address" class="input" type="text" /></div>
              <div class="row"><label>Lotus</label><input v-model="createForm.lotus" class="input" type="text" /></div>
              <div class="row"><label>Телефон</label><input v-model="createForm.phone" class="input" type="text" /></div>
              <div class="row"><label>Email</label><input v-model="createForm.email" class="input" type="email" /></div>
            </div>

            <div class="row">
              <label>Логотип (иконка)</label>
              <input class="input file" type="file" accept="image/*" @change="onCreateLogo" />
            </div>

            <div class="row submit">
              <button class="btn primary" :disabled="saving || !createForm.name" @click="createOrganization">
                {{ saving ? "Сохраняем…" : "Создать" }}
              </button>
              <button class="btn ghost" @click="showCreate = false">Отмена</button>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- EDIT MODAL -->
    <transition name="fade">
      <div class="modal" v-if="showEdit" @click.self="showEdit = false">
        <div class="modal-card" @mousemove="onTilt" @mouseleave="resetTilt">
          <div class="modal-inner card-inner">
            <h3 class="modal-title">Редактировать организацию</h3>

            <div class="row">
              <label>Название *</label>
              <input v-model="editForm.name" class="input" type="text" />
            </div>

            <!-- Куратор -->
            <div class="row">
              <label class="check">
                <input type="checkbox" v-model="editForm.hasCurator" />
                Есть куратор
              </label>
              <div v-if="editForm.hasCurator">
                <select v-model="editForm.curator" class="input">
                  <option :value="null" disabled>Выберите сотрудника…</option>
                  <option v-for="u in employeeOptions" :key="u.id" :value="u.id">
                    {{ u.label }}
                  </option>
                </select>
                <small class="muted" v-if="loadingEmployees">Загрузка списка сотрудников…</small>
                <small class="muted" v-else-if="!employeeOptions.length">Сотрудники не найдены</small>
              </div>
            </div>

            <details class="adv">
              <summary>Доп. поля</summary>
              <div class="row">
                <label>Slug (смена slug на свой риск)</label>
                <input v-model="editForm.slug" class="input" type="text" />
              </div>
            </details>

            <div class="row">
              <label>Описание</label>
              <textarea v-model="editForm.description" class="input area" rows="3"></textarea>
            </div>

            <div class="grid2 form-grid">
              <div class="row"><label>Адрес</label><input v-model="editForm.address" class="input" type="text" /></div>
              <div class="row"><label>Lotus</label><input v-model="editForm.lotus" class="input" type="text" /></div>
              <div class="row"><label>Телефон</label><input v-model="editForm.phone" class="input" type="text" /></div>
              <div class="row"><label>Email</label><input v-model="editForm.email" class="input" type="email" /></div>
            </div>

            <div class="row">
              <label>Логотип</label>
              <input class="input file" type="file" accept="image/*" @change="onEditLogo" />
              <label class="check"><input type="checkbox" v-model="editForm.keepLogo" /> оставить текущий</label>
            </div>

            <div class="row submit">
              <button class="btn primary" :disabled="saving || !editForm.name" @click="updateOrganization">
                {{ saving ? "Сохраняем…" : "Сохранить" }}
              </button>
              <button class="btn ghost" @click="showEdit = false">Отмена</button>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
/* ====== THEME ====== */
.scene {
  --bg: #f6f7fb;
  --panel: #fff;
  --ink: #0f141a;
  --muted: #6b7280;
  --primary: #19c46d;
  --line: #e6e8ee;
  --ring: rgba(25, 196, 109, 0.24);
  --accent: #2bdf83;
  min-height: calc(100vh - 64px);
  background: radial-gradient(1200px 600px at 70% -100px, rgba(25, 196, 109, 0.12), transparent 60%),
    var(--bg);
  color: var(--ink);
  display: flex;
  flex-direction: column;
}
.scene.dark {
  --bg: #0f1118;
  --panel: #151b22;
  --ink: #eaf0f6;
  --muted: #94a3b8;
  --primary: #2bdf83;
  --line: #222a36;
  --ring: rgba(43, 223, 131, 0.2);
  background: radial-gradient(1300px 700px at 70% -120px, rgba(43, 223, 131, 0.1), transparent 60%),
    var(--bg);
}

/* ====== HEADER ====== */
.toolbar {
  margin-top: 70px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 22px 8px;
  gap: 12px;
}
.left { display: flex; align-items: center; gap: 12px; }
.title { margin: 0; font-size: 22px; }
.hl { color: var(--primary); }
.right .chip {
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 6px 12px;
  color: var(--muted);
  font-weight: 700;
}

.error { color: #ef4444; margin: 8px 22px; }

/* ====== GRID ====== */
.cards {
  width: 100%;
  padding: 22px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}
.card { perspective: 900px; }
.card-inner {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0)),
    var(--panel);
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 16px;
  transform-style: preserve-3d;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  box-shadow: 0 18px 38px rgba(0, 0, 0, 0.14);
}
.card-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.left-meta { display: flex; align-items: center; gap: 8px; }
.logo { width: 28px; height: 28px; object-fit: cover; border-radius: 8px; border: 1px solid var(--line); }
.badge {
  display: inline-flex; align-items: center; height: 24px; padding: 0 10px; border-radius: 999px;
  background: rgba(25, 196, 109, 0.15); color: var(--primary); border: 1px solid rgba(25, 196, 109, 0.25);
  font-weight: 800; font-size: 12px; letter-spacing: 0.3px;
}
.dots span { display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: var(--line); margin-left: 4px; }

/* 3D text */
.name-3d { position: relative; margin: 8px 0 6px; font-size: 20px; line-height: 1.2; transform-style: preserve-3d; }
.name-3d .front { position: relative; z-index: 1; }
.name-3d .shadow { position: absolute; left: 2px; top: 2px; z-index: 0; opacity: 0.15; transform: translateZ(-8px); }

.muted { color: var(--muted); }

.grid2 { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; margin: 10px 0 12px; }

.card-actions { display: flex; gap: 10px; }

.btn {
  height: 36px; padding: 0 12px; border-radius: 12px; border: 1px solid var(--line);
  background: var(--panel); color: var(--ink); font-weight: 800; cursor: pointer; transition: 0.18s ease;
}
.btn:hover { transform: translateY(-1px); box-shadow: 0 12px 24px rgba(0,0,0,0.12); }
.btn.primary { background: var(--primary); color: #fff; border-color: transparent; }
.btn.ghost { background: transparent; }
.btn.subtle { background: transparent; border-color: var(--line); }
.btn.danger.ghost { color: #ef4444; }
.btn.danger.ghost:hover { border-color: #ef4444; }

.empty { grid-column: 1/-1; text-align: center; padding: 26px; }

/* ====== SPARKLINE ====== */
.chart { height: 36px; margin: 6px 0 10px; }
.chart svg { width: 100%; height: 100%; }
.chart .line { fill: none; stroke: var(--accent); stroke-width: 2.4; filter: drop-shadow(0 2px 6px rgba(43, 223, 131, 0.35)); }

/* ====== MODALS ====== */
.fade-enter-active, .fade-leave-active { transition: opacity 0.18s ease, transform 0.18s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(6px); }

.modal {
  position: fixed; inset: 0; background: rgba(0, 0, 0, 0.35);
  display: flex; align-items: center; justify-content: center; padding: 18px; z-index: 60;
}
.modal-card { perspective: 900px; max-width: 760px; width: min(760px, 95vw); }
.modal-inner {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0)), var(--panel);
  border: 1px solid var(--line); border-radius: 18px; padding: 18px;
}
.modal-title { margin: 0 0 8px; }
.row { display: grid; gap: 6px; margin-top: 10px; }
label { font-weight: 800; font-size: 12px; color: var(--muted); }
.input {
  height: 42px; border: 1px solid var(--line); border-radius: 12px; padding: 0 12px;
  background: transparent; color: var(--ink); outline: none;
}
.input.area { height: auto; padding: 10px 12px; resize: vertical; }
.input.file { padding: 8px; height: auto; }
.input:focus { border-color: var(--primary); box-shadow: 0 0 0 4px var(--ring); }
.form-grid .row { margin-top: 0; }
details.adv summary { cursor: pointer; font-weight: 800; color: var(--muted); margin-top: 6px; }

/* Responsive */
@media (max-width: 1080px) { .cards { grid-template-columns: 1fr 1fr; } }
@media (max-width: 720px)  { .cards { grid-template-columns: 1fr; } }
</style>
