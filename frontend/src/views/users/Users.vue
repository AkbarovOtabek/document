<template>
  <div class="scene">
    <!-- TOP ACTION BAR -->
    <div class="actions-bar" v-if="!loading">
      <button @click="ui.addStruct = true">Добавить структуру</button>
      <button @click="ui.addStaff = true">Добавить сотрудника</button>
      <button class="danger" @click="ui.delStaff = true">Удалить сотрудника</button>
      <button class="danger" @click="ui.delUnit = true">Удалить отдел/упр./центр</button>
    </div>

    <div v-if="loading" class="loader">Загрузка...</div>

    <!-- Схема -->
    <OrgCircleBoard
      v-else-if="centerData"
      :center="centerData"
      :canEdit="true"
      @edit-entity="onEditEntity"
      @open-modal="openPerson"
    />

    <!-- Просмотр персоны (если используешь) -->
    <PersonModal
      v-if="selectedPerson"
      :person="selectedPerson"
      @close="selectedPerson = null"
      @edit="editPerson"
      @delete="deletePerson"
    />

    <!-- MODALS -->
    <AddStructureModal
      v-if="ui.addStruct"
      :centers="centers"
      :managements="managements"
      @close="ui.addStruct = false"
      @saved="onSaved"
    />
    <AddStaffModal
      v-if="ui.addStaff"
      :centers="centers"
      :managements="managements"
      :departments="departments"
      @close="ui.addStaff = false"
      @saved="onSaved"
    />
    <DeleteStaffModal
      v-if="ui.delStaff"
      :staff="staff"
      @close="ui.delStaff = false"
      @deleted="onSaved"
    />
    <DeleteUnitModal
      v-if="ui.delUnit"
      :centers="centers"
      :managements="managements"
      :departments="departments"
      @close="ui.delUnit = false"
      @deleted="onSaved"
    />
    <EditEntityModal
      v-if="edit.open"
      :open="edit.open"
      :level="edit.level"
      :entity="edit.entity"
      :ids="edit.ids"
      :centers="centers"
      :managements="managements"
      :departments="departments"
      @close="edit = { open:false, level:null, entity:null, ids:{} }"
      @saved="handleEdited"
    />
  </div>
</template>

<script>
import OrgCircleBoard from "./OrgCircleBoard.vue";
import EditEntityModal from "./EditEntityModal.vue";

import PersonModal from "./PersonModal.vue";
import AddStructureModal from "./AddStructureModal.vue";
import AddStaffModal from "./AddStaffModal.vue";
import DeleteStaffModal from "./DeleteStaffModal.vue";
import DeleteUnitModal from "./DeleteUnitModal.vue";

import axios from "axios";
import { API_BASE_URL } from "../../API";

export default {
  name: "Users",
  components: {
    OrgCircleBoard,
    PersonModal,
    AddStructureModal,
    AddStaffModal,
     EditEntityModal,
    DeleteStaffModal,
    DeleteUnitModal,
  },
  data() {
    return {
      loading: false,
      error: "",
      centerData: null,
      centers: [],
      managements: [],
      departments: [],
      staff: [],
      selectedPerson: null,
      ui: { addStruct: false, addStaff: false, delStaff: false, delUnit: false },
      edit: { open:false, level:null, entity:null, ids:{} },
    };
  },
  async mounted() {
    await this.loadAll();
  },
  methods: {
    getId(val) {
      return typeof val === "object" && val ? val.id : val;
    },

    async loadAll() {
      try {
        this.loading = true;
        const [centers, managements, departments, staff] = await Promise.all([
          axios.get(`${API_BASE_URL}api/staff/centers/`),
          axios.get(`${API_BASE_URL}api/staff/management/`),
          axios.get(`${API_BASE_URL}api/staff/departments/`),
          axios.get(`${API_BASE_URL}api/staff/users/`),
        ]);

        const pick = (d) => (Array.isArray(d.data) ? d.data : d.data?.results ?? []);
        this.centers = pick(centers);
        this.managements = pick(managements);
        this.departments = pick(departments);
        this.staff = pick(staff);

        if (!this.centers.length) throw new Error("Центры не найдены");

        const center = this.centers[0];
        const getId = this.getId;

        const managementList = this.managements
          .filter((m) => getId(m.center) === center.id)
          .map((m) => ({
            ...m,
            director:
              this.staff.find(
                (s) => getId(s.management) === m.id && s.position === "deputy_director"
              ) || { fio: "—", position: "Директор управления" },
            departments: [],
          }));

        this.departments.forEach((dep) => {
          const m = managementList.find((x) => x.id === getId(dep.management));
          if (m) {
            const head =
              this.staff.find(
                (s) => getId(s.department) === dep.id && s.position === "head_of_department"
              ) || { fio: "—", position: "Начальник отдела" };
            const employees = this.staff.filter(
              (s) => getId(s.department) === dep.id && s.position !== "head_of_department"
            );
            m.departments.push({ ...dep, head, staff: employees });
          }
        });

        this.centerData = {
          id: center.id,
          name: center.name,
          director:
            this.staff.find(
              (s) => s.position === "director" && (!s.management || !s.department)
            ) || { fio: "—", position: "Директор центра" },
          managements: managementList,
        };
      } catch (e) {
        console.error(e);
        this.error = "Ошибка при загрузке структуры.";
      } finally {
        this.loading = false;
      }
    },

    onSaved() {
      this.ui = { addStruct: false, addStaff: false, delStaff: false, delUnit: false };
      this.loadAll();
    },

    openPerson(p) {
      this.selectedPerson = p;
    },
    editPerson(p) {
      alert(`Редактировать ${p.fio}`);
    },
    deletePerson(p) {
      if (confirm(`Удалить ${p.fio}?`)) alert("Удалён (демо)");
      this.selectedPerson = null;
    },
    
    // обработчик клика по «Редактировать» из OrgCircleBoard
    onEditEntity({ level, entity, ids, ctx }) {
      this.edit = { open:true, level, entity, ids: ids || {} };
    },
    async handleEdited() {
      this.edit = { open:false, level:null, entity:null, ids:{} };
      await this.loadAll();
    },
  },
};
</script>

<style scoped>
.scene {
  padding: 20px;
  background: #f1f5f9;
  min-height: 100vh;
  padding-top: 80px;
}
.loader {
  font-weight: bold;
  color: #2563eb;
}

.actions-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 14px;
}
.actions-bar > button {
  border: 1px solid #cbd5e1;
  background: #fff;
  border-radius: 8px;
  padding: 8px 12px;
  cursor: pointer;
}
.actions-bar > button.danger {
  border-color: #fecaca;
  color: #b91c1c;
}
</style>
