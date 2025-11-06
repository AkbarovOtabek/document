<template>
  <div class="modal">
    <div class="card">
      <header>
        <h3>Удалить сотрудника</h3>
        <button @click="$emit('close')">×</button>
      </header>

      <section class="form">
        <label>Сотрудник</label>
        <input v-model.trim="q" placeholder="Поиск по ФИО..." />
        <select v-model.number="selected">
          <option :value="s.id" v-for="s in filtered" :key="s.id">
            {{ s.fio || s.username }} — {{ s.position || "—" }}
          </option>
        </select>
      </section>

      <footer>
        <button @click="$emit('close')" class="ghost">Отмена</button>
        <button class="danger" :disabled="!selected || deleting" @click="remove">Удалить</button>
      </footer>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { API_BASE_URL } from "../../API";

export default {
  name: "DeleteStaffModal",
  props: { staff: Array },
  emits: ["close", "deleted"],
  data() {
    return { q: "", selected: null, deleting: false };
  },
  computed: {
    filtered() {
      const t = this.q.trim().toLowerCase();
      if (!t) return this.staff;
      return this.staff.filter((s) => (s.fio || s.username || "").toLowerCase().includes(t));
    },
    methods: {
      async remove() {
        if (!this.selected) return;
        if (!confirm("Удалить выбранного сотрудника?")) return;
        try {
          this.deleting = true;
          await axios.delete(`${API_BASE_URL}api/staff/users/${this.selected}/`);
          this.$emit("deleted");
        } catch (e) {
          alert("Ошибка при удалении: " + (e?.response?.data?.detail || e.message));
        } finally {
          this.deleting = false;
        }
      },
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
  width: 480px;
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