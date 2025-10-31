<script>
import axios from "axios";
import { API_BASE_URL } from "@/API.js";

/** Справочник должностей для селектов (русские лейблы) */
const POSITION_OPTIONS = [
  { value: "director",          label: "Директор" },
  { value: "deputy_director",   label: "Заместитель директора (по управлению)" },
  { value: "head_of_department", label: "Начальник отдела" },
  { value: "chief_expert",      label: "Главный эксперт" },
  { value: "lead_expert",       label: "Ведущий эксперт" },
  { value: "expert_l1",         label: "Эксперт первого уровня" },
  { value: "employee",          label: "Сотрудник" },
  { value: "records_clerk",     label: "Делопроизводитель" },
];

/** Простейшее хранение JWT в localStorage */
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

/** Локальный axios-инстанс с baseURL и перехватчиками */
const api = axios.create({ baseURL: API_BASE_URL });

// Подставляем Authorization
api.interceptors.request.use((config) => {
  const a = token.access;
  if (a) config.headers.Authorization = `Bearer ${a}`;
  return config;
});

// Обновление access по 401 через /api/auth/token/refresh/
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
        // Важно: endpoints соответствуют твоему urls.py
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

export default {
  name: "Users",
  data() {
    return {
      loading: false,
      error: "",

      positionOptions: POSITION_OPTIONS,

      // исходные данные
      managements: [],   // GET api/staff/management/
      departments: [],   // GET api/staff/departments/
      staff: [],         // GET api/staff/users/

      // выбор/детали
      selectedStaff: null,
      query: "",

      // модалки
      mod: { show: false, kind: null, payload: null },

      // формы
      form: {
        mu: { name: "" },
        dep: { name: "", management_id: null },
        /** Привязка существующего StaffProfile к управлению/отделу + заполнение полей */
        staffAttach: {
          staff_id: null,
          management_id: null,
          department_id: null,
          position: "employee",
          role: "curator",
          lotus: "",
          work_email: "",
          work_phone: ""
        },
        /** Редактирование профиля сотрудника */
        staffEdit: {
          first_name: "",
          second_name: "",
          last_name: "",
          position: "",
          role: "",
          lotus: "",
          work_email: "",
          work_phone: "",
          management_id: null,
          department_id: null
        },
      },
    };
  },
  computed: {
    /** Строим древовидное представление: Управление -> Отделы -> Сотрудники */
    tree() {
      const depsByMgmt = new Map();
      for (const d of this.departments) {
        const key = d.management?.id || d.management_id || d.management?.pk || d.management || d.management_data?.id;
        if (!depsByMgmt.has(key)) depsByMgmt.set(key, []);
        depsByMgmt.get(key).push(d);
      }
      // группируем сотрудников по паре (management_id, department_id)
      const staffByPair = new Map();
      for (const s of this.staff) {
        const m = s.management?.id ?? s.management?.pk ?? s.management_id ?? null;
        const d = s.department?.id ?? s.department?.pk ?? s.department_id ?? null;
        const key = `${m || "none"}::${d || "none"}`;
        if (!staffByPair.has(key)) staffByPair.set(key, []);
        staffByPair.get(key).push(s);
      }

      const nodes = [];
      for (const mu of this.managements) {
        const muId = mu.id;
        // все отделы управления
        const children = (depsByMgmt.get(muId) || [])
          .sort((a, b) => (a.name || "").localeCompare(b.name || ""))
          .map((dep) => {
            const depId = dep.id;
            const key = `${muId}::${depId}`;
            const members = (staffByPair.get(key) || [])
              .slice()
              .sort((a, b) => (a.last_name || a.fio || "").localeCompare(b.last_name || b.fio || ""));
            return { kind: "dep", data: dep, staff: members };
          });

        // сотрудники управления без отдела
        const noDeptKey = `${muId}::none`;
        const floating = (staffByPair.get(noDeptKey) || [])
          .slice()
          .sort((a, b) => (a.last_name || a.fio || "").localeCompare(b.last_name || b.fio || ""));

        nodes.push({ kind: "mu", data: mu, deps: children, staffFloating: floating });
      }

      // сотрудники без управления и без отдела
      const noMgmtKey = `none::none`;
      const unassigned = (staffByPair.get(noMgmtKey) || [])
        .slice()
        .sort((a, b) => (a.last_name || a.fio || "").localeCompare(b.last_name || b.fio || ""));

      return { nodes, unassigned };
    },

    /** Поиск по ФИО/позиции/ролям/контактам */
    filteredTree() {
      const q = this.query.trim().toLowerCase();
      if (!q) return this.tree;

      const matchStaff = (s) => {
        const parts = [
          s.fio, s.first_name, s.second_name, s.last_name,
          s.position, s.role, s.work_email, s.work_phone, s.lotus,
          s.username, s.email
        ].filter(Boolean).map(String);
        return parts.some((p) => p.toLowerCase().includes(q));
      };

      const copy = { nodes: [], unassigned: [] };
      for (const muNode of this.tree.nodes) {
        const deps = [];
        for (const depNode of muNode.deps) {
          const staff = depNode.staff.filter(matchStaff);
          if (staff.length || (depNode.data.name || "").toLowerCase().includes(q)) {
            deps.push({ ...depNode, staff });
          }
        }
        const floating = muNode.staffFloating.filter(matchStaff);
        if (deps.length || floating.length || (muNode.data.name || "").toLowerCase().includes(q)) {
          copy.nodes.push({ ...muNode, deps, staffFloating: floating });
        }
      }
      copy.unassigned = this.tree.unassigned.filter(matchStaff);
      return copy;
    },
  },
  async mounted() {
    await this.loadAll();
  },
  methods: {
    /** Загрузка всех списков */
    async loadAll() {
      try {
        this.loading = true;
        this.error = "";
        // baseURL уже http://127.0.0.1:8000/
        const [mu, dep, staff] = await Promise.all([
          api.get("api/staff/management/"),
          api.get("api/staff/departments/"),
          api.get("api/staff/users/"),
        ]);
        this.managements = mu.data?.results || mu.data || [];
        this.departments = dep.data?.results || dep.data || [];
        this.staff = (staff.data?.results || staff.data || []).map((s) => ({ ...s, fio: s.fio }));
      } catch (e) {
        console.error(e);
        this.error = "Не удалось загрузить структуру пользователей";
      } finally {
        this.loading = false;
      }
    },
    openCreateMu(){ 
      this.mod = { 
        show: true, 
        kind: "mu-create",   
        payload: null 
      },           
      this.form.mu = { name: "" }; 
    },
    openEditMu(mu)        { this.mod = { show: true, kind: "mu-edit",     payload: mu };              this.form.mu = { name: mu.name }; },
    openDeleteMu(mu)      { this.mod = { show: true, kind: "mu-delete",   payload: mu }; },

    openCreateDep(mu)     { this.mod = { show: true, kind: "dep-create",  payload: mu };              this.form.dep = { name: "", management_id: mu.id }; },
    openEditDep(dep)      { this.mod = { show: true, kind: "dep-edit",    payload: dep };             this.form.dep = { name: dep.name, management_id: dep.management?.id || dep.management_id }; },
    openDeleteDep(dep)    { this.mod = { show: true, kind: "dep-delete",  payload: dep }; },

    openAttachStaff(muOrDep) {
      // Привязка существующего профиля к управлению/отделу
      const management_id = muOrDep.kind === "mu"
        ? muOrDep.data.id
        : muOrDep.management?.id || muOrDep.data?.management?.id || muOrDep.management_id || muOrDep.data?.management_id;
      const department_id = muOrDep.kind === "dep" ? (muOrDep.data?.id || muOrDep.id) : null;

      this.mod = { show: true, kind: "staff-attach", payload: muOrDep };
      this.form.staffAttach = {
        staff_id: null,
        management_id,
        department_id,
        position: "employee",
        role: "curator",
        lotus: "",
        work_email: "",
        work_phone: ""
      };
    },

    openEditStaff(staff) {
      this.mod = { show: true, kind: "staff-edit", payload: staff };
      this.form.staffEdit = {
        first_name:   staff.first_name   || "",
        second_name:  staff.second_name  || "",
        last_name:    staff.last_name    || "",
        position:     staff.position     || "",
        role:         staff.role         || "curator",
        lotus:        staff.lotus        || "",
        work_email:   staff.work_email   || "",
        work_phone:   staff.work_phone   || "",
        management_id: staff.management?.id || staff.management_id || null,
        department_id: staff.department?.id || staff.department_id || null,
      };
    },
    openDeleteStaff(staff) { this.mod = { show: true, kind: "staff-delete", payload: staff }; },
    closeModal() { this.mod = { show: false, kind: null, payload: null }; },

    // ===== CRUD: Управление
    async createMu() {
      await api.post("api/staff/management/", { name: this.form.mu.name });
      await this.loadAll();
      this.closeModal();
    },
    async updateMu() {
      await api.patch(`api/staff/management/${this.mod.payload.id}/`, { name: this.form.mu.name });
      await this.loadAll();
      this.closeModal();
    },
    async deleteMu() {
      await api.delete(`api/staff/management/${this.mod.payload.id}/`);
      await this.loadAll();
      this.closeModal();
    },

    // ===== CRUD: Отдел
    async createDep() {
      await api.post("api/staff/departments/", {
        name: this.form.dep.name,
        management_id: this.form.dep.management_id
      });
      await this.loadAll();
      this.closeModal();
    },
    async updateDep() {
      await api.patch(`api/staff/departments/${this.mod.payload.id}/`, {
        name: this.form.dep.name,
        management_id: this.form.dep.management_id
      });
      await this.loadAll();
      this.closeModal();
    },
    async deleteDep() {
      await api.delete(`api/staff/departments/${this.mod.payload.id}/`);
      await this.loadAll();
      this.closeModal();
    },

    // ===== Сотрудник
    /** Привязка существующего StaffProfile и заполнение полей */
    async attachStaff() {
      const { staff_id, management_id, department_id, position, role, lotus, work_email, work_phone } = this.form.staffAttach;
      await api.patch(`api/staff/users/${staff_id}/`, {
        management_id,
        department_id,
        position,
        role,
        lotus,
        work_email,
        work_phone,
      });
      await this.loadAll();
      this.closeModal();
    },

    /** Обновление профиля сотрудника */
    async updateStaff() {
      await api.patch(`api/staff/users/${this.mod.payload.id}/`, { ...this.form.staffEdit });
      await this.loadAll();
      this.closeModal();
    },

    /** Удаление профиля сотрудника */
    async deleteStaff() {
      await api.delete(`api/staff/users/${this.mod.payload.id}/`);
      await this.loadAll();
      this.closeModal();
      if (this.selectedStaff && this.selectedStaff.id === this.mod.payload.id) this.selectedStaff = null;
    },

    // ===== UI helpers
    selectStaff(s) { this.selectedStaff = s; },
    staffBadge(s) {
      const parts = [];
      if (s.role) parts.push(s.role);
      if (s.position) {
        const p = this.positionOptions.find(x => x.value === s.position);
        parts.push(p ? p.label : s.position);
      }
      return parts.join(" · ");
    },
    fullFio(s) { return s.fio || [s.last_name, s.first_name, s.second_name].filter(Boolean).join(" "); },
  },
};
</script>

<template>
  <div class="scene">
    <header class="head">
      <h1>Пользователи (дерево)</h1>
      <div class="tools">
        <input v-model="query" type="search" class="inp" placeholder="Поиск по сотрудникам…" />
        <button class="btn" @click="openCreateMu">+ Управление</button>
      </div>
    </header>

    <p v-if="error" class="error">{{ error }}</p>
    <div v-if="loading" class="skeleton">Загрузка…</div>

    <div v-else class="grid">
      <!-- ЛЕВАЯ КОЛОНКА: дерево -->
      <section class="left">
        <div v-for="muNode in filteredTree.nodes" :key="muNode.data.id" class="mu">
          <div class="mu-head">
            <div class="mu-title"><strong>{{ muNode.data.name }}</strong></div>
            <div class="mu-actions">
              <button class="ghost" @click="openCreateDep(muNode.data)">+ Отдел</button>
              <button class="ghost" @click="openAttachStaff({ kind:'mu', data: muNode.data })">+ Сотрудник</button>
              <button class="ghost" @click="openEditMu(muNode.data)">Изм.</button>
              <button class="danger" @click="openDeleteMu(muNode.data)">Удалить</button>
            </div>
          </div>

          <div class="deps">
            <div v-for="depNode in muNode.deps" :key="depNode.data.id" class="dep">
              <div class="dep-head">
                <div class="dep-title">
                  <span class="dot"></span>
                  <strong>{{ depNode.data.name }}</strong>
                </div>
                <div class="dep-actions">
                  <button class="ghost" @click="openAttachStaff({ kind:'dep', data: depNode.data })">+ Сотр.</button>
                  <button class="ghost" @click="openEditDep(depNode.data)">Изм.</button>
                  <button class="danger" @click="openDeleteDep(depNode.data)">Удалить</button>
                </div>
              </div>

              <ul class="staff-list" v-if="depNode.staff.length">
                <li v-for="s in depNode.staff" :key="s.id" class="staff" @click="selectStaff(s)">
                  <b>{{ fullFio(s) }}</b><span class="muted"> — {{ staffBadge(s) }}</span>
                </li>
              </ul>
              <div v-else class="muted small pad">Нет сотрудников</div>
            </div>

            <div v-if="muNode.staffFloating.length" class="dep">
              <div class="dep-head">
                <div class="dep-title"><span class="dot"></span><strong>(без отдела)</strong></div>
                <div class="dep-actions">
                  <button class="ghost" @click="openAttachStaff({ kind:'mu', data: muNode.data })">+ Сотр.</button>
                </div>
              </div>
              <ul class="staff-list">
                <li v-for="s in muNode.staffFloating" :key="s.id" class="staff" @click="selectStaff(s)">
                  <b>{{ fullFio(s) }}</b><span class="muted"> — {{ staffBadge(s) }}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div v-if="filteredTree.unassigned.length" class="mu">
          <div class="mu-head">
            <div class="mu-title"><strong>(без управления)</strong></div>
            <div class="mu-actions">
              <button class="ghost" @click="openAttachStaff({ kind:'mu', data: { id: null } })">+ Сотрудник</button>
            </div>
          </div>
          <ul class="staff-list">
            <li v-for="s in filteredTree.unassigned" :key="s.id" class="staff" @click="selectStaff(s)">
              <b>{{ fullFio(s) }}</b><span class="muted"> — {{ staffBadge(s) }}</span>
            </li>
          </ul>
        </div>
      </section>

      <!-- ПРАВАЯ КОЛОНКА: карточка сотрудника -->
      <aside class="right">
        <div v-if="!selectedStaff" class="muted empty">Выберите сотрудника слева.</div>

        <div v-else class="card">
          <div class="card-head">
            <div class="title">
              <h3>{{ fullFio(selectedStaff) }}</h3>
              <div class="sub">
                <span class="tag" v-if="selectedStaff.role">{{ selectedStaff.role }}</span>
                <span class="muted" v-if="selectedStaff.position"> · {{ staffBadge(selectedStaff).split(' · ').slice(-1)[0] }}</span>
              </div>
            </div>
            <div class="actions">
              <button class="ghost" @click="openEditStaff(selectedStaff)">Изменить</button>
              <button class="danger" @click="openDeleteStaff(selectedStaff)">Удалить</button>
            </div>
          </div>

          <div class="grid2">
            <div>
              <div class="kv"><b>Управление:</b> <span class="muted">{{ selectedStaff.management?.name || "—" }}</span></div>
              <div class="kv"><b>Отдел:</b> <span class="muted">{{ selectedStaff.department?.name || "—" }}</span></div>
              <div class="kv"><b>Lotus:</b> <span class="muted">{{ selectedStaff.lotus || "—" }}</span></div>
              <div class="kv"><b>Телефон:</b> <span class="muted">{{ selectedStaff.work_phone || "—" }}</span></div>
              <div class="kv"><b>Email:</b> <span class="muted">{{ selectedStaff.work_email || selectedStaff.email || "—" }}</span></div>
            </div>
            <div>
              <div class="kv"><b>Имя пользователя:</b> <span class="muted">{{ selectedStaff.username }}</span></div>
              <div class="kv"><b>Куратор:</b>
                <span class="muted">
                  {{
                    (selectedStaff.links?.length ||
                     selectedStaff.curated_organizations?.length ||
                     selectedStaff.curated_by_categories?.length) ? "да" : "нет"
                  }}
                </span>
              </div>
            </div>
          </div>

          <div class="block">
            <h4>Организации (куратор напрямую)</h4>
            <ul class="lines">
              <li
                v-for="lnk in (selectedStaff.links || []).filter(l => l.organization_data)"
                :key="lnk.id"
              >
                <b>{{ lnk.organization_data.name }}</b>
                <span class="muted"> — {{ lnk.organization_data.category_name }}</span>
              </li>
              <li v-if="!((selectedStaff.links || []).some(l => l.organization_data))" class="muted">Нет</li>
            </ul>
          </div>

          <div class="block">
            <h4>Организации по курируемым категориям</h4>
            <ul class="lines">
              <li v-for="o in (selectedStaff.curated_by_categories || [])" :key="o.id">
                <b>{{ o.name }}</b> <span class="muted"> — {{ o.category_name }}</span>
              </li>
              <li v-if="!(selectedStaff.curated_by_categories || []).length" class="muted">Нет</li>
            </ul>
          </div>
        </div>
      </aside>
    </div>

    <!-- МОДАЛКИ -->
    <div v-if="mod.show" class="m-ov" @click.self="closeModal">
      <div class="m-card">
        <header class="m-head">
          <h3 class="m-title">
            {{
              mod.kind === 'mu-create'   ? 'Новое управление' :
              mod.kind === 'mu-edit'     ? 'Переименовать управление' :
              mod.kind === 'mu-delete'   ? 'Удалить управление' :
              mod.kind === 'dep-create'  ? 'Новый отдел' :
              mod.kind === 'dep-edit'    ? 'Переименовать отдел' :
              mod.kind === 'dep-delete'  ? 'Удалить отдел' :
              mod.kind === 'staff-attach'? 'Добавить сотрудника (привязка профиля)' :
              mod.kind === 'staff-edit'  ? 'Изменить сотрудника' :
              mod.kind === 'staff-delete'? 'Удалить сотрудника' : ''
            }}
          </h3>
          <button class="m-x" @click="closeModal">×</button>
        </header>

        <div class="m-body">
          <!-- Управление -->
          <template v-if="mod.kind==='mu-create' || mod.kind==='mu-edit'">
            <label class="f-l">
              <span>Название</span>
              <input v-model="form.mu.name" class="inp" placeholder="Управление ..." />
            </label>
          </template>

          <!-- Отдел -->
          <template v-else-if="mod.kind==='dep-create' || mod.kind==='dep-edit'">
            <div class="f-grid">
              <label class="f-l">
                <span>Название</span>
                <input v-model="form.dep.name" class="inp" placeholder="Отдел ..." />
              </label>
              <label class="f-l">
                <span>Управление</span>
                <select v-model="form.dep.management_id" class="inp">
                  <option :value="null">—</option>
                  <option v-for="m in managements" :key="m.id" :value="m.id">{{ m.name }}</option>
                </select>
              </label>
            </div>
          </template>

          <!-- Привязка сотрудника -->
          <template v-else-if="mod.kind==='staff-attach'">
            <div class="f-grid">
              <label class="f-l">
                <span>Профиль сотрудника</span>
                <select v-model="form.staffAttach.staff_id" class="inp">
                  <option :value="null">— выберите —</option>
                  <option v-for="s in staff" :key="s.id" :value="s.id">
                    {{ fullFio(s) }} ({{ s.username }})
                  </option>
                </select>
              </label>
              <label class="f-l">
                <span>Управление</span>
                <select v-model="form.staffAttach.management_id" class="inp">
                  <option :value="null">(без управления)</option>
                  <option v-for="m in managements" :key="m.id" :value="m.id">{{ m.name }}</option>
                </select>
              </label>
              <label class="f-l">
                <span>Отдел</span>
                <select v-model="form.staffAttach.department_id" class="inp">
                  <option :value="null">(без отдела)</option>
                  <option
                    v-for="d in departments.filter(d => (d.management?.id || d.management_id) === form.staffAttach.management_id)"
                    :key="d.id" :value="d.id"
                  >
                    {{ d.name }}
                  </option>
                </select>
              </label>
            </div>

            <div class="f-grid">
              <label class="f-l">
                <span>Должность</span>
                <select v-model="form.staffAttach.position" class="inp">
                  <option v-for="opt in positionOptions" :key="opt.value" :value="opt.value">
                    {{ opt.label }}
                  </option>
                </select>
              </label>
              <label class="f-l">
                <span>Роль доступа</span>
                <select v-model="form.staffAttach.role" class="inp">
                  <option value="admin">admin</option>
                  <option value="manager">manager</option>
                  <option value="curator">curator</option>
                  <option value="viewer">viewer</option>
                </select>
              </label>
            </div>

            <div class="f-grid">
              <label class="f-l">
                <span>Lotus</span>
                <input v-model="form.staffAttach.lotus" class="inp" placeholder="01cert16" />
              </label>
              <label class="f-l">
                <span>Рабочий email</span>
                <input v-model="form.staffAttach.work_email" class="inp" type="email" placeholder="name@company.com" />
              </label>
            </div>
            <label class="f-l">
              <span>Рабочий телефон</span>
              <input v-model="form.staffAttach.work_phone" class="inp" placeholder="+998 ..." />
            </label>

            <div class="muted small">
              Подсказка: нового Django-пользователя создаём отдельно (админка/ручка). Здесь привязываем уже существующий профиль.
            </div>
          </template>

          <!-- Редактирование сотрудника -->
          <template v-else-if="mod.kind==='staff-edit'">
            <div class="f-grid">
              <label class="f-l"><span>Фамилия</span><input v-model="form.staffEdit.last_name" class="inp" /></label>
              <label class="f-l"><span>Имя</span><input v-model="form.staffEdit.first_name" class="inp" /></label>
              <label class="f-l"><span>Отчество</span><input v-model="form.staffEdit.second_name" class="inp" /></label>
            </div>
            <div class="f-grid">
              <label class="f-l">
                <span>Должность</span>
                <select v-model="form.staffEdit.position" class="inp">
                  <option v-for="opt in positionOptions" :key="opt.value" :value="opt.value">
                    {{ opt.label }}
                  </option>
                </select>
              </label>
              <label class="f-l">
                <span>Роль</span>
                <select v-model="form.staffEdit.role" class="inp">
                  <option value="admin">admin</option>
                  <option value="manager">manager</option>
                  <option value="curator">curator</option>
                  <option value="viewer">viewer</option>
                </select>
              </label>
            </div>
            <div class="f-grid">
              <label class="f-l"><span>Рабочий email</span><input v-model="form.staffEdit.work_email" class="inp" type="email" /></label>
              <label class="f-l"><span>Рабочий телефон</span><input v-model="form.staffEdit.work_phone" class="inp" /></label>
            </div>
            <label class="f-l"><span>Lotus</span><input v-model="form.staffEdit.lotus" class="inp" /></label>
          </template>

          <!-- Удаления -->
          <template v-else-if="mod.kind==='mu-delete'">Удалить управление «{{ mod.payload.name }}»?</template>
          <template v-else-if="mod.kind==='dep-delete'">Удалить отдел «{{ mod.payload.name }}»?</template>
          <template v-else-if="mod.kind==='staff-delete'">Удалить профиль «{{ fullFio(mod.payload) }}»?</template>
        </div>

        <footer class="m-foot">
          <button class="btn ghost" @click="closeModal">Отмена</button>

          <button v-if="mod.kind==='mu-create'" class="btn" @click="createMu" :disabled="!form.mu.name">Создать</button>
          <button v-else-if="mod.kind==='mu-edit'" class="btn" @click="updateMu" :disabled="!form.mu.name">Сохранить</button>
          <button v-else-if="mod.kind==='mu-delete'" class="btn danger" @click="deleteMu">Удалить</button>

          <button v-else-if="mod.kind==='dep-create'" class="btn" @click="createDep" :disabled="!form.dep.name || !form.dep.management_id">Создать</button>
          <button v-else-if="mod.kind==='dep-edit'" class="btn" @click="updateDep" :disabled="!form.dep.name || !form.dep.management_id">Сохранить</button>
          <button v-else-if="mod.kind==='dep-delete'" class="btn danger" @click="deleteDep">Удалить</button>

          <button v-else-if="mod.kind==='staff-attach'" class="btn" @click="attachStaff" :disabled="!form.staffAttach.staff_id">Привязать</button>
          <button v-else-if="mod.kind==='staff-edit'" class="btn" @click="updateStaff">Сохранить</button>
          <button v-else-if="mod.kind==='staff-delete'" class="btn danger" @click="deleteStaff">Удалить</button>
        </footer>
      </div>
    </div>
  </div>
</template>

<style scoped>
.scene { --line:#e5e7eb; --panel:#fff; --ink:#0f141a; --muted:#6b7280; }
.head { margin-top: 80px; display:flex; justify-content:space-between; align-items:center; gap:12px; margin-bottom:12px; }
.tools { display:flex; gap:8px; align-items:center; }
.inp { height:36px; padding:0 10px; border:1px solid var(--line); border-radius:10px; background:transparent; color:var(--ink); }
.btn { height:34px; padding:0 12px; border:1px solid var(--line); border-radius:10px; background:transparent; color:var(--ink); font-weight:800; cursor:pointer; }
.btn.ghost { opacity:.85; }
.btn.danger { border-color:#fecaca; color:#b91c1c; }

.grid { display:grid; grid-template-columns: 1.2fr .8fr; gap:16px; }
@media (max-width: 1080px) { .grid { grid-template-columns: 1fr; } }

.left .mu { border:1px solid var(--line); border-radius:14px; padding:12px; margin-bottom:12px; background:linear-gradient(180deg, rgba(255,255,255,.04), rgba(255,255,255,0)); }
.mu-head { display:grid; grid-template-columns:1fr auto; gap:10px; align-items:center; }
.mu-actions, .dep-actions { display:flex; gap:6px; }

.dep { border:1px solid var(--line); border-radius:12px; padding:10px; margin-top:10px; }
.dep-head { display:grid; grid-template-columns:1fr auto; gap:8px; align-items:center; }
.dep-title { display:flex; gap:8px; align-items:center; }
.dot { width:8px; height:8px; border-radius:999px; background:#19c46d; }

.staff-list { list-style:none; margin:8px 0 0; padding:0; display:grid; gap:6px; }
.staff { padding:6px 8px; border:1px solid var(--line); border-radius:10px; cursor:pointer; }
.staff:hover { background:#f9fafb; }

.right .card { border:1px solid var(--line); border-radius:14px; padding:12px; background:var(--panel); }
.card-head { display:grid; grid-template-columns:1fr auto; gap:8px; align-items:start; }
.title h3 { margin:0; }
.sub { display:flex; gap:8px; align-items:center; }
.tag { border:1px solid var(--line); border-radius:999px; padding:0 8px; font-size:12px; }
.grid2 { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:8px; }
.kv { margin:4px 0; }
.block { margin-top:14px; }
.lines { list-style:none; margin:6px 0 0; padding:0; display:grid; gap:6px; }
.muted { color:var(--muted); }
.small { font-size:12px; }
.pad { padding:4px 0; }

.m-ov { position:fixed; inset:0; background:rgba(0,0,0,.45); display:grid; place-items:center; z-index:9999; padding:14px; }
.m-card { width:min(760px,96vw); background:var(--panel); border:1px solid var(--line); border-radius:16px; }
.m-head { display:grid; grid-template-columns:1fr auto; align-items:center; padding:12px 14px; border-bottom:1px solid var(--line); }
.m-title { margin:0; font-size:18px; }
.m-x { background:transparent; border:0; font-size:22px; color:#9aa1aa; cursor:pointer; }
.m-body { padding:12px 14px; display:grid; gap:12px; }
.m-foot { padding:12px 14px 16px; display:flex; gap:8px; justify-content:flex-end; }
.f-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
@media (max-width:640px){ .f-grid { grid-template-columns:1fr; } }
.error { color:#ef4444; margin:8px 0; }
.skeleton { border:1px dashed var(--line); border-radius:12px; padding:10px; }
.empty { border:1px dashed var(--line); border-radius:12px; padding:12px; text-align:center; }
</style>
