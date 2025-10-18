<script>
export default {
  name: "OrgChartBoard",
  emits: ["select"],
  props: {
    root: { type: Object, required: true }, // bitta root daraxti
    showCounters: { type: Boolean, default: true },
  },
  data() {
    return {
      levels: [], // [[nodes...], ...]
      edges: [], // [{pId, cId}]
      positions: new Map(), // id -> {x,y,w,h}
      paths: [], // SVG path'lar (ota→bola)
      parentStems: [], // ota → bus (V)
      busSegments: [], // chap→o‘ng gorizontal chiziq (H)
      childStems: [],
      diagPaths: [],
      wireColor: "#c8ced9",
      rafId: null, // resize debouncing
    };
  },
  mounted() {
    this.rebuild();
    window.addEventListener("resize", this.remeasureDebounced);
    const v = getComputedStyle(this.$el).getPropertyValue("--wire").trim();
    if (v) this.wireColor = v;
    setTimeout(this.remeasureDebounced, 0);
    setTimeout(this.remeasureDebounced, 200);
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.remeasureDebounced);
    if (this.rafId) cancelAnimationFrame(this.rafId);
  },
  watch: {
    root: {
      deep: true,
      handler() {
        this.rebuild();
      },
    },
  },
  methods: {
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
    levelGap() {
      return "24px";
    },

    rebuild() {
      const R = this.root || {};

      // генератор стабильных id по пути в дереве (если у узла нет id)
      const makeId = (path, node) => node.id ?? `${path.join(".")}::${node.name || "unit"}`;

      // универсальный доступ к детям (любой из вариантов)
      const getChildren = (n) =>
        n?.children ?? n?.units ?? n?.kids ?? n?.childs ?? n?.subunits ?? [];

      const levels = [],
        edges = [];
      const q = [{ node: R, level: 0, parentId: null, path: [0] }];

      while (q.length) {
        const { node, level, parentId, path } = q.shift();
        // принудительно создаём id, если отсутствует
        if (!node.id) node.id = makeId(path, node);

        (levels[level] ||= []).push(node);

        const kids = getChildren(node);
        kids.forEach((ch, i) => {
          if (!ch.id) ch.id = makeId([...path, i + 1], ch);
          edges.push({ pId: node.id, cId: ch.id });
          q.push({ node: ch, level: level + 1, parentId: node.id, path: [...path, i + 1] });
        });
      }

      this.levels = levels;
      this.edges = edges;
      this.$nextTick(this.remeasureDebounced);
    },
    remeasureDebounced() {
      if (this.rafId) cancelAnimationFrame(this.rafId);
      this.rafId = requestAnimationFrame(this.remeasure);
    },

    remeasure() {
      const wrap = this.$refs.wrap;
      if (!wrap) return;
      const rect = wrap.getBoundingClientRect();
      const pos = new Map();

      // Собираем геометрию карточек
      for (const row of this.levels) {
        for (const n of row) {
          const elRef = this.$refs[`n-${n.id}`];
          const el = Array.isArray(elRef) ? elRef[0] : elRef;
          if (!el) continue;
          const r = el.getBoundingClientRect();
          pos.set(n.id, { x: r.left - rect.left, y: r.top - rect.top, w: r.width, h: r.height });
        }
      }

      // Строим диагональные/плавные связи
      const paths = [];
      const ARROW_GAP = 10; // отступ от верхнего края ребёнка
      const CURVE_FACTOR = 0.42; // насколько “плавная” дуга
      for (const e of this.edges) {
        const p = pos.get(e.pId);
        const c = pos.get(e.cId);
        if (!p || !c) continue;

        const x1 = p.x + p.w / 2; // низ родителя
        const y1 = p.y + p.h;
        const x2 = c.x + c.w / 2; // верх ребёнка (с зазором)
        const y2 = c.y - ARROW_GAP;

        const dy = Math.max(20, y2 - y1);
        const cx1 = x1; // контрольные точки для C-сплайна
        const cy1 = y1 + dy * CURVE_FACTOR;
        const cx2 = x2;
        const cy2 = y2 - dy * CURVE_FACTOR;

        paths.push(`M ${x1} ${y1} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${x2} ${y2}`);
      }

      this.positions = pos;
      this.diagPaths = paths;

      // SVG: занимаем всю область и задаём viewBox
      const svg = this.$refs.wires;
      if (svg) {
        const w = Math.max(rect.width, wrap.scrollWidth || rect.width);
        const h = Math.max(rect.height, wrap.scrollHeight || rect.height);
        svg.setAttribute("width", "100%");
        svg.setAttribute("height", "100%");
        svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
      }
    },

    pick(node, level) {
      this.$emit("select", { node, level });
    },
  },
};
</script>

<template>
  <div class="board" ref="wrap">
    <!-- SVG simlar va o‘qlar -->
    <svg ref="wires" class="wires" preserveAspectRatio="none">
      <defs>
        <!-- Стрелка -->
        <marker
          id="arrow-tip"
          markerWidth="8"
          markerHeight="8"
          refX="0"
          refY="3"
          orient="auto"
          markerUnits="strokeWidth"
        >
          <!-- Здесь можно задать нужный цвет -->
          <path d="M0,0 L6,3 L0,6 Z" fill="#404040" stroke="#404040" />
        </marker>
      </defs>

      <!-- Диагонали “родитель → ребёнок” -->
      <g
        fill="none"
        :stroke="wireColor"
        stroke-width="2.2"
        stroke-linecap="round"
        stroke-linejoin="round"
        style="color: var(--wire)"
      >
        <path v-for="(d, i) in diagPaths" :key="'edge-' + i" :d="d" marker-end="url(#arrow-tip)" />
      </g>
    </svg>

    <!-- Darajalar -->
    <div
      v-for="(row, lvl) in levels"
      :key="'lvl-' + lvl"
      class="level"
      :style="{ '--gap': levelGap(lvl) }"
    >
      <div
        v-for="n in row"
        :key="n.id"
        class="node"
        :style="{ '--box': typeInfo(n.type).color }"
        :ref="'n-' + n.id"
        @click="pick(n, lvl)"
      >
        <div class="node-type">{{ typeInfo(n.type).label }}</div>
        <div class="node-title">{{ n.name }}</div>
        <div v-if="showCounters" class="node-meta">
          <span v-if="empCount(n)">{{ empCount(n) }} сотрудн.</span>
          <span v-if="kidsCount(n)"> · {{ kidsCount(n) }} подр.</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
:root {
  /* Defaultlar; OrganizationDetail’dan var() larni meros qilib oladi */
  --panel: #fff;
  --line: #e6e8ee;
  --wire: #c8ced9;

  --c-dir: #8b5cf6;
  --c-mng: #22c55e;
  --c-dep: #06b6d4;
  --c-sec: #f59e0b;
  --c-oth: #9ca3af;
}

.board {
  position: relative;
  padding: 8px 8px 24px;
  border-radius: 12px;
  background: var(--panel);
  border: 1px solid var(--line);
  overflow: hidden; /* SVG absolute bo‘lgani uchun silliq ko‘rinsin */
}
.wires {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.level {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: center;
  gap: var(--gap, 40px);
  margin: 40px 0;
  flex-wrap: wrap; /* uzun qatorda sig‘may qolsa tashlab ketadi */
}

.node {
  width: 240px;
  min-height: 76px;
  padding: 12px 14px 14px;
  border-radius: 14px;
  background: var(--panel);
  box-shadow: 0 10px 22px rgba(0, 0, 0, 0.06);
  transition: transform 0.18s, box-shadow 0.18s, filter 0.18s;
  cursor: pointer;
  border: 1px solid #eef2f7;
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
</style>
