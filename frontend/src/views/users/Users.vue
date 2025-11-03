<template>
  <div class="scene">
    <!-- Загрузка -->
    <div v-if="loading" class="loader">Загрузка...</div>

    <!-- Основная доска -->
    <OrgCircleBoard
      v-else-if="centerData"
      :center="centerData"
      @open-modal="openPerson"
      @open-add="openAdd"
    />

    <!-- Модальное окно сотрудника -->
    <PersonModal
      v-if="selectedPerson"
      :person="selectedPerson"
      @close="selectedPerson = null"
      @edit="editPerson"
      @delete="deletePerson"
    />

    <!-- Модальное окно добавления -->
    <AddEntityModal
      v-if="addModal.show"
      :type="addModal.type"
      @close="addModal = { show: false, type: null }"
      @save="saveEntity"
    />
  </div>
</template>

<script>
import OrgCircleBoard from "./OrgCircleBoard.vue";
import PersonModal from "./PersonModal.vue";
import AddEntityModal from "./AddEntityModal.vue";
import axios from "axios";
import { API_BASE_URL } from "../../API";
export default {
  name: "Users",
  components: { OrgCircleBoard, PersonModal, AddEntityModal },

  data() {
    return {
      loading: false,
      error: "",
      centerData: null,
      selectedPerson: null,
      addModal: { show: false, type: null },
    };
  },

  async mounted() {
    await this.loadAll();
  },

  methods: {
    /** Универсальный способ получить id (если объект или число) */
    getId(val) {
      return typeof val === "object" && val ? val.id : val;
    },

    /** Загрузка всей структуры (центр → управления → отделы → сотрудники) */
    async loadAll() {
      try {
        this.loading = true;
        this.error = "";

        const [centers, managements, departments, staff] = await Promise.all([
          axios.get(`${API_BASE_URL}api/staff/centers/`),
          axios.get(`${API_BASE_URL}api/staff/management/`),
          axios.get(`${API_BASE_URL}api/staff/departments/`),
          axios.get(`${API_BASE_URL}api/staff/users/`),
        ]);

        // Универсальный метод — если DRF вернул results
        const getResults = (data) =>
          Array.isArray(data) ? data : data.results ? data.results : [];

        const centersData = getResults(centers.data);
        const managementsData = getResults(managements.data);
        const departmentsData = getResults(departments.data);
        const staffData = getResults(staff.data);

        if (!centersData.length) throw new Error("Центры не найдены");

        const center = centersData[0]; // пока берём первый центр
        const getId = this.getId;

        // === УПРАВЛЕНИЯ ===
        const managementList = managementsData
          .filter((m) => getId(m.center) === center.id)
          .map((m) => ({
            ...m,
            director: staffData.find(
              (s) => getId(s.management) === m.id && s.position === "deputy_director"
            ) || {
              fio: "—",
              position: "Директор управления",
            },
            departments: [],
          }));

        // === ОТДЕЛЫ ===
        departmentsData.forEach((dep) => {
          const m = managementList.find((x) => x.id === getId(dep.management));
          if (m) {
            const head = staffData.find(
              (s) => getId(s.department) === dep.id && s.position === "head_of_department"
            ) || { fio: "—", position: "Начальник отдела" };

            const employees = staffData.filter(
              (s) => getId(s.department) === dep.id && s.position !== "head_of_department"
            );

            m.departments.push({
              ...dep,
              head,
              staff: employees,
            });
          }
        });

        // === ЦЕНТР ===
        this.centerData = {
          id: center.id,
          name: center.name,
          director: staffData.find(
            (s) => s.position === "director" && (!s.management || !s.department)
          ) || {
            fio: "—",
            position: "Директор центра",
          },
          managements: managementList,
        };

        console.log("✅ Центр:", this.centerData);
      } catch (e) {
        console.error("Ошибка при загрузке структуры:", e);
        this.error = "Ошибка при загрузке структуры.";
      } finally {
        this.loading = false;
      }
    },

    /** Модалка информации о человеке */
    openPerson(p) {
      this.selectedPerson = p;
    },

    /** Модалка добавления управления/отдела/сотрудника */
    openAdd(payload) {
      this.addModal = { show: true, type: payload.type };
    },

    /** Редактирование */
    editPerson(p) {
      alert(`Редактировать ${p.fio}`);
    },

    /** Удаление */
    deletePerson(p) {
      if (confirm(`Удалить ${p.fio}?`)) alert("Удалён!");
      this.selectedPerson = null;
    },

    /** Добавление нового элемента */
    saveEntity(e) {
      alert(`Добавлен новый ${e.type}: ${e.name}`);
      this.addModal = { show: false, type: null };
    },
  },
};
</script>

<style scoped>
.scene {
  padding: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f1f5f9;
  min-height: 100vh;
}

.loader {
  font-weight: bold;
  color: #2563eb;
}

.error {
  color: #b91c1c;
  margin-top: 12px;
}
</style>
