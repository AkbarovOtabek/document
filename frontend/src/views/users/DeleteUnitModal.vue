<template>
  <div class="modal">
    <div class="card">
      <header>
        <h3>Удалить отдел / управление / центр</h3>
        <button @click="$emit('close')">×</button>
      </header>

      <section class="form">
        <label>Тип</label>
        <select v-model="form.type">
          <option value="department">Отдел</option>
          <option value="management">Управление</option>
          <option value="center">Центр</option>
        </select>

        <template v-if="form.type === 'department'">
          <label>Отдел</label>
          <select v-model.number="form.id">
            <option v-for="d in departments" :key="d.id" :value="d.id">
              {{ d.name }} ({{ muName(d.management) }})
            </option>
          </select>
        </template>

        <template v-if="form.type === 'management'">
          <label>Управление</label>
          <select v-model.number="form.id">
            <option v-for="m in managements" :key="m.id" :value="m.id">
              {{ m.name }} ({{ centerName(m.center) }})
            </option>
          </select>
        </template>

        <template v-if="form.type === 'center'">
          <label>Центр</label>
          <select v-model.number="form.id">
            <option v-for="c in centers" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </template>
      </section>

      <footer>
        <button @click="$emit('close')" class="ghost">Отмена</button>
        <button class="danger" :disabled="!form.id || deleting" @click="remove">Удалить</button>
      </footer>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { API_BASE_URL } from "../../API";

export default {
  name: "DeleteUnitModal",
  props: {
    centers: Array,
    managements: Array,
    departments: Array,
  },
  emits: ["close", "deleted"],
  data() {
    return { deleting: false, form: { type: "department", id: null } };
  },
  methods: {
    centerName(id) {
      const c = this.centers.find((x) => x.id === id || x.id?.id === id);
      return c?.name || "—";
    },
    muName(id) {
      const m = this.managements.find((x) => x.id === id || x.id?.id === id);
      return m?.name || "—";
    },
    async remove() {
      if (!this.form.id) return;
      const t = this.form.type;
      const url =
        t === "department"
          ? `${API_BASE_URL}api/staff/departments/${this.form.id}/`
          : t === "management"
          ? `${API_BASE_URL}api/staff/management/${this.form.id}/`
          : `${API_BASE_URL}api/staff/centers/${this.form.id}/`;

      if (!confirm("Вы уверены, что хотите удалить выбранный элемент? Это действие необратимо."))
        return;
      try {
        this.deleting = true;
        await axios.delete(url);
        this.$emit("deleted");
      } catch (e) {
        alert("Ошибка при удалении: " + (e?.response?.data?.detail || e.message));
      } finally {
        this.deleting = false;
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
button.danger {
  border-color: #fecaca;
  color: #b91c1c;
}
button.ghost {
  background: #f3f4f6;
}
</style>