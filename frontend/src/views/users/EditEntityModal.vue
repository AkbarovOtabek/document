<template>
  <div class="overlay" @mousedown.self="$emit('close')">
    <div class="modal" @mousedown.stop>
      <div class="head">
        <h3>Редактировать — {{ titleByLevel }}</h3>
        <button class="close" @click="$emit('close')">✕</button>
      </div>

      <form class="body" @submit.prevent="save">
        <!-- CENTER / MANAGEMENT / DEPARTMENT -->
        <template v-if="level !== 'staff'">
          <label class="row">
            <span>Название</span>
            <input v-model="form.name" required placeholder="Название"/>
          </label>

          <label class="row" v-if="level !== 'department'">
            <span>Директор (ID пользователя, опц.)</span>
            <input v-model="form.director_id" type="number" placeholder="ID директора"/>
          </label>

          <label class="row" v-else>
            <span>Начальник отдела (ID пользователя, опц.)</span>
            <input v-model="form.head_id" type="number" placeholder="ID начальника"/>
          </label>

          <label class="row" v-if="level === 'management'">
            <span>Центр</span>
            <select v-model="form.center">
              <option :value="getId(c)" v-for="c in centers" :key="'c'+getId(c)">{{ c.name }}</option>
            </select>
          </label>

          <label class="row" v-if="level === 'department'">
            <span>Управление</span>
            <select v-model="form.management">
              <option :value="getId(m)" v-for="m in managements" :key="'m'+getId(m)">{{ m.name }}</option>
            </select>
          </label>
        </template>

        <!-- STAFF -->
        <template v-else>
          <label class="row">
            <span>ФИО</span>
            <input v-model="form.fio" placeholder="ФИО"/>
          </label>

          <label class="row">
            <span>Должность</span>
            <select v-model="form.position">
              <option value="director">Директор</option>
              <option value="deputy_director">Заместитель директора</option>
              <option value="head_of_department">Начальник отдела</option>
              <option value="chief_expert">Главный эксперт</option>
              <option value="lead_expert">Ведущий эксперт</option>
              <option value="expert_l1">Эксперт первого уровня</option>
              <option value="employee">Сотрудник</option>
              <option value="records_clerk">Делопроизводитель</option>
            </select>
          </label>

          <label class="row">
            <span>Email</span>
            <input v-model="form.email" type="email" placeholder="email@domain"/>
          </label>

          <label class="row">
            <span>Телефон</span>
            <input v-model="form.phone" placeholder="+998..." />
          </label>

          <label class="row">
            <span>Lotus</span>
            <input v-model="form.lotus" placeholder="Lotus"/>
          </label>

          <div class="grid2">
            <label class="row">
              <span>Управление</span>
              <select v-model="form.management">
                <option :value="getId(m)" v-for="m in managements" :key="'mm'+getId(m)">{{ m.name }}</option>
              </select>
            </label>
            <label class="row">
              <span>Отдел</span>
              <select v-model="form.department">
                <option :value="getId(d)" v-for="d in departments" :key="'dd'+getId(d)">{{ d.name }}</option>
              </select>
            </label>
          </div>
        </template>

        <div class="footer">
          <button type="button" class="ghost" @click="$emit('close')">Отмена</button>
          <button type="submit" :disabled="saving">
            {{ saving ? 'Сохраняю…' : 'Сохранить' }}
          </button>
        </div>

        <p v-if="err" class="err">{{ err }}</p>
      </form>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { API_BASE_URL } from "../../API";

export default {
  name: "EditEntityModal",
  props: {
    open: { type: Boolean, default: false },
    level: { type: String, required: true }, // center | management | department | staff
    entity: { type: Object, required: true },
    ids: { type: Object, default: () => ({}) },
    centers: { type: Array, default: () => [] },
    managements: { type: Array, default: () => [] },
    departments: { type: Array, default: () => [] },
  },
  emits: ["close", "saved"],
  data() {
    return { form: this.makeInitial(), saving: false, err: "" };
  },
  watch: {
    entity: { handler() { this.form = this.makeInitial(); }, deep: true },
    level()  { this.form = this.makeInitial(); },
  },
  computed: {
    titleByLevel() {
      return { center:"Центр", management:"Управление", department:"Отдел", staff:"Сотрудник" }[this.level] || this.level;
    },
  },
  methods: {
    getId(v){ return typeof v === "object" && v ? v.id : v; },

    makeInitial() {
      const e = this.entity || {};
      if (this.level === "center") {
        return { name: e.name || "", director_id: this.getId(e.director) || e.director_id || "" };
      }
      if (this.level === "management") {
        return {
          name: e.name || "",
          center: this.getId(e.center) || this.ids.centerId || "",
          director_id: this.getId(e.director) || e.director_id || "",
        };
      }
      if (this.level === "department") {
        return {
          name: e.name || "",
          management: this.getId(e.management) || this.ids.managementId || "",
          head_id: this.getId(e.head) || e.head_id || "",
        };
      }
      // staff
      return {
        fio: e.fio || "",
        position: e.position || "employee",
        email: e.email || e.work_email || "",
        phone: e.phone || e.work_phone || "",
        lotus: e.lotus || "",
        management: this.getId(e.management) || this.ids.managementId || "",
        department: this.getId(e.department) || this.ids.departmentId || "",
      };
    },

    endpoint() {
      const id =
        this.level === "center" ? this.getId(this.entity.id) :
        this.level === "management" ? this.getId(this.entity.id) :
        this.level === "department" ? this.getId(this.entity.id) :
        this.level === "staff" ? (this.entity.id ?? this.entity.user_id ?? this.entity.person_id) :
        null;

      const map = {
        center:     (i) => `${API_BASE_URL}api/staff/centers/${i}/`,
        management: (i) => `${API_BASE_URL}api/staff/management/${i}/`,
        department: (i) => `${API_BASE_URL}api/staff/departments/${i}/`,
        staff:      (i) => `${API_BASE_URL}api/staff/users/${i}/`,
      };
      return id ? map[this.level](id) : null;
    },

    body() {
      // Оставляем только заполненные поля
      const clean = {};
      for (const [k,v] of Object.entries(this.form)) {
        if (v !== "" && v !== null && v !== undefined) clean[k] = v;
      }
      return clean;
    },

    async save() {
      this.err = "";
      const url = this.endpoint();
      if (!url) { this.err = "Не удалось определить эндпоинт."; return; }

      this.saving = true;
      try {
        await axios.patch(url, this.body(), { withCredentials: true });
        this.$emit("saved");
      } catch (e) {
        this.err = e?.response?.data?.detail || e?.message || "Ошибка сохранения";
      } finally {
        this.saving = false;
      }
    },
  },
};
</script>

<style scoped>
.overlay{
  position:fixed; inset:0; background:rgba(15,23,42,.55);
  display:grid; place-items:center; z-index:2000;
}
.modal{
  width:min(680px, 94vw); max-height:90vh; overflow:auto;
  background:#fff; border-radius:16px; box-shadow:0 25px 70px rgba(0,0,0,.35);
}
.head{
  display:flex; align-items:center; justify-content:space-between;
  padding:14px 16px; border-bottom:1px solid #e5e7eb;
}
.head h3{ margin:0; font-size:16px; font-weight:800; }
.head .close{ border:none; background:transparent; font-size:18px; padding:4px 6px; cursor:pointer; }

.body{ padding:14px 16px; display:grid; gap:12px; }
.row{ display:grid; grid-template-columns:160px 1fr; gap:10px; align-items:center; }
.row>span{ font-size:13px; color:#6b7280; }
.row input, .row select{
  width:100%; border:1px solid #d1d5db; border-radius:10px; padding:8px 10px; outline:none;
}
.grid2{ display:grid; grid-template-columns:1fr 1fr; gap:12px; }

.footer{
  display:flex; justify-content:flex-end; gap:10px; padding-top:6px;
}
.footer .ghost{
  background:#f3f4f6; border:1px solid #e5e7eb; color:#111827; border-radius:10px; padding:8px 12px;
}
.footer button[type="submit"]{
  background:#2563eb; color:#fff; border:1px solid #1d4ed8; border-radius:10px; padding:8px 14px; cursor:pointer;
}
.err{ color:#b91c1c; margin:0; }
</style>
