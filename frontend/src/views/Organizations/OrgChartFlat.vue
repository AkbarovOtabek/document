<template>
  <div class="orgflat" :class="{ dark: isDark }">
    <!-- ВЕРХНЯЯ ПАНЕЛЬ -->
    <div class="topbar">
      <div class="spacer" />
      <div class="actions">
        <button class="btn add center" @click="$emit('add-center')">Добавить центр</button>
        <button class="btn add manage" @click="$emit('add-manage')">Добавить управление</button>
        <button class="btn add dept" @click="$emit('add-dept')">Добавить отдел</button>
        <button class="btn add sector" @click="$emit('add-sector')">Добавить сектор/группу</button>
        <button class="btn add other" @click="$emit('add-other')">Добавить иное</button>
      </div>
    </div>

    <!-- ПОЛЕ С ОРГСТРУКТУРОЙ -->
    <div
      class="canvas"
      ref="canvasEl"
      @mousedown="onPointerDown"
      @mousemove="onPointerMove"
      @mouseup="onPointerUp"
      @mouseleave="onPointerUp"
      @wheel.prevent="onWheel"
    >
      <svg
        :viewBox="`${view.x} ${view.y} ${view.w} ${view.h}`"
        xmlns="http://www.w3.org/2000/svg"
        class="chart"
      >
        <defs>
          <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
            <feDropShadow dx="0" dy="4" stdDeviation="6" flood-opacity="0.18" />
          </filter>

          <!-- 🔽 Определяем стрелки (для разных цветов) -->
          <marker
            v-for="color in markerColors"
            :key="color"
            :id="`arrow-${color.replace('#', '')}`"
            viewBox="0 0 10 10"
            refX="10"
            refY="5"
            markerWidth="6"
            markerHeight="6"
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" :fill="color" />
          </marker>
        </defs>

        <!-- СВЯЗИ -->
        <g class="links">
          <path
            v-for="link in links"
            :key="link.id"
            :d="link.d"
            class="edge"
            :stroke="link.stroke"
            fill="none"
            stroke-width="2"
            opacity="0.8"
            :marker-end="`url(#arrow-${link.stroke.replace('#', '')})`"
          />
        </g>

        <!-- УЗЛЫ -->
        <g class="nodes">
          <g
            v-for="n in laidOutNodes"
            :key="n.id"
            class="node"
            :transform="`translate(${n.x}, ${n.y})`"
            @click="$emit('pick-node', n.raw)"
          >
            <rect
              :width="NODE_W"
              :height="NODE_H"
              rx="14"
              ry="14"
              :fill="fillByType(n.raw.type)"
              filter="url(#shadow)"
            />
            <text class="title" :x="NODE_W / 2" :y="22" text-anchor="middle">
              {{ displayName(n.raw) }}
            </text>
            <text class="subtitle" :x="NODE_W / 2" :y="40" text-anchor="middle">
              {{ displaySubtitle(n.raw) }}
            </text>
          </g>
        </g>
      </svg>

      <div class="hint">Колесо — масштаб, перетаскивание — панорама</div>
      <div v-if="_debug" class="debug-badge">
        {{ _debug.nodes }} узл · {{ _debug.edges }} связ · {{ _debug.roots }} корн
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { API_BASE_URL } from "@/API.js";

export default {
  name: "OrgChartFlat",
  props: {
    organizationSlug: { type: String, default: "" },
    organizationId: { type: [String, Number], default: null },
    includeEmployees: { type: Boolean, default: true },
    useCredentials: { type: Boolean, default: false },
    isDark: { type: Boolean, default: false },
    langRU: { type: Boolean, default: true },
  },
  emits: [
    "add-center",
    "add-manage",
    "add-dept",
    "add-sector",
    "add-other",
    "pick-node",
    "loaded",
    "error",
  ],
  data() {
    return {
      loading: false,
      error: "",
      roots: [],
      view: { x: 0, y: 0, w: 1600, h: 900 },
      dragging: false,
      dragStart: { x: 0, y: 0 },
      viewStart: { x: 0, y: 0 },
      NODE_W: 160,
      NODE_H: 56,
      GAP_X: 64,
      GAP_Y: 140,
    };
  },
  computed: {
    /** Цвета стрелок для marker */
    markerColors() {
      return ["#ff8a3d", "#7a64ff", "#2a5da0", "#37c2c0", "#7c8aa3"];
    },
    laidOutNodes() {
      const placed = [];
      let cursorX = 0;

      const layout = (node, depth, xLeft) => {
        const kids = Array.isArray(node.children) ? node.children : [];
        const w = this.subtreeWidth(node);
        const nodeX = xLeft + w / 2 - this.NODE_W / 2;
        const nodeY = depth * this.GAP_Y;

        placed.push({ id: node.id, x: nodeX, y: nodeY, raw: node });

        let childX = xLeft;
        for (const ch of kids) {
          const cw = this.subtreeWidth(ch);
          layout(ch, depth + 1, childX);
          childX += cw + this.GAP_X;
        }
      };

      for (const r of this.roots) {
        const w = this.subtreeWidth(r);
        layout(r, 0, cursorX);
        cursorX += w + this.GAP_X * 2;
      }
      return placed;
    },
    links() {
      const byId = new Map(this.laidOutNodes.map((n) => [n.id, n]));
      const out = [];
      const walk = (node) => {
        const kids = Array.isArray(node.children) ? node.children : [];
        const p = byId.get(node.id);
        for (const ch of kids) {
          const c = byId.get(ch.id);
          if (p && c) {
            const x1 = p.x + this.NODE_W / 2;
            const y1 = p.y + this.NODE_H;
            const x2 = c.x + this.NODE_W / 2;
            const y2 = c.y;
            const mx = (x1 + x2) / 2;

            // плавная кривая вниз со стрелкой
            out.push({
              id: `${node.id}->${ch.id}`,
              d: `M ${x1} ${y1} C ${mx} ${y1 + 40}, ${mx} ${y2 - 40}, ${x2} ${y2}`,
              stroke: this.strokeByType(ch.type),
            });
          }
          walk(ch);
        }
      };
      this.roots.forEach(walk);
      return out;
    },
  },
  mounted() {
    this.fetchData();
    this.resizeToContainer();
    window.addEventListener("resize", this.resizeToContainer);
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.resizeToContainer);
  },
  methods: {
    async fetchData() {
      this.loading = true;
      this.error = "";
      try {
        let orgId = this.organizationId;
        if (!orgId && this.organizationSlug) {
          const { data } = await axios.get(
            `${API_BASE_URL}api/organizations/${this.organizationSlug}/`,
            { withCredentials: this.useCredentials }
          );
          orgId = data?.id ?? data?.pk ?? null;
        }

        const params = {};
        if (orgId) params.organization_id = orgId;
        if (this.organizationSlug && !orgId) params.organization = this.organizationSlug;

        const { data: unitsRaw } = await axios.get(
          `${API_BASE_URL}api/organizations-staff/units/`,
          { params, withCredentials: this.useCredentials }
        );
        const units = Array.isArray(unitsRaw?.results)
          ? unitsRaw.results
          : Array.isArray(unitsRaw)
          ? unitsRaw
          : [];

        this.roots = this.buildTree(units);
        this.$emit("loaded", this.roots);
      } catch (e) {
        this.error = e?.message || "Ошибка загрузки";
        this.$emit("error", this.error);
      } finally {
        this.loading = false;
      }
    },

    buildTree(units) {
      // 1) Достаём parent в любом виде (число/строка/объект)
      const getParentRaw = (u) => {
        let p = u.parent_id ?? u.parent ?? u.parentUnit ?? u.parent_unit ?? u.parentId ?? null;

        // Если это объект, берём его id/pk/value
        if (p && typeof p === "object") {
          p = p.id ?? p.pk ?? p.value ?? null;
        }
        return p;
      };

      // 2) Нормализуем узлы: приводим id/parent_id к строкам
      const nodes = units.map((u) => {
        const rawParent = getParentRaw(u);
        const idKey = u.id != null ? String(u.id) : null;
        const parentKey = rawParent != null && rawParent !== "" ? String(rawParent) : null;

        return {
          id: idKey,
          type: this.normalizeType(u.unit_type || u.type),
          name: u.name_ru || u.name || u.name_uz || (idKey ? `Unit #${idKey}` : "Unit"),
          position: u.position || u.title || "",
          parent_id: parentKey,
          children: [],
          _raw: u,
        };
      });

      // 3) Строим дерево
      const byId = new Map(nodes.map((n) => [n.id, n]));
      const roots = [];
      for (const n of nodes) {
        if (n.parent_id && byId.has(n.parent_id)) {
          byId.get(n.parent_id).children.push(n);
        } else {
          roots.push(n);
        }
      }

      // 4) Отладка: покажем в консоль и на экране
      const edges = nodes.filter((n) => n.parent_id && byId.has(n.parent_id)).length;
      console.log(`[OrgChartFlat] nodes=${nodes.length}, edges=${edges}, roots=${roots.length}`);
      this._debug = { nodes: nodes.length, edges, roots: roots.length };

      return roots;
    },

    normalizeType(t) {
      if (!t) return "other";
      t = String(t).toLowerCase();
      if (["center", "centre", "центр"].includes(t)) return "center";
      if (["manage", "management", "управление"].includes(t)) return "manage";
      if (["dept", "department", "отдел"].includes(t)) return "dept";
      if (["sector", "group", "сектор", "группа"].includes(t)) return "sector";
      return "other";
    },
    subtreeWidth(node) {
      const kids = node.children || [];
      if (!kids.length) return this.NODE_W;
      const sum = kids.map(this.subtreeWidth).reduce((a, b) => a + b, 0);
      return Math.max(sum + this.GAP_X * (kids.length - 1), this.NODE_W);
    },

    // Панорамирование и масштаб
    onWheel(e) {
      const rect = this.$refs.canvasEl.getBoundingClientRect();
      const px = e.clientX - rect.left,
        py = e.clientY - rect.top;
      const wx = this.view.x + (px / rect.width) * this.view.w;
      const wy = this.view.y + (py / rect.height) * this.view.h;
      const scale = e.deltaY < 0 ? 0.9 : 1.1;
      const newW = this.view.w * scale,
        newH = this.view.h * scale;
      this.view.x = wx - (px / rect.width) * newW;
      this.view.y = wy - (py / rect.height) * newH;
      this.view.w = Math.max(400, Math.min(6000, newW));
      this.view.h = Math.max(300, Math.min(4000, newH));
    },
    onPointerDown(e) {
      this.dragging = true;
      this.dragStart = { x: e.clientX, y: e.clientY };
      this.viewStart = { x: this.view.x, y: this.view.y };
    },
    onPointerMove(e) {
      if (!this.dragging) return;
      const rect = this.$refs.canvasEl.getBoundingClientRect();
      const dx = ((e.clientX - this.dragStart.x) / rect.width) * this.view.w;
      const dy = ((e.clientY - this.dragStart.y) / rect.height) * this.view.h;
      this.view.x = this.viewStart.x - dx;
      this.view.y = this.viewStart.y - dy;
    },
    onPointerUp() {
      this.dragging = false;
    },
    resizeToContainer() {
      if (!this.$refs.canvasEl) return;
      this.view.w = 1600;
      this.view.h = 900;
    },

    // Вспомогательные функции
    displayName(n) {
      return this.langRU ? n.name || "Без названия" : n.name || "Nomsiz";
    },
    displaySubtitle(n) {
      const base =
        n.type === "center"
          ? "Центр"
          : n.type === "manage"
          ? "Управление"
          : n.type === "dept"
          ? "Отдел"
          : n.type === "sector"
          ? "Сектор/группа"
          : "Иное";
      return n.position ? `${base} • ${n.position}` : base;
    },
    fillByType(t) {
      return t === "center"
        ? "#ff8a3d"
        : t === "manage"
        ? "#7a64ff"
        : t === "dept"
        ? "#173a6a"
        : t === "sector"
        ? "#37c2c0"
        : "#5a6b84";
    },
    strokeByType(t) {
      return t === "center"
        ? "#ff8a3d"
        : t === "manage"
        ? "#7a64ff"
        : t === "dept"
        ? "#2a5da0"
        : t === "sector"
        ? "#37c2c0"
        : "#7c8aa3";
    },
  },
};
</script>

<style scoped>
.orgflat {
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 100%;
  color: #17202a;
}
.orgflat.dark {
  color: #e7edf6;
}
.topbar {
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  padding: 8px 12px;
}
.actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.btn {
  padding: 8px 12px;
  border-radius: 12px;
  border: 1px solid transparent;
  background: #f2f4f8;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.05s, box-shadow 0.2s, background 0.2s;
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.06);
}
.btn:hover {
  transform: translateY(-1px);
}
.btn.add.center {
  background: #ffe8d7;
  border-color: #ff8a3d33;
}
.btn.add.manage {
  background: #ece8ff;
  border-color: #7a64ff33;
}
.btn.add.dept {
  background: #e1ebff;
  border-color: #2a5da033;
}
.btn.add.sector {
  background: #d9f6f5;
  border-color: #37c2c033;
}
.btn.add.other {
  background: #eef1f6;
  border-color: #8896a633;
}
.canvas {
  position: relative;
  flex: 1;
  background: radial-gradient(1200px 600px at 30% 20%, #3b4654 0%, #2e3844 60%, #26303a 100%);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.04);
  min-height: 520px;
}
.orgflat:not(.dark) .canvas {
  background: #f7f8fb;
  box-shadow: inset 0 0 0 1px rgba(16, 24, 40, 0.06);
}
.chart {
  width: 100%;
  height: 100%;
  user-select: none;
  -webkit-user-select: none;
  display: block;
}
.edge {
  stroke-linecap: round;
  transition: stroke 0.3s ease;
}
.node .title {
  font-size: 13px;
  font-weight: 700;
  fill: #0b1621;
}
.node .subtitle {
  font-size: 11px;
  fill: #243548;
  opacity: 0.85;
}
.orgflat.dark .node .title,
.orgflat.dark .node .subtitle {
  fill: #fff;
  opacity: 0.92;
}
.hint {
  position: absolute;
  right: 10px;
  bottom: 8px;
  font-size: 12px;
  opacity: 0.7;
  background: rgba(0, 0, 0, 0.25);
  color: #fff;
  padding: 4px 8px;
  border-radius: 8px;
}
.orgflat:not(.dark) .hint {
  background: rgba(0, 0, 0, 0.05);
  color: #3b4654;
}
.debug-badge {
  position: absolute;
  left: 10px;
  bottom: 8px;
  font-size: 12px;
  background: rgba(0, 0, 0, 0.25);
  color: #fff;
  padding: 4px 8px;
  border-radius: 8px;
}
.orgflat:not(.dark) .debug-badge {
  background: rgba(0, 0, 0, 0.05);
  color: #3b4654;
}
</style>
