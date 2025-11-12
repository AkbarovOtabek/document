<template>
  <div class="modal" v-if="open" @click.self="$emit('close')">
    <div class="panel">
      <div class="head">
        <h3>{{ langRU ? 'Добавить структуру' : 'Tuzilma qo‘shish' }}</h3>
        <button class="x" @click="$emit('close')">✕</button>
      </div>

      <form @submit.prevent="submit">
        <div class="row">
          <label>Название</label>
          <input v-model.trim="form.name" type="text" required placeholder="Например: Отдел ИБ" />
        </div>

        <div class="row">
          <label>Тип</label>
          <select v-model="form.type" required>
            <option value="center">Центр</option>
            <option value="manage">Управление</option>
            <option value="dept">Отдел</option>
            <option value="sector">Сектор/Группа</option>
            <option value="other">Иное</option>
          </select>
        </div>

        <div class="row">
          <label>Родитель</label>
          <select v-model="form.parentId">
            <option :value="null">— Без родителя (корневой) —</option>
            <option v-for="u in units" :key="u.id" :value="u.id">
              {{ ' '.repeat(u.depth*2) + u.name }}
            </option>
          </select>
        </div>

        <div class="row check">
          <label><input type="checkbox" v-model="form.addHead" /> Добавить руководителя</label>
        </div>

        <div v-if="form.addHead" class="head-grid">
          <div class="row">
            <label>ФИО</label>
            <input v-model.trim="form.head.full_name" type="text" required />
          </div>
          <div class="row">
            <label>Должность</label>
            <input v-model.trim="form.head.position" type="text" placeholder="Руководитель" />
          </div>
          <div class="row">
            <label>Телефон</label>
            <input v-model.trim="form.head.phone" type="text" />
          </div>
          <div class="row">
            <label>Email</label>
            <input v-model.trim="form.head.email" type="email" />
          </div>
          <div class="row check">
            <label><input type="checkbox" v-model="form.head.is_director" /> Директор</label>
          </div>
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
  name: "AddUnitModal",
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
        name: "",
        type: "dept",
        parentId: null,
        addHead: false,
        head: {
          full_name: "",
          position: "Руководитель",
          phone: "",
          email: "",
          is_director: false,
        },
      },
    };
  },
  methods: {
    submit() {
      if (!this.form.name || !this.form.type) return;
      if (this.form.addHead && !this.form.head.full_name) return;
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

.head-grid { border: 1px dashed #d1d5db; border-radius: 12px; padding: 10px; margin-top: 8px; }

.actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 16px; }
.btn { padding: 8px 14px; border-radius: 10px; border: 1px solid transparent; cursor: pointer; font-weight: 700; }
.btn.ghost { background: #f3f4f6; }
.btn.primary { background: #2563eb; color: #fff; }
</style>
