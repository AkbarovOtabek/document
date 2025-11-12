<template>
  <div class="modal" v-if="open" @click.self="$emit('close')">
    <div class="panel">
      <div class="head">
        <h3>{{ langRU ? 'Добавить сотрудника' : 'Xodim qo‘shish' }}</h3>
        <button class="x" @click="$emit('close')">✕</button>
      </div>

      <form @submit.prevent="submit">
        <div class="row">
          <label>Подразделение</label>
          <select v-model="form.unitId" required>
            <option disabled value="">— Выберите подразделение —</option>
            <option v-for="u in units" :key="u.id" :value="u.id">
              {{ ' '.repeat(u.depth*2) + u.name }}
            </option>
          </select>
        </div>

        <div class="row">
          <label>ФИО</label>
          <input v-model.trim="form.full_name" type="text" required />
        </div>

        <div class="row">
          <label>Должность</label>
          <input v-model.trim="form.position" type="text" />
        </div>

        <div class="row">
          <label>Телефон</label>
          <input v-model.trim="form.phone" type="text" />
        </div>

        <div class="row">
          <label>Email</label>
          <input v-model.trim="form.email" type="email" />
        </div>

        <div class="row check">
          <label><input type="checkbox" v-model="form.is_head" /> Руководитель</label>
        </div>
        <div class="row check">
          <label><input type="checkbox" v-model="form.is_director" /> Директор</label>
        </div>

        <div class="actions">
          <button type="button" class="btn ghost" @click="$emit('close')">Отмена</button>
          <button type="submit" class="btn primary">Создать</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: "AddEmployeeModal",
  props: {
    open: Boolean,
    units: { type: Array, default: () => [] }, // [{id,name,depth}]
    langRU: { type: Boolean, default: true },
    isDark: { type: Boolean, default: false },
  },
  emits: ["close", "submit"],
  data() {
    return {
      form: {
        unitId: "",
        full_name: "",
        position: "",
        phone: "",
        email: "",
        is_head: false,
        is_director: false,
      },
    };
  },
  methods: {
    submit() {
      if (!this.form.unitId || !this.form.full_name) return;
      this.$emit("submit", JSON.parse(JSON.stringify(this.form)));
    },
  },
};
</script>

<style scoped>
.modal { position: fixed; inset: 0; background: rgba(0,0,0,.35); display: grid; place-items: center; z-index: 2000; }
.panel { width: 560px; background: #fff; border-radius: 16px; box-shadow: 0 20px 60px rgba(0,0,0,.25); padding: 16px; }
.head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.head h3 { margin: 0; font-size: 18px; }
.x { border: none; background: transparent; font-size: 18px; cursor: pointer; }

.row { display: grid; gap: 6px; margin-top: 10px; }
.row.check { align-items: center; }
label { font-size: 13px; opacity: .8; }
input, select { height: 36px; padding: 6px 10px; border-radius: 10px; border: 1px solid #e5e7eb; outline: none; }
input:focus, select:focus { border-color: #93c5fd; box-shadow: 0 0 0 3px #93c5fd33; }

.actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 16px; }
.btn { padding: 8px 14px; border-radius: 10px; border: 1px solid transparent; cursor: pointer; font-weight: 700; }
.btn.ghost { background: #f3f4f6; }
.btn.primary { background: #2563eb; color: #fff; }
</style>
