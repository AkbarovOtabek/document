<!-- src/components/modals/AddStaffModal.vue -->
<template>
  <transition name="fade">
    <div class="modal" @click.self="$emit('close')">
      <transition name="zoom">
        <div class="card" role="dialog" aria-modal="true">
          <header class="card__head">
            <div>
              <h3 class="card__title">Добавить сотрудника</h3>
              <p class="card__sub">Заполните данные и при необходимости назначьте роль/подразделение.</p>
            </div>
            <button class="icon-btn" @click="$emit('close')" aria-label="Закрыть">×</button>
          </header>

          <section class="card__body">
            <!-- User -->
            <div class="field">
              <label class="label">User</label>
              <select v-model.number="form.user" class="input">
                <option :value="u.id" v-for="u in users" :key="`u-${u.id}`">
                  {{ userLabel(u) }}
                </option>
              </select>
            </div>

            <!-- ФИО (по админке отдельно) -->
            <div class="grid3">
              <div class="field">
                <label class="label">First name</label>
                <input class="input" v-model.trim="form.first_name" />
              </div>
              <div class="field">
                <label class="label">Second name</label>
                <input class="input" v-model.trim="form.second_name" />
              </div>
              <div class="field">
                <label class="label">Last name</label>
                <input class="input" v-model.trim="form.last_name" />
              </div>
            </div>

            <div class="grid3">
              <div class="field">
                <label class="label">Lotus</label>
                <input class="input" v-model.trim="form.lotus" />
              </div>
              <div class="field">
                <label class="label">Work email</label>
                <input class="input" v-model.trim="form.work_email" type="email" />
              </div>
              <div class="field">
                <label class="label">Work phone</label>
                <input class="input" v-model.trim="form.work_phone" />
              </div>
            </div>

            <!-- Привязка: Центр / Управление / Отдел -->
            <div class="field">
              <label class="label">Center</label>
              <select v-model.number="bind.center" class="input">
                <option :value="null">—</option>
                <option :value="c.id" v-for="c in centers" :key="`c-${c.id}`">{{ c.name }}</option>
              </select>
            </div>

            <div class="field">
              <label class="label">Position</label>
              <select v-model="form.position" class="input">
                <option value="director">Директор</option>
                <option value="deputy_director">Заместитель директора (по управлению)</option>
                <option value="head_of_department">Начальник отдела</option>
                <option value="chief_expert">Главный эксперт</option>
                <option value="leading_expert">Ведущий эксперт</option>
                <option value="first_level_expert">Эксперт первого уровня</option>
                <option value="employee">Сотрудник</option>
                <option value="clerical">Делопроизводитель</option>
              </select>
            </div>

            <!-- Управление зависит от выбранного центра -->
            <div class="field">
              <label class="label">Management</label>
              <select v-model.number="bind.management" class="input">
                <option :value="null">—</option>
                <option
                  v-for="m in managementsByCenter"
                  :key="`m-${m.id}`"
                  :value="m.id"
                >
                  {{ m.name }}
                </option>
              </select>
            </div>

            <div class="field">
              <label class="label">Department</label>
              <select v-model.number="bind.department" class="input">
                <option :value="null">—</option>
                <option
                  v-for="d in departmentsByMu"
                  :key="`d-${d.id}`"
                  :value="d.id"
                >
                  {{ d.name }}
                </option>
              </select>
            </div>

            <!-- Если руководящая должность — показать блок назначения, чем руководит -->
            <div v-if="isLeader" class="subsection">
              <div class="grid2">
                <div class="field" v-if="form.position === 'director'">
                  <label class="label">Руководит центром</label>
                  <select v-model.number="lead.center" class="input">
                    <option :value="null">— выберите центр —</option>
                    <option :value="c.id" v-for="c in centers" :key="`lc-${c.id}`">{{ c.name }}</option>
                  </select>
                </div>

                <div class="field" v-if="form.position === 'deputy_director'">
                  <label class="label">Руководит управлением</label>
                  <select v-model.number="lead.management" class="input">
                    <option :value="null">— выберите управление —</option>
                    <option
                      v-for="m in managementsByCenterForLead"
                      :key="`lm-${m.id}`"
                      :value="m.id"
                    >{{ m.name }}</option>
                  </select>
                </div>

                <div class="field" v-if="form.position === 'head_of_department'">
                  <label class="label">Руководит отделом</label>
                  <select v-model.number="lead.department" class="input">
                    <option :value="null">— выберите отдел —</option>
                    <option
                      v-for="d in departmentsByMuForLead"
                      :key="`ld-${d.id}`"
                      :value="d.id"
                    >{{ d.name }}</option>
                  </select>
                </div>
              </div>
              <p class="help">
                При сохранении сотрудник автоматически будет назначен руководителем указанного подразделения.
              </p>
            </div>

            <!-- Роль -->
            <div class="field">
              <label class="label">Role</label>
              <select v-model="form.role" class="input">
                <option value="curator">Куратор</option>
                <option value="none">Без роли</option>
              </select>
            </div>

            <!-- Если Куратор — выбор типа организаций и мультиселект организаций -->
            <div v-if="form.role === 'curator'" class="subsection">
              <div class="field">
                <label class="label">Тип организаций</label>
                <select v-model.number="curator.category" class="input">
                  <option :value="null">— выберите тип —</option>
                  <option
                    :value="t.id"
                    v-for="t in orgTypes"
                    :key="`t-${t.id}`"
                  >{{ t.name }}</option>
                </select>
              </div>

              <div class="field" v-if="curator.category">
                <label class="label">Организации (можно несколько)</label>
                <select v-model="curator.organizations" class="input" multiple size="6">
                  <option
                    v-for="o in orgsByType"
                    :key="`o-${o.id}`"
                    :value="o.id"
                  >
                    {{ o.name }}
                  </option>
                </select>
              </div>
              <p class="help">
                Выбранные организации будут привязаны куратору.
              </p>
            </div>
          </section>

          <footer class="card__foot">
            <button class="btn ghost" @click="$emit('close')">Отмена</button>
            <button class="btn primary" :disabled="saving" @click="save">
              <span v-if="saving" class="spinner"></span>
              {{ saving ? "Сохраняю…" : "Добавить" }}
            </button>
          </footer>
        </div>
      </transition>
    </div>
  </transition>
</template>

<script>
import axios from "axios";
import { API_BASE_URL } from "@/API.js";

export default {
  name: "AddStaffModal",
  props: {
    centers: { type: Array, default: () => [] },
    managements: { type: Array, default: () => [] },
    departments: { type: Array, default: () => [] },
  },
  emits: ["close", "saved"],
  data() {
    return {
      saving: false,

      users: [],
      orgTypes: [],
      orgs: [],

      form: {
        user: null,
        first_name: "",
        second_name: "",
        last_name: "",
        lotus: "",
        work_email: "",
        work_phone: "",
        position: "employee",
        role: "none",
      },

      bind: {
        center: null,
        management: null,
        department: null,
      },

      lead: {
        center: null,
        management: null,
        department: null,
      },

      curator: {
        category: null,
        organizations: [],
      },
    };
  },
  computed: {
    managementsByCenter() {
      const c = this.bind.center;
      return this.managements.filter(
        (m) => (m.center?.id ?? m.center) === c
      );
    },
    departmentsByMu() {
      const mu = this.bind.management;
      return this.departments.filter(
        (d) => (d.management?.id ?? d.management) === mu
      );
    },

    // для блока «Руководит …»
    managementsByCenterForLead() {
      const c = this.lead.center ?? this.bind.center;
      return this.managements.filter((m) => (m.center?.id ?? m.center) === c);
    },
    departmentsByMuForLead() {
      const mu = this.lead.management ?? this.bind.management;
      return this.departments.filter((d) => (d.management?.id ?? d.management) === mu);
    },

    isLeader() {
      return ["director", "deputy_director", "head_of_department"].includes(this.form.position);
    },

    orgsByType() {
      const cat = this.curator.category;
      return this.orgs.filter((o) => (o.category?.id ?? o.category) === cat);
    },
  },
  mounted() {
    this.loadUsers();
    this.loadOrgTypes();
    this.loadOrgs();
    // дефолтные привязки
    this.bind.center = this.centers[0]?.id ?? null;
    const firstMu = this.managements.find((m) => (m.center?.id ?? m.center) === this.bind.center);
    this.bind.management = firstMu?.id ?? null;
    const firstDep = this.departments.find((d) => (d.management?.id ?? d.management) === this.bind.management);
    this.bind.department = firstDep?.id ?? null;
  },
  methods: {
    userLabel(u) {
      const base = u.username || u.email || `user#${u.id}`;
      const fio = [u.last_name, u.first_name, u.second_name].filter(Boolean).join(" ");
      return fio ? `${fio} — ${base}` : base;
    },
    async loadUsers() {
      try {
        const { data } = await axios.get(`${API_BASE_URL}api/staff/users/`, { params: { page_size: 500 }});
        this.users = Array.isArray(data?.results) ? data.results : Array.isArray(data) ? data : [];
      } catch (e) { /* no-op */ }
    },
    async loadOrgTypes() {
      try {
        const { data } = await axios.get(`${API_BASE_URL}api/categories/list/`);
        this.orgTypes = Array.isArray(data?.results) ? data.results : Array.isArray(data) ? data : [];
      } catch (e) { /* no-op */ }
    },
    async loadOrgs() {
      try {
        const { data } = await axios.get(`${API_BASE_URL}api/organizations/list/`, { params: { page_size: 1000 }});
        this.orgs = Array.isArray(data?.results) ? data.results : Array.isArray(data) ? data : [];
      } catch (e) { /* no-op */ }
    },

    async save() {
      try {
        this.saving = true;

        // 1) создаём/обновляем сотрудника
        const payload = {
          user: this.form.user,
          first_name: this.form.first_name || null,
          second_name: this.form.second_name || null,
          last_name: this.form.last_name || null,
          lotus: this.form.lotus || null,
          work_email: this.form.work_email || null,
          work_phone: this.form.work_phone || null,
          position: this.form.position,
          center: this.bind.center || null,
          management: this.bind.management || null,
          department: this.bind.department || null,
          role: this.form.role === "curator" ? "Куратор" : null,
        };

        // POST /api/staff/users/
        const { data: created } = await axios.post(`${API_BASE_URL}api/staff/users/`, payload);

        // 2) если руководящая должность — назначить руководство
        if (this.isLeader) {
          const leadPayload = {
            leadership: this.form.position, // серверу можно маппить на своём конце
            center: this.lead.center || null,
            management: this.lead.management || null,
            department: this.lead.department || null,
          };
          // Если ничего не выбрано в lead — пробуем взять из привязок
          if (this.form.position === "director" && !leadPayload.center) leadPayload.center = this.bind.center;
          if (this.form.position === "deputy_director" && !leadPayload.management) leadPayload.management = this.bind.management;
          if (this.form.position === "head_of_department" && !leadPayload.department) leadPayload.department = this.bind.department;

          // Если на бэке отдельной ручки нет — можно PATCH к тому же пользователю:
          await axios.patch(`${API_BASE_URL}api/staff/users/${created.id}/`, leadPayload);
        }

        // 3) если куратор — привязать тип и организации
        if (this.form.role === "curator" && (this.curator.category || this.curator.organizations.length)) {
          const curatorPayload = {
            curator_category: this.curator.category,
            curator_organizations: this.curator.organizations,
          };
          await axios.patch(`${API_BASE_URL}api/staff/users/${created.id}/`, curatorPayload);
        }

        this.$emit("saved");
      } catch (e) {
        const msg = e?.response?.data?.detail || e?.message || "Неизвестная ошибка";
        alert("Ошибка при сохранении: " + msg);
      } finally {
        this.saving = false;
      }
    },
  },
};
</script>

<style scoped>
/* Анимации */
.fade-enter-active,.fade-leave-active{transition:opacity .18s ease}
.fade-enter-from,.fade-leave-to{opacity:0}
.zoom-enter-active,.zoom-leave-active{transition:transform .18s ease,opacity .18s ease}
.zoom-enter-from,.zoom-leave-to{transform:translateY(6px) scale(.98);opacity:0}

/* Backdrop: светлый белый блюр, чтобы фон читался */
.modal{
  position:fixed; inset:0; display:grid; place-items:center; padding:24px; z-index:9999;
  background:rgba(255,255,255,0.35);
  backdrop-filter:blur(10px) saturate(120%);
}

/* Карточка */
.card{
  width:760px; max-width:100%;
  background:rgba(255,255,255,0.92);
  color:#0f141a;
  border:1px solid rgba(15,20,26,0.06);
  border-radius:18px;
  box-shadow:0 18px 42px rgba(15,20,26,.18);
  overflow:clip;
}
.card__head,.card__foot{padding:14px 18px}
.card__body{padding:10px 18px 12px; display:grid; gap:12px}
.card__head{display:flex; align-items:flex-start; justify-content:space-between; gap:12px; border-bottom:1px solid rgba(15,20,26,0.06)}
.card__title{margin:0; font-size:20px; font-weight:900}
.card__sub{margin:4px 0 0; font-size:12px; color:#6b7280}
.card__foot{display:flex; justify-content:flex-end; gap:10px; border-top:1px solid rgba(15,20,26,0.06)}

/* Формы */
.field{display:grid; gap:6px}
.label{font-size:12px; font-weight:700; color:#6b7280}
.input{
  width:100%; height:38px; border:1px solid #e6e8ee; border-radius:12px; padding:0 12px;
  background:#fff; color:#0f141a; font-size:14px;
  transition:border-color .15s, box-shadow .15s;
}
.input:focus{outline:none; border-color:#22c55e; box-shadow:0 0 0 4px rgba(34,197,94,.18)}
.input[multiple]{height:auto; min-height:120px; padding:10px; border-radius:12px}

/* Блоки */
.subsection{
  border:1px dashed #e6e8ee; border-radius:12px; padding:12px; background:rgba(15,20,26,.02);
  display:grid; gap:10px;
}
.help{margin:-2px 2px 0; font-size:12px; color:#6b7280}

/* Сетки */
.grid2{display:grid; grid-template-columns:1fr 1fr; gap:12px}
.grid3{display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px}
@media (max-width:860px){.grid2,.grid3{grid-template-columns:1fr}}

/* Кнопки */
.btn{
  height:38px; padding:0 14px; border-radius:12px; border:1px solid #e6e8ee; background:#fff; color:#0f141a;
  font-weight:800; display:inline-flex; align-items:center; gap:8px; cursor:pointer;
  transition:transform .06s, box-shadow .2s, background .2s;
}
.btn:hover{transform:translateY(-1px); box-shadow:0 10px 22px rgba(0,0,0,.08)}
.btn.primary{background:#22c55e; border-color:#22c55e; color:#062a17}
.btn.primary:disabled{opacity:.6; cursor:not-allowed; transform:none; box-shadow:none}
.btn.ghost{background:#f3f4f6}

.icon-btn{
  width:34px; height:34px; border-radius:12px; border:1px solid #e6e8ee; background:#fff;
  color:#0f141a; font-size:18px; line-height:1; display:grid; place-items:center;
  transition:transform .06s, box-shadow .2s;
}
.icon-btn:hover{transform:translateY(-1px); box-shadow:0 10px 22px rgba(0,0,0,.08)}

.spinner{width:16px; height:16px; border-radius:50%; border:2px solid rgba(255,255,255,.65); border-top-color:#fff; animation:spin .7s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
</style>
