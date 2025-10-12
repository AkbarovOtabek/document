<script>
export default {
  name: "OrgChartBoard",
  emits: ["select"],
  props: {
    roots: { type: Array, default: () => [] },
    showCounters: { type: Boolean, default: true },
  },
  data() {
    return {
      cols: [], // [{rootId, levels, edges, positions: Map, paths: []}]
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
    roots: {
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
    levelGap(lvl) {
      return lvl === 0 ? "24px" : "24px";
    },

    rebuild() {
      const cols = [];
      for (const root of this.roots) {
        const levels = [];
        const edges = [];
        const q = [{ node: root, level: 0, parentId: null }];

        while (q.length) {
          const { node, level, parentId } = q.shift();
          (levels[level] ||= []).push(node);
          if (parentId != null) edges.push({ pId: parentId, cId: node.id });
          (node.children || []).forEach((ch) =>
            q.push({ node: ch, level: level + 1, parentId: node.id })
          );
        }

        cols.push({
          rootId: root.id,
          levels,
          edges,
          positions: new Map(),
          paths: [], // SVG path strings
        });
      }

      this.cols = cols;
      this.$nextTick(this.remeasure);
    },

    remeasure() {
      for (const col of this.cols) {
        const wrap = this.$refs[`wrap-${col.rootId}`];
        if (!wrap) continue;
        const rect = wrap.getBoundingClientRect();

        col.positions.clear();
        for (const row of col.levels) {
          for (const n of row) {
            const el = this.$refs[`n-${col.rootId}-${n.id}`];
            const box = Array.isArray(el) ? el[0] : el;
            if (!box) continue;
            const r = box.getBoundingClientRect();
            col.positions.set(n.id, {
              x: r.left - rect.left,
              y: r.top - rect.top,
              w: r.width,
              h: r.height,
            });
          }
        }

        const paths = [];
        for (const e of col.edges) {
          const p = col.positions.get(e.pId);
          const c = col.positions.get(e.cId);
          if (!p || !c) continue;

          const x1 = p.x + p.w / 2,
            y1 = p.y + p.h;
          const x2 = c.x + c.w / 2,
            y2 = c.y;
          const ARROW_GAP = 8; // 6–10px: подберите под свой дизайн
          const y2Arrow = y2 - ARROW_GAP;
          const ymid = y1 + Math.max(16, (y2Arrow - y1) * 0.45);

          // вниз -> горизонталь -> вниз (заканчиваем перед карточкой)
          paths.push(`M ${x1} ${y1} V ${ymid} H ${x2} V ${y2Arrow}`);
        }
        col.paths = paths;
      }
    },

    pick(colRootId, node, level) {
      this.$emit("select", { colRootId, node, level });
    },
  },
};
</script>

<template>
  <div class="board">
    <!-- одна колонка на корень -->
    <div class="col" v-for="root in roots" :key="root.id">
      <div class="col-wrap" :ref="`wrap-${root.id}`">
        <!-- ЛИНИИ + СТРЕЛКИ -->
        <svg class="wires" :width="'100%'" :height="'100%'" preserveAspectRatio="none">
          <defs>
            <!-- уникальный маркер-стрелка для данной колонки -->
            <marker
              :id="`arrow-${root.id}`"
              markerWidth="10"
              markerHeight="10"
              refX="6"
              refY="3"
              orient="auto"
              markerUnits="strokeWidth"
            >
              <!-- цвет маркера возьмём как currentColor, чтобы совпадал с линией -->
              <path
                v-for="(d, i) in cols.find((c) => c.rootId === root.id)?.paths || []"
                :key="i"
                :d="d"
                :marker-end="`url(#arrow-${root.id})`"
              />
            </marker>
          </defs>

          <!-- линии; stroke берёт currentColor от <g> -->
          <g fill="none" :stroke="`var(--wire)`" stroke-width="1.5" style="color: var(--wire)">
            <path
              v-for="(d, i) in cols.find((c) => c.rootId === root.id)?.paths || []"
              :key="i"
              :d="d"
              :marker-end="`url(#arrow-${root.id})`"
            />
          </g>
        </svg>

        <!-- уровни/карточки -->
        <div
          v-for="(row, lvl) in cols.find((c) => c.rootId === root.id)?.levels || []"
          :key="`lvl-${root.id}-${lvl}`"
          class="level"
          :style="{ '--gap': levelGap(lvl) }"
        >
          <div
            v-for="n in row"
            :key="n.id"
            class="node"
            :style="{ '--box': typeInfo(n.type).color }"
            :ref="`n-${root.id}-${n.id}`"
            @click="pick(root.id, n, lvl)"
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
    </div>
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
.board {
  --wire: #c8ced9; /* цвет линий/стрелок */
  --line: #e6e8ee;
  --panel: #fff;
  --ink: #0f141a;
  display: flex;
  justify-content: space-between;
  gap: 32px;
  align-items: flex-start;
}
.col {
  flex: 1;
  min-width: 280px;
}
.col-wrap {
  position: relative;
  padding: 8px 8px 24px;
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
  margin: 28px 0;
}

/* карточка узла */
.node {
  width: 240px;
  min-height: 76px;
  padding: 12px 14px 14px;
  border-radius: 14px;
  background: #fff;
  box-shadow: 0 10px 22px rgba(0, 0, 0, 0.06);
  transition: transform 0.18s, box-shadow 0.18s, filter 0.18s;
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
.wires {
  position: absolute;
  inset: 0;
  pointer-events: none; /* клики идут по карточкам */
  z-index: 3; /* выше карточек */
}
.level {
  position: relative;
  z-index: 2; /* ниже svg-проводки */
}
</style>
