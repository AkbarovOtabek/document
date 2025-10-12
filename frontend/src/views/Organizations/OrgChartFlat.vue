<script>
import OrgChartBoard from "./OrgChartBoard.vue";

export default {
  name: "OrgChartFlat",
  components: { OrgChartBoard },
  props: {
    tree: { type: Array, default: () => [] },
    showCounters: { type: Boolean, default: true },
  },
  data() {
    return {
      levels: [],
      edges: [],
      sideStack: [],
      positions: {},
      lines: [],
      _els: new Map(), // <— тут будем хранить dom-элементы узлов по id
    };
  },
  mounted() {
    this.rebuild();
    window.addEventListener("resize", this.remeasure);
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.remeasure);
  },
  watch: {
    tree: {
      deep: true,
      handler() {
        this.rebuild();
      },
    },
  },
  methods: {
    levelGap(lvl) {
      if (lvl === 0) return "480px";
      if (lvl === 1) return "120px";
      return "40px";
    },
    typeInfo(t) {
      const map = {
        directorate: { label: "Дирекция", color: "var(--c-dir)" },
        management: { label: "Управление", color: "var(--c-mng)" },
        department: { label: "Отдел", color: "var(--c-dep)" },
        section: { label: "Сектор", color: "var(--c-sec)" },
        other: { label: "Подразделение", color: "var(--c-oth)" },
      };
      return map[t] || map.other;
    },
    empCount(n) {
      return n?.employees?.length || 0;
    },
    kidsCount(n) {
      return n?.children?.length || 0;
    },

    // собираем ссылки на dom узлы
    register(id, el) {
      if (el) this._els.set(id, el);
    },

    rebuild() {
      const roots = Array.isArray(this.tree) ? this.tree : [];
      const levels = [],
        edges = [],
        q = [];
      roots.forEach((r) => q.push({ node: r, level: 0, parentId: null }));
      while (q.length) {
        const { node, level, parentId } = q.shift();
        (levels[level] ||= []).push(node);
        if (parentId != null) edges.push({ pId: parentId, cId: node.id });
        (node.children || []).forEach((ch) =>
          q.push({ node: ch, level: level + 1, parentId: node.id })
        );
      }
      this.levels = levels;
      this.edges = edges;
      this.$nextTick(this.remeasure);
    },

    remeasure() {
      const wrap = this.$refs.wrap;
      if (!wrap) return;
      const wrapRect = wrap.getBoundingClientRect();
      const positions = {};
      this._els.forEach((el, id) => {
        const r = el.getBoundingClientRect();
        positions[id] = {
          x: r.left - wrapRect.left,
          y: r.top - wrapRect.top,
          w: r.width,
          h: r.height,
        };
      });
      const lines = [];
      for (const e of this.edges) {
        const p = positions[e.pId],
          c = positions[e.cId];
        if (!p || !c) continue;
        lines.push({ x1: p.x + p.w / 2, y1: p.y + p.h, x2: c.x + c.w / 2, y2: c.y });
      }
      this.positions = positions;
      this.lines = lines;
    },

    // правая панель
    clickNode({ node, level }) {
      this.sideStack = this.sideStack.filter((it) => it.level <= level);
      this.sideStack.push({ node, level });
    },
    clearAll() {
      this.sideStack = [];
    },
    removeAt(i) {
      this.sideStack.splice(i, 1);
    },

    initials(s) {
      return (
        String(s || "")
          .trim()
          .split(/\s+/)
          .map((w) => w[0])
          .join("")
          .slice(0, 2)
          .toUpperCase() || "👤"
      );
    },
    fio(e) {
      return e?.fio || e?.full_name || "";
    },
    phone(e) {
      return e?.phone || e?.work_phone || "";
    },
    email(e) {
      return e?.email || e?.work_email || "";
    },
    position(e) {
      return e?.position_display || e?.position_title || e?.position || "";
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
  <div class="flat-layout">
    <div class="flat-left" ref="wrap">
      <svg class="wires" :width="'100%'" :height="'100%'" preserveAspectRatio="none">
        <g stroke="var(--line)" stroke-width="1">
          <line v-for="(L, i) in lines" :key="i" :x1="L.x1" :y1="L.y1" :x2="L.x2" :y2="L.y2" />
        </g>
      </svg>

      <!-- БЫЛ блок levels; теперь — компонент -->
      <OrgChartBoard
        :levels="levels"
        :show-counters="showCounters"
        :level-gap="levelGap"
        :type-info="typeInfo"
        :register="register"
        @pick="clickNode"
      />
    </div>

    <aside class="flat-right">
      <div class="right-head">
        <div class="muted" v-if="!sideStack.length">Нажмите на блок в схеме</div>
        <button v-else class="btn clear" @click="clearAll">Очистить</button>
      </div>

      <div
        v-for="(it, idx) in sideStack"
        :key="(it.node?.id ?? idx) + '-' + it.level"
        class="side-card"
      >
        <div class="side-line">
          <div class="side-type" :style="{ background: typeInfo(it.node.type).color }">
            {{ typeInfo(it.node.type).label }}
          </div>
          <button class="close" @click="removeAt(idx)">✕</button>
        </div>
        <div class="side-title">{{ it.node.name }}</div>
        <div class="side-meta">
          <span v-if="empCount(it.node)">{{ empCount(it.node) }} сотрудн.</span>
          <span v-if="kidsCount(it.node)"> · {{ kidsCount(it.node) }} подраздел.</span>
        </div>

        <div class="emp-list" v-if="empCount(it.node)">
          <div v-for="(e, i) in it.node.employees" :key="e.id || i" class="emp-item">
            <div class="emp-avatar">{{ initials(fio(e)) }}</div>
            <div class="emp-main">
              <div class="emp-name">
                {{ fio(e) }} <span v-if="e.is_head" class="chip">Руководитель</span>
              </div>
              <div class="emp-sub">{{ position(e) || "—" }}</div>
              <div class="emp-links">
                <a v-if="phone(e)" :href="tel(phone(e))">☎ {{ phone(e) }}</a>
                <a v-if="email(e)" :href="mail(email(e))">✉ {{ email(e) }}</a>
              </div>
            </div>
          </div>
        </div>
        <div class="muted" v-else>Сотрудники не указаны.</div>
      </div>
    </aside>
  </div>
</template>

<style scoped>
:root {
  --c-dir: #8b5cf6;
  --c-mng: #22c55e;
  --c-dep: #06b6d4;
  --c-sec: #f59e0b;
  --c-oth: #9ca3af;
}
.flat-layout {
  --line: #e6e8ee;
  --panel: #fff;
  --ink: #0f141a;
  display: grid;
  grid-template-columns: minmax(680px, 1fr) 360px;
  gap: 16px;
  align-items: start;
}
@media (max-width: 1100px) {
  .flat-layout {
    grid-template-columns: 1fr;
  }
}

/* левая зона */
.flat-left {
  position: relative;
  padding: 24px 24px 32px;
  overflow: auto;
  min-height: 420px;
  border-radius: 16px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.65), rgba(255, 255, 255, 0.35));
  border: 1px solid var(--line);
  box-shadow: 0 18px 42px rgba(0, 0, 0, 0.08);
}
.wires {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

/* строки уровней */
.level {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin: 28px 0;
}

/* узел (без собственного бордера и фона — только «плашка») */
.node {
  width: 240px;
  min-height: 76px;
  padding: 12px 14px 14px;
  border-radius: 14px;
  background: #fff;
  box-shadow: 0 10px 22px rgba(0, 0, 0, 0.06);
  transition: transform 0.18s ease, box-shadow 0.18s ease, filter 0.18s ease;
  cursor: pointer;
}
.node:hover {
  transform: translateY(-2px);
  box-shadow: 0 16px 30px rgba(0, 0, 0, 0.1);
  filter: saturate(1.04);
}
.node-type {
  display: inline-flex;
  align-items: center;
  height: 20px;
  padding: 0 8px;
  margin-bottom: 6px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 800;
  color: #fff;
  background: var(--box, #9ca3af);
}
.node-title {
  font-weight: 900;
  line-height: 1.2;
  font-size: 16px;
}
.node-meta {
  margin-top: 6px;
  font-size: 12px;
  color: #6b7280;
}

/* правая колонка */
.flat-right {
  position: sticky;
  top: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.right-head {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  min-height: 28px;
}
.btn.clear {
  height: 30px;
  padding: 0 10px;
  border-radius: 10px;
  border: 1px solid var(--line);
  background: #fff;
  cursor: pointer;
}
.side-card {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.7), rgba(255, 255, 255, 0.45));
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 14px;
  box-shadow: 0 18px 42px rgba(0, 0, 0, 0.08);
}
.side-line {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}
.side-type {
  color: #fff;
  font-size: 11px;
  font-weight: 900;
  height: 22px;
  padding: 0 10px;
  border-radius: 999px;
}
.close {
  width: 28px;
  height: 28px;
  border-radius: 10px;
  border: 1px solid var(--line);
  background: #fff;
  cursor: pointer;
}
.side-title {
  margin: 8px 0 2px;
  font-size: 18px;
  font-weight: 900;
}
.side-meta {
  color: #6b7280;
  font-size: 12px;
  margin-bottom: 8px;
}

.emp-list {
  display: grid;
  gap: 10px;
}
.emp-item {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 10px;
  align-items: flex-start;
  padding: 10px;
  border: 1px solid var(--line);
  border-radius: 14px;
  background: #fff;
  box-shadow: 0 10px 22px rgba(0, 0, 0, 0.06);
}
.emp-avatar {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  background: #effaf3;
  color: #0ea95b;
  font-weight: 900;
  border: 1px solid #d9f3e4;
}
.emp-name {
  font-weight: 900;
}
.chip {
  margin-left: 6px;
  height: 18px;
  font-size: 10px;
  padding: 0 8px;
  border-radius: 999px;
  background: rgba(25, 196, 109, 0.16);
  color: #0ea95b;
  border: 1px solid rgba(25, 196, 109, 0.24);
}
.emp-sub {
  font-size: 13px;
  color: #6b7280;
  margin-top: 2px;
}
.emp-links {
  display: flex;
  gap: 12px;
  margin-top: 4px;
  flex-wrap: wrap;
}
a {
  color: #0f141a;
  text-decoration: none;
}
.muted {
  color: #6b7280;
}
.level {
  display: flex;
  justify-content: center;
  gap: var(--gap, 40px); /* раньше было: gap:40px */
  margin: 28px 0;
}
</style>
