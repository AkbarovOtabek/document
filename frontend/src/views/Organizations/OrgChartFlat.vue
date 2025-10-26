<script>
import OrgChartBoard from "./OrgChartBoard.vue";

function deepClone(v) {
  try {
    return JSON.parse(JSON.stringify(v));
  } catch {
    return Array.isArray(v) ? [...v] : v;
  }
}
let _uid = 100000;

export default {
  name: "OrgChartFlat",
  components: { OrgChartBoard },
  props: {
    tree: { type: Array, required: true, default: () => [] },
  },
  data() {
    return {
      localTree: deepClone(this.tree),

      // правая панель
      selections: [],
      query: "",

      // модалка
      showModal: false,
      modalType: null, // 'root' | 'unit' | 'employee'
      targetNode: null,
      form: { name: "", type: "department", fio: "", position: "", phone: "", email: "" },
    };
  },
  watch: {
    tree: {
      deep: true,
      handler(v) {
        this.localTree = deepClone(v || []);
      },
    },
  },
  computed: {
    hasBranches() {
      return Array.isArray(this.localTree) && this.localTree.length > 0;
    },
    palette() {
      return [{ wire: "#d84c3f" }, { wire: "#2962ff" }];
    },
    filtered() {
      if (!this.query) return this.selections;
      const q = this.query.toLowerCase();
      return this.selections.filter((s) => {
        const unitText = `${s.unit?.name || ""} ${s.unit?.type || ""} ${
          s.path || ""
        }`.toLowerCase();
        const empsText = (s.employees || [])
          .map((e) =>
            `${e.fio || e.name || ""} ${e.position || ""} ${e.phone || ""} ${
              e.email || ""
            }`.toLowerCase()
          )
          .join(" ");
        return unitText.includes(q) || empsText.includes(q);
      });
    },
    modalTitle() {
      if (this.modalType === "root") return "Новое корневое подразделение";
      if (this.modalType === "unit") return "Новое дочернее подразделение";
      if (this.modalType === "employee") return "Новый сотрудник";
      return "";
    },
    modalSubmitText() {
      return this.modalType === "employee" ? "Добавить сотрудника" : "Создать";
    },
  },
  mounted() {
    window.addEventListener("keydown", this.onKeydown);
  },
  beforeUnmount() {
    window.removeEventListener("keydown", this.onKeydown);
  },
  methods: {
    // ==== правая панель ====
    idxByUnit(u) {
      const id = u?.id ?? u?.name;
      return this.selections.findIndex((s) => (s.unit?.id ?? s.unit?.name) === id);
    },
    onPick(item) {
      if (item.kind !== "unit") return;
      const u = item.payload || {};
      const i = this.idxByUnit(u);
      const emps = Array.isArray(u.employees) ? u.employees.slice() : [];
      if (i === -1) this.selections.push({ unit: u, employees: emps, path: item.path });
      else {
        this.selections[i].employees = emps;
        this.selections[i].path = item.path;
      }
    },
    removeUnit(i) {
      this.selections.splice(i, 1);
    },
    clearAll() {
      this.selections = [];
      this.query = "";
    },
    tel(v) {
      return v ? `tel:${String(v).replace(/\s+/g, "")}` : "#";
    },
    mail(v) {
      return v ? `mailto:${v}` : "#";
    },

    // ==== открытие модалок ====
    openRootModal() {
      this.modalType = "root";
      this.form = { name: "", type: "department", fio: "", position: "", phone: "", email: "" };
      this.targetNode = null;
      this.showModal = true;
    },
    createChild(node) {
      this.modalType = "unit";
      this.form = { name: "", type: "department", fio: "", position: "", phone: "", email: "" };
      this.targetNode = node;
      this.showModal = true;
    },
    createEmployee(node) {
      this.modalType = "employee";
      this.form = { fio: "", position: "", phone: "", email: "", name: "", type: "department" };
      this.targetNode = node;
      this.showModal = true;
    },

    // ==== submit/close модалки ====
    submitModal() {
      if (this.modalType === "root") {
        const name = (this.form.name || "").trim();
        if (!name) return;
        this.localTree.push({
          id: _uid++,
          name,
          type: this.form.type || "department",
          order: 0,
          children: [],
          employees: [],
        });
      } else if (this.modalType === "unit" && this.targetNode) {
        const name = (this.form.name || "").trim();
        if (!name) return;
        if (!Array.isArray(this.targetNode.children)) this.targetNode.children = [];
        this.targetNode.children.push({
          id: _uid++,
          name,
          type: this.form.type || "department",
          order: 0,
          children: [],
          employees: [],
        });
      } else if (this.modalType === "employee" && this.targetNode) {
        const fio = (this.form.fio || "").trim();
        if (!fio) return;
        if (!Array.isArray(this.targetNode.employees)) this.targetNode.employees = [];
        this.targetNode.employees.push({
          id: _uid++,
          fio,
          position: this.form.position || "",
          phone: this.form.phone || "",
          email: this.form.email || "",
        });
      }
      this.closeModal();
    },
    closeModal() {
      this.showModal = false;
      this.targetNode = null;
    },

    // ==== UX модалки (фон/ESC) ====
    onModalBg(e) {
      if (e.target === e.currentTarget) this.closeModal();
    },
    onKeydown(e) {
      if (e.key === "Escape") this.closeModal();
    },
  },
};
</script>

<template>
  <div class="wrap">
    <!-- ЛЕВАЯ: структура -->
    <section class="left">
      <div class="toolbar">
        <button class="plus" title="Добавить корневое подразделение" @click="openRootModal">
          ＋
        </button>
        <span class="muted small">Создать корневое подразделение</span>
      </div>

      <div v-if="hasBranches" class="bus"></div>
      <div v-if="hasBranches" class="branches">
        <div v-for="(root, i) in localTree" :key="root.id || root.name || i" class="branch">
          <div class="stem"></div>
          <OrgChartBoard
            :root="root"
            :color="palette[i % palette.length].wire"
            @pick="onPick"
            @create-child="createChild"
            @create-emp="createEmployee"
          />
        </div>
      </div>
      <div v-else class="muted empty">Структура не задана.</div>
    </section>

    <!-- ПРАВАЯ: выбранные -->
    <aside class="right">
      <div class="panel-head">
        <h3>Выбранные</h3>
        <div class="tools">
          <input v-model="query" type="search" class="search" placeholder="Поиск…" />
          <button class="btn" @click="clearAll" :disabled="!selections.length">Очистить</button>
        </div>
      </div>

      <div v-if="!selections.length" class="empty muted">
        Нажмите на подразделение слева — карточка и его сотрудники появятся здесь.
      </div>

      <div v-else class="units">
        <div v-for="(s, i) in filtered" :key="s.unit?.id || i" class="unit-card">
          <div class="unit-head">
            <div>
              <div class="unit-title">
                <strong>{{ s.unit?.name || "Подразделение" }}</strong>
                <span v-if="s.unit?.type" class="tag">{{ s.unit.type }}</span>
              </div>
              <div v-if="s.path" class="path">{{ s.path }}</div>
            </div>
            <button class="x" @click="removeUnit(i)" title="Убрать подразделение">×</button>
          </div>

          <div v-if="s.employees?.length" class="emp-list">
            <div v-for="(e, j) in s.employees" :key="e.id || j" class="emp-row">
              <div class="avatar">{{ (e.fio || e.name || "👤").slice(0, 1) }}</div>
              <div class="emp-body">
                <div class="emp-title">
                  <b>{{ e.fio || e.name }}</b
                  ><span v-if="e.position" class="muted"> · {{ e.position }}</span>
                </div>
                <div class="emp-contacts">
                  <a v-if="e.phone" :href="tel(e.phone)" class="chip">☎ {{ e.phone }}</a>
                  <a v-if="e.email" :href="mail(e.email)" class="chip">✉ {{ e.email }}</a>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="muted small">Сотрудников нет для отображения.</div>
        </div>
      </div>
    </aside>

    <!-- ==== МОДАЛКА (inline, без runtime-compiler) ==== -->
    <div v-if="showModal" class="m-ov" @click="onModalBg">
      <div class="m-card" role="dialog" aria-modal="true">
        <header class="m-head">
          <h3 class="m-title">{{ modalTitle }}</h3>
          <button class="m-x" @click="closeModal" aria-label="Закрыть">×</button>
        </header>

        <div class="m-body">
          <!-- Подразделение/Корень -->
          <template v-if="modalType === 'unit' || modalType === 'root'">
            <div class="f-grid">
              <label class="f-l">
                <span>Название</span>
                <input v-model="form.name" class="inp" placeholder="Например: Отдел продаж" />
              </label>
              <label class="f-l">
                <span>Тип</span>
                <select v-model="form.type" class="inp">
                  <option value="management">management</option>
                  <option value="department">department</option>
                  <option value="section">section</option>
                  <option value="other">other</option>
                </select>
              </label>
            </div>
          </template>

          <!-- Сотрудник -->
          <template v-else-if="modalType === 'employee'">
            <div class="f-grid">
              <label class="f-l">
                <span>ФИО</span>
                <input v-model="form.fio" class="inp" placeholder="Иванов Иван" />
              </label>
              <label class="f-l">
                <span>Должность</span>
                <input v-model="form.position" class="inp" placeholder="Менеджер по продажам" />
              </label>
            </div>
            <div class="f-grid">
              <label class="f-l">
                <span>Телефон</span>
                <input v-model="form.phone" class="inp" placeholder="+998 .." />
              </label>
              <label class="f-l">
                <span>Email</span>
                <input
                  v-model="form.email"
                  type="email"
                  class="inp"
                  placeholder="name@company.com"
                />
              </label>
            </div>
          </template>
        </div>

        <footer class="m-foot">
          <button class="btn ghost" @click="closeModal">Отмена</button>
          <button class="btn" @click="submitModal">{{ modalSubmitText }}</button>
        </footer>
      </div>
    </div>
  </div>
</template>

<style scoped>
.wrap {
  display: grid;
  grid-template-columns: 1.6fr 0.9fr;
  gap: 18px;
}
@media (max-width: 1200px) {
  .wrap {
    grid-template-columns: 1fr;
  }
  .right {
    order: -1;
  }
}

/* Панель */
.toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}
.plus {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  border: 1px solid var(--line);
  background: var(--panel);
  font-size: 20px;
  font-weight: 900;
  cursor: pointer;
}

.left {
  position: relative;
  overflow: visible;
}
.bus {
  height: 2px;
  background: #c9cfda;
  margin: 6px 0 0;
}
.branches {
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: max-content;
  justify-content: center;
  align-items: start;
  gap: 30px;
  padding-top: 10px;
  overflow: visible;
}
.branch {
  display: grid;
  justify-items: center;
  align-items: start;
  overflow: visible;
  position: relative;
}
.branch .stem {
  width: 2px;
  height: 12px;
  background: #c9cfda;
  margin-bottom: 2px;
}

/* Правая панель */
.right {
  position: sticky;
  top: 12px;
  align-self: start;
  border: 1px solid var(--line);
  border-radius: 16px;
  background: var(--panel);
  padding: 12px;
}
.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}
.tools {
  display: flex;
  gap: 8px;
  align-items: center;
}
.search {
  height: 34px;
  padding: 0 10px;
  border-radius: 10px;
  border: 1px solid var(--line);
  background: transparent;
  color: var(--ink);
}
.btn {
  height: 34px;
  padding: 0 12px;
  border-radius: 10px;
  border: 1px solid var(--line);
  background: transparent;
  color: var(--ink);
  font-weight: 800;
}
.btn.ghost {
  opacity: 0.85;
}

.units {
  display: grid;
  gap: 12px;
}
.unit-card {
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 12px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.03), rgba(255, 255, 255, 0));
  box-shadow: 0 10px 20px rgba(19, 31, 55, 0.05);
}
.unit-head {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
  align-items: start;
}
.unit-title {
  display: flex;
  gap: 8px;
  align-items: baseline;
  flex-wrap: wrap;
}
.tag {
  font-size: 11px;
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 2px 8px;
  color: #7b8497;
}
.path {
  margin-top: 4px;
  font-size: 12px;
  color: #7b8497;
}
.small {
  font-size: 12px;
}
.emp-list {
  display: grid;
  gap: 10px;
  margin-top: 10px;
}
.emp-row {
  display: grid;
  grid-template-columns: 28px 1fr;
  gap: 10px;
  align-items: start;
}
.avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-weight: 900;
  background: rgba(25, 196, 109, 0.16);
  color: #0d8f56;
  border: 1px solid #cfe8db;
}
.emp-title {
  font-size: 14px;
}
.emp-contacts {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 4px;
}
.chip {
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 2px 8px;
  font-size: 12px;
  text-decoration: none;
  color: inherit;
}

.empty {
  padding: 10px;
  border: 1px dashed var(--line);
  border-radius: 12px;
  color: #7b8497;
}

/* ==== Модал ==== */
.m-ov {
  position: fixed;
  inset: 0;
  background: rgba(4, 6, 10, 0.42);
  display: grid;
  place-items: center;
  z-index: 9999;
  padding: 14px;
}
.m-card {
  width: min(560px, 96vw);
  background: var(--panel);
  color: var(--ink);
  border: 1px solid var(--line);
  border-radius: 16px;
  box-shadow: 0 30px 70px rgba(0, 0, 0, 0.25);
}
.m-head {
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  padding: 14px 16px;
  border-bottom: 1px solid var(--line);
}
.m-title {
  margin: 0;
  font-size: 18px;
}
.m-x {
  background: transparent;
  border: 0;
  font-size: 22px;
  cursor: pointer;
  color: var(--muted);
}
.m-body {
  padding: 14px 16px;
  display: grid;
  gap: 12px;
}
.m-foot {
  padding: 12px 16px 16px;
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}
.f-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
@media (max-width: 640px) {
  .f-grid {
    grid-template-columns: 1fr;
  }
}
.f-l {
  display: grid;
  gap: 6px;
}
.f-l > span {
  font-size: 12px;
  color: var(--muted);
}
.inp {
  height: 36px;
  padding: 0 10px;
  border-radius: 10px;
  border: 1px solid var(--line);
  background: transparent;
  color: var(--ink);
}
</style>
