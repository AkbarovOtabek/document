<template>
  <div class="modal">
    <div class="card">
      <header>
        <h3>Добавить сотрудника</h3>
        <button @click="$emit('close')">×</button>
      </header>

      <section class="form">
        <label>ФИО</label>
        <input v-model.trim="form.fio" placeholder="ФИО" />

        <label>Должность</label>
        <input v-model.trim="form.position" placeholder="Должность" />

        <label>Центр</label>
        <select v-model.number="sel.center">
          <option :value="c.id" v-for="c in centers" :key="c.id">{{ c.name }}</option>
        </select>

        <label>Управление</label>
        <select v-model.number="sel.management">
          <option v-for="m in managementsByCenter" :key="m.id" :value="m.id">{{ m.name }}</option>
        </select>

        <label>Отдел</label>
        <select v-model.number="sel.department">
          <option v-for="d in departmentsByMu" :key="d.id" :value="d.id">{{ d.name }}</option>
        </select>
      </section>

      <footer>
        <button @click="$emit('close')" class="ghost">Отмена</button>
        <button @click="save" :disabled="saving">Добавить</button>
      </footer>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { API_BASE_URL } from "../../API";

export default {
  name: "AddStaffModal",
  props: {
    centers: Array,
    managements: Array,
    departments: Array,
  },
  emits: ["close", "saved"],
  data() {
    return {
      saving: false,
      form: { fio: "", position: "" },
      sel: { center: null, management: null, department: null },
    };
  },
  computed: {
    managementsByCenter() {
      return this.managements.filter(
        (m) => m.center === this.sel.center || m.center?.id === this.sel.center
      );
    },
    departmentsByMu() {
      return this.departments.filter(
        (d) => d.management === this.sel.management || d.management?.id === this.sel.management
      );
    },
  },
  mounted() {
    // дефолты
    this.sel.center = this.centers[0]?.id ?? null;
    const firstMu = this.managements.find((m) => (m.center?.id ?? m.center) === this.sel.center);
    this.sel.management = firstMu?.id ?? null;
    const firstDep = this.departments.find(
      (d) => (d.management?.id ?? d.management) === this.sel.management
    );
    this.sel.department = firstDep?.id ?? null;
  },
  methods: {
    async save() {
      try {
        this.saving = true;
        const payload = {
          fio: this.form.fio.trim(),
          position: this.form.position.trim(),
          management: this.sel.management || null,
          department: this.sel.department || null,
        };
        await axios.post(`${API_BASE_URL}api/staff/users/`, payload);
        this.$emit("saved");
      } catch (e) {
        alert("Ошибка при добавлении сотрудника: " + (e?.response?.data?.detail || e.message));
      } finally {
        this.saving = false;
      }
    },
  },
};
</script>

<style scoped>
.modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: grid;
  place-items: center;
  z-index: 9999;
}
.card {
  background: #fff;
  border-radius: 12px;
  width: 520px;
  padding: 14px;
}
header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.form {
  margin-top: 10px;
  display: grid;
  gap: 8px;
}
input,
select {
  width: 100%;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 8px;
}
footer {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
button {
  border: 1px solid #cbd5e1;
  background: #fff;
  border-radius: 8px;
  padding: 8px 12px;
  cursor: pointer;
}
button.ghost {
  background: #f3f4f6;
}
</style>