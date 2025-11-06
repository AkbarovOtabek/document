<template>
  <div class="modal">
    <div class="card">
      <header>
        <h3>Добавить структуру</h3>
        <button @click="$emit('close')">×</button>
      </header>

      <section class="form">
        <label>Тип</label>
        <select v-model="form.type">
          <option value="center">Центр</option>
          <option value="management">Управление</option>
          <option value="department">Отдел</option>
        </select>

        <template v-if="form.type === 'management'">
          <label>Центр</label>
          <select v-model.number="form.center">
            <option :value="c.id" v-for="c in centers" :key="c.id">{{ c.name }}</option>
          </select>
        </template>

        <template v-if="form.type === 'department'">
          <label>Управление</label>
          <select v-model.number="form.management">
            <option v-for="m in centersFlatManagements" :key="m.id" :value="m.id">
              {{ m.name }} ({{ centerName(m.center) }})
            </option>
          </select>
        </template>

        <label>Название</label>
        <input v-model.trim="form.name" placeholder="Название" />

        <label class="row">
          <input type="checkbox" v-model="form.addDirector" />
          <span>Добавить директора</span>
        </label>

        <div v-if="form.addDirector" class="grid2">
          <div>
            <label>ФИО директора</label>
            <input v-model.trim="form.dirFio" placeholder="ФИО" />
          </div>
          <div>
            <label>Должность</label>
            <input :value="directorPosition" disabled />
          </div>
        </div>
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
  name: "AddStructureModal",
  props: {
    centers: { type: Array, default: () => [] },
    managements: { type: Array, default: () => [] },
  },
  emits: ["close", "saved"],
  data() {
    return {
      saving: false,
      form: {
        type: "management", // центр | управление | отдел
        center: null,
        management: null,
        name: "",
        addDirector: true,
        dirFio: "",
      },
    };
  },
  computed: {
    centersFlatManagements() {
      return this.managements || [];
    },
    directorPosition() {
      return this.form.type === "center"
        ? "director"
        : this.form.type === "management"
        ? "deputy_director"
        : "head_of_department";
    },
  },
  methods: {
    centerName(id) {
      const c = this.centers.find((x) => x.id === (x.id?.id ?? id) || x.id === id);
      return c?.name || "—";
    },
    async save() {
      try {
        this.saving = true;
        const t = this.form.type;

        // 1) создаём структуру
        if (t === "center") {
          await axios.post(`${API_BASE_URL}api/staff/centers/`, { name: this.form.name });
        } else if (t === "management") {
          if (!this.form.center) this.form.center = this.centers[0]?.id;
          await axios.post(`${API_BASE_URL}api/staff/management/`, {
            name: this.form.name,
            center: this.form.center,
          });
        } else {
          if (!this.form.management) throw new Error("Укажите управление");
          await axios.post(`${API_BASE_URL}api/staff/departments/`, {
            name: this.form.name,
            management: this.form.management,
          });
        }

        // 2) при необходимости — создаём директора
        if (this.form.addDirector && this.form.dirFio.trim()) {
          const payload = {
            fio: this.form.dirFio.trim(),
            position: this.directorPosition,
          };
          if (t === "management") payload.management = this.form.center ? undefined : undefined;
          // для центра директор без management/department
          if (t === "management") payload.management = this.form.center ?? null; // если нужно поправить, можно достать id свежесозданного, но чаще управление создаём под известным центром
          if (t === "department") payload.department = this.form.management;

          await axios.post(`${API_BASE_URL}api/staff/users/`, payload);
        }

        this.$emit("saved");
      } catch (e) {
        alert("Ошибка при добавлении: " + (e?.response?.data?.detail || e.message));
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
.grid2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.row {
  display: flex;
  gap: 8px;
  align-items: center;
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