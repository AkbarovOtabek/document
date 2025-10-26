<script>
import OrgChartBoard from "./OrgChartBoard.vue";

export default {
  name: "OrgChartFlat",
  components: { OrgChartBoard },
  props: {
    tree: { type: Array, required: true, default: () => [] }, // org.units_tree
  },
  data() {
    return {
      // [{ unit, employees:[], path }]
      selections: [],
      query: "",
    };
  },
  computed: {
    hasBranches() {
      return Array.isArray(this.tree) && this.tree.length > 0;
    },
    palette() {
      return [{ wire: "#d84c3f" }, { wire: "#2962ff" }];
    }, // красная/синяя
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
  },
  methods: {
    // индекс по unit.id (или name как запасной ключ)
    idxByUnit(u) {
      const id = u?.id ?? u?.name;
      return this.selections.findIndex((s) => (s.unit?.id ?? s.unit?.name) === id);
    },
    onPick(item) {
      // кликом всегда приходит подразделение; его сотрудников показываем справа
      if (item.kind === "unit") {
        const u = item.payload || {};
        const i = this.idxByUnit(u);
        const emps = Array.isArray(u.employees) ? u.employees.slice() : [];
        if (i === -1) {
          this.selections.push({ unit: u, employees: emps, path: item.path });
        } else {
          // обновим список сотрудников (если вдруг изменился на бэке)
          this.selections[i].employees = emps;
          this.selections[i].path = item.path;
        }
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
  },
};
</script>

<template>
  <div class="wrap">
    <!-- ЛЕВАЯ: структура -->
    <section class="left">
      <div v-if="hasBranches" class="bus"></div>
      <div v-if="hasBranches" class="branches">
        <div v-for="(root, i) in tree" :key="root.id || root.name || i" class="branch">
          <div class="stem"></div>
          <OrgChartBoard :root="root" :color="palette[i % palette.length].wire" @pick="onPick" />
        </div>
      </div>
      <div v-else class="muted empty">Структура не задана.</div>
    </section>

    <!-- ПРАВАЯ: выбранные подразделения + их сотрудники -->
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
                  <b>{{ e.fio || e.name }}</b>
                  <span v-if="e.position" class="muted"> · {{ e.position }}</span>
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
  </div>
</template>

<style scoped>
.wrap {
  display: grid;
  grid-template-columns: 2.3fr 0.9fr;
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

/* ЛЕВАЯ */
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
}
.branch .stem {
  width: 2px;
  height: 12px;
  background: #c9cfda;
  margin-bottom: 2px;
}

/* ПРАВАЯ */
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
.x {
  background: transparent;
  border: 0;
  font-size: 20px;
  color: var(--muted);
  cursor: pointer;
}
.x:hover {
  color: var(--ink);
}

.empty {
  padding: 10px;
  border: 1px dashed var(--line);
  border-radius: 12px;
  color: #7b8497;
}

/* ...остальные стили без изменений... */

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
  height: 14px;
  background: #b7bfcc;
  margin-bottom: 2px;
  position: relative;
}
/* маленькая «шапка» сверху ствола — Т-узел на общей шине */
.branch .stem::before {
  content: "";
  position: absolute;
  top: -2px;
  left: 50%;
  transform: translateX(-50%);
  width: 16px;
  height: 0;
  border-top: 2px solid #b7bfcc;
}
</style>
