<template>
  <div class="modal">
    <div class="modal-card">
      <header>
        <h3>Добавить {{ label }}</h3>
        <button @click="$emit('close')">×</button>
      </header>
      <section>
        <input v-model="form.name" placeholder="Название" />
        <input v-model="form.fio" placeholder="ФИО руководителя/сотрудника" />
        <input v-model="form.position" placeholder="Должность" />
      </section>
      <footer>
        <button @click="save">Добавить</button>
        <button @click="$emit('close')" class="ghost">Отмена</button>
      </footer>
    </div>
  </div>
</template>

<script>
export default {
  name: "AddEntityModal",
  props: {
    // show: Boolean,
    type: String,
    preset: Object,
  },
  emits: ["close", "save"],
  data() {
    return {
      form: { name: "", fio: "", position: "" },
    };
  },
  computed: {
    label() {
      return (
        {
          center: "центр",
          management: "управление",
          department: "отдел",
          staff: "сотрудника",
        }[this.type] || "элемент"
      );
    },
  },
  preset: {
    immediate: true,
    handler(p) {
      if (p) this.form = { ...this.form, ...p };
    },
  },
  methods: {
    save() {
      this.$emit("save", { ...this.form, type: this.type });
      this.form = { name: "", fio: "", position: "" };
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
.modal-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  width: 340px;
}
input {
  display: block;
  width: 100%;
  margin-top: 8px;
  padding: 8px;
  border-radius: 6px;
  border: 1px solid #ccc;
}
footer {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
button {
  border: 1px solid #ccc;
  border-radius: 6px;
  padding: 6px 10px;
  cursor: pointer;
}
button.ghost {
  background: #f3f4f6;
}
</style>