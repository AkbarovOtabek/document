<template>
  <div class="modal" v-if="person">
    <div class="modal-card">
      <header>
        <h3>{{ person.fio }}</h3>
        <button @click="$emit('close')">×</button>
      </header>
      <section>
        <p><b>Должность:</b> {{ person.position }}</p>
        <p><b>Роль:</b> {{ person.role || "—" }}</p>
        <p><b>Телефон:</b> {{ person.work_phone || "—" }}</p>
        <p><b>Email:</b> {{ person.work_email || "—" }}</p>
        <p><b>Lotus:</b> {{ person.lotus || "—" }}</p>
      </section>
      <footer>
        <button @click="$emit('edit', person)">Изменить</button>
        <button @click="$emit('delete', person)" class="danger">Удалить</button>
        <button @click="$emit('close')" class="ghost">Закрыть</button>
      </footer>
    </div>
  </div>
</template>

<script>
export default {
  name: "PersonModal",
  props: { person: Object },
};
</script>

<style scoped>
.modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: grid;
  place-items: center;
  z-index: 999;
}
.modal-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  width: 360px;
}
header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
button {
  border: 1px solid #ccc;
  border-radius: 6px;
  padding: 4px 8px;
  margin-top: 10px;
  cursor: pointer;
}
button.danger {
  background: #fee2e2;
  color: #b91c1c;
}
button.ghost {
  background: #f3f4f6;
}
</style>
