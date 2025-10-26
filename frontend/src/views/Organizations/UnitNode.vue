<script>
export default {
  name: "UnitNode",
  emits: ["pick-unit", "create-child", "create-emp"],
  props: {
    node: { type: Object, required: true },
    wire: { type: String, default: "#5a6b84" },
    level: { type: Number, default: 0 },
    parentPath: { type: String, default: "" },
  },
  data() {
    return { paths: [], _ro: null, _mo: null };
  },
  computed: {
    children() {
      return Array.isArray(this.node.children) ? this.node.children : [];
    },
    unitType() {
      return this.node?.type || "";
    },
    path() {
      const name = this.node?.name || "Без названия";
      return this.parentPath ? `${this.parentPath} ⟶ ${name}` : name;
    },
  },
  watch: {
    node: {
      deep: true,
      handler() {
        this.$nextTick(this.computePaths);
      },
    },
  },
  mounted() {
    this.$nextTick(() => {
      setTimeout(this.computePaths, 0);
      if (window.ResizeObserver) {
        this._ro = new ResizeObserver(this.computePaths);
        this._ro.observe(this.$refs.kids);
      }
      this._mo = new MutationObserver(this.computePaths);
      this._mo.observe(this.$refs.row, { childList: true, subtree: true });
      window.addEventListener("resize", this.computePaths);
    });
  },
  beforeUnmount() {
    if (this._ro) this._ro.disconnect();
    if (this._mo) this._mo.disconnect();
    window.removeEventListener("resize", this.computePaths);
  },
  methods: {
    pickUnit() {
      this.$emit("pick-unit", this.node, this.path);
    },

    _childBoxOf(cell) {
      const nodeRoot = cell.querySelector(":scope > .node");
      if (!nodeRoot) return null;
      const box = nodeRoot.querySelector(":scope > .box");
      return box || null;
    },

    computePaths() {
      const box = this.$refs.box,
        kids = this.$refs.kids,
        row = this.$refs.row;
      if (!box || !kids || !row) {
        this.paths = [];
        return;
      }

      const base = kids.getBoundingClientRect();
      const pb = box.getBoundingClientRect();
      const startX = pb.left + pb.width / 2 - base.left;
      const startY = pb.bottom - base.top;

      let cells = [];
      try {
        cells = Array.from(row.querySelectorAll(":scope > .cell"));
      } catch {
        cells = Array.from(row.children).filter((el) => el.classList?.contains("cell"));
      }

      const results = [];
      for (let idx = 0; idx < cells.length; idx++) {
        const cell = cells[idx];
        const childBox = this._childBoxOf(cell);
        if (!childBox) continue;

        const cb = childBox.getBoundingClientRect();
        const endX = cb.left + cb.width / 2 - base.left;
        const endY = cb.top - base.top;

        const midY = startY + Math.max(14, (endY - startY) * 0.5);
        const c1x = startX,
          c1y = midY;
        const c2x = endX,
          c2y = midY;
        const tip = 11;
        const d =
          `M ${startX.toFixed(1)} ${startY.toFixed(1)} ` +
          `C ${c1x.toFixed(1)} ${c1y.toFixed(1)}, ` +
          `${c2x.toFixed(1)} ${c2y.toFixed(1)}, ` +
          `${endX.toFixed(1)} ${(endY - tip).toFixed(1)} ` +
          `L ${endX.toFixed(1)} ${endY.toFixed(1)}`;

        results.push({ d, key: idx });
      }
      this.paths = results;
    },
  },
};
</script>

<template>
  <div class="node">
    <!-- Карточка -->
    <div
      ref="box"
      class="box"
      @click.stop="pickUnit"
      @mousedown.stop
      :title="unitType ? 'Тип: ' + unitType : ''"
    >
      <div class="name">{{ node.name || "Без названия" }}</div>
      <div v-if="unitType" class="type">{{ unitType }}</div>

      <!-- Встроенные кнопки (внутри карточки) -->
      <div class="inner-actions">
        <button
          class="pill"
          @mousedown.stop.prevent="$emit('create-emp', node)"
          @click.stop.prevent="$emit('create-emp', node)"
        >
          👤 Сотрудник
        </button>
        <button
          class="pill ghost"
          @mousedown.stop.prevent="$emit('create-child', node)"
          @click.stop.prevent="$emit('create-child', node)"
        >
          ➕ Подразделение
        </button>
      </div>
    </div>

    <!-- Дочерние узлы -->
    <div v-if="children.length" ref="kids" class="kids">
      <svg class="wires" :style="{ color: wire }" preserveAspectRatio="none">
        <defs>
          <marker id="arrowHead" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
            <path d="M0,0 L6,3 L0,6 z" fill="currentColor" />
          </marker>
        </defs>
        <path
          v-for="p in paths"
          :key="p.key"
          :d="p.d"
          class="wire-path"
          marker-end="url(#arrowHead)"
        />
      </svg>

      <div ref="row" class="row">
        <div v-for="c in children" :key="c.id || c.name" class="cell">
          <UnitNode
            :node="c"
            :wire="wire"
            :level="level + 1"
            :parentPath="path"
            @pick-unit="$emit('pick-unit', $event, path)"
            @create-child="$emit('create-child', $event)"
            @create-emp="$emit('create-emp', $event)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.node {
  position: relative;
  display: grid;
  justify-items: center;
  overflow: visible;
}

/* Карточка */
.box {
  position: relative;
  background: #fff;
  border: 2px solid #c9d1e1;
  border-radius: 14px;
  padding: 14px 16px 18px;
  min-width: 260px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.15s ease, transform 0.12s ease, box-shadow 0.2s ease;
  box-shadow: 0 8px 18px rgba(19, 31, 55, 0.06);
}
.box:hover {
  border-color: rgba(25, 196, 109, 0.55);
  transform: translateY(-1px);
  box-shadow: 0 12px 26px rgba(19, 31, 55, 0.08);
}
.name {
  font-size: 16px;
  font-weight: 900;
  letter-spacing: 0.2px;
}
.type {
  margin-top: 4px;
  font-size: 11px;
  color: #7b8497;
}

/* Кнопки внутри карточки */
.inner-actions {
  margin-top: 10px;
  display: flex;
  gap: 6px;
  justify-content: center;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.15s ease;
}
.box:hover .inner-actions {
  opacity: 1;
  pointer-events: auto;
}

/* Кнопки-пилюли */
.pill {
  height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 12px;
  border: 1px solid rgba(25, 196, 109, 0.35);
  background: rgba(25, 196, 109, 0.1);
  color: #0d8f56;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
}
.pill:hover {
  background: rgba(25, 196, 109, 0.18);
}
.pill.ghost {
  border-color: #c9d1e1;
  background: #f6f8fc;
  color: #1b2739;
}
.pill.ghost:hover {
  background: #eef2f9;
}

/* Дети и стрелки */
.kids {
  position: relative;
  width: 100%;
}
.row {
  position: relative;
  z-index: 1;
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: max-content;
  gap: 30px;
  padding-top: 6px;
  margin-top: 40px;
  overflow: visible;
}
.cell {
  display: grid;
  justify-items: center;
  overflow: visible;
}

/* SVG стрелки */
.wires {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}
.wire-path {
  fill: none;
  stroke: currentColor;
  stroke-width: 2.2;
  vector-effect: non-scaling-stroke;
  filter: drop-shadow(0 1px 0 rgba(0, 0, 0, 0.05));
}
</style>
