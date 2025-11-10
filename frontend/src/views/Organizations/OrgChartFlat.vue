<script>
import axios from "axios";
import { API_BASE_URL } from "@/API.js";

export default {
  name: "OrgChartFlat",
  props: {
    organizationSlug: { type: String, default: "" },
    organizationId:   { type: [String, Number], default: null },
    includeEmployees: { type: Boolean, default: true },
    useCredentials:   { type: Boolean, default: false },
    isDark:           { type: Boolean, default: false },
    langRU:           { type: Boolean, default: true },
  },
  emits: ["add-center","add-manage","add-dept","add-sector","add-other","pick-node","loaded","error"],
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
      _debug: null, // <-- чтобы не было Vue warning
    };
  },
  computed: {
    markerColors() { return ["#ff8a3d", "#7a64ff", "#2a5da0", "#37c2c0", "#7c8aa3"]; },
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
        const base = `${API_BASE_URL}api/organizations-staff/units/`;
        const opts = { withCredentials: this.useCredentials };

        let resp = null;

        // 1) если есть organizationId — используем ТОЛЬКО его
        if (this.organizationId) {
          resp = await axios.get(base, { params: { organization_id: this.organizationId }, ...opts });
        } 
        // 2) если id нет, но есть slug — пробуем по slug (если бэк поддерживает)
        else if (this.organizationSlug) {
          resp = await axios.get(base, { params: { organization: this.organizationSlug }, ...opts });
        } 
        // 3) иначе — общий список (диагностика; можно удалить)
        else {
          resp = await axios.get(base, opts);
        }

        const unitsRaw = resp?.data;
        const units = Array.isArray(unitsRaw?.results)
          ? unitsRaw.results
          : Array.isArray(unitsRaw)
          ? unitsRaw
          : [];

        this.roots = this.buildTree(units);
        this.$emit("loaded", this.roots);

        const edges = this.roots.reduce((acc, r) => acc + (r.children?.length || 0), 0);
        this._debug = { nodes: units.length, edges, roots: this.roots.length };
      } catch (e) {
        const msg = e?.response?.data?.detail || e?.response?.statusText || e?.message || "Ошибка загрузки";
        this.error = `Не удалось загрузить подразделения: ${msg}`;
        this.$emit("error", this.error);
      } finally {
        this.loading = false;
      }
    },

      buildTree(units) {
    // 1) Нормализуем записи и режем самоссылки
    const nodes = units.map(u => {
      const id = u.id != null ? String(u.id) : null;
      let parentId = u.parent_id != null ? String(u.parent_id) : null;

      // самоссылка -> считаем корнем
      if (id && parentId && id === parentId) parentId = null;

      return {
        id,
        type: this.normalizeType(u.type),
        name: u.name || (id ? `Unit #${id}` : "Unit"),
        parent_id: parentId,
        children: [],
        order: Number.isFinite(u.order) ? u.order : 0,
        _raw: u,
      };
    });

    // 2) Собираем дерево
    const byId = new Map(nodes.map(n => [n.id, n]));
    const roots = [];
    for (const n of nodes) {
      if (n.parent_id && byId.has(n.parent_id) && n.parent_id !== n.id) {
        byId.get(n.parent_id).children.push(n);
      } else {
        roots.push(n);
      }
    }

    // 3) Сортировка детей для красивого вывода
    const typeRank = t => ({ center:0, manage:1, dept:2, sector:3, other:4 }[t] ?? 9);
    const sortRec = (node) => {
      node.children.sort((a,b) =>
        (typeRank(a.type) - typeRank(b.type)) ||
        (a.order - b.order) ||
        a.name.localeCompare(b.name, "ru"));
      node.children.forEach(sortRec);
    };
    roots.forEach(sortRec);

    // для отладочной плашки
    const edges = nodes.filter(n => n.parent_id && byId.has(n.parent_id) && n.parent_id !== n.id).length;
    this._debug = { nodes: nodes.length, edges, roots: roots.length };

    return roots;
  },

  normalizeType(t) {
    if (!t) return "other";
    t = String(t).toLowerCase();
    if (["directorate", "дирекция", "центр", "center", "centre"].includes(t)) return "center";
    if (["management", "управление", "manage"].includes(t)) return "manage";
    if (["department", "dept", "отдел"].includes(t)) return "dept";
    if (["section", "sector", "group", "сектор", "группа"].includes(t)) return "sector";
    return "other";
  },

  // Генерация рёбер с защитой от циклов
  links() {
    const byId = new Map(this.laidOutNodes.map(n => [n.id, n]));
    const out = [];
    const visiting = new Set();

    const walk = (node) => {
      if (visiting.has(node.id)) return; // защита от цикла
      visiting.add(node.id);

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
          out.push({
            id: `${node.id}->${ch.id}`,
            d: `M ${x1} ${y1} C ${mx} ${y1 + 40}, ${mx} ${y2 - 40}, ${x2} ${y2}`,
            stroke: this.strokeByType(ch.type),
          });
        }
        walk(ch);
      }
      visiting.delete(node.id);
    };

    this.roots.forEach(walk);
    return out;
  },
    subtreeWidth(node) {
      const kids = node.children || [];
      if (!kids.length) return this.NODE_W;
      const sum = kids.map(this.subtreeWidth).reduce((a, b) => a + b, 0);
      return Math.max(sum + this.GAP_X * (kids.length - 1), this.NODE_W);
    },

    onWheel(e) {
      const rect = this.$refs.canvasEl.getBoundingClientRect();
      const px = e.clientX - rect.left, py = e.clientY - rect.top;
      const wx = this.view.x + (px / rect.width) * this.view.w;
      const wy = this.view.y + (py / rect.height) * this.view.h;
      const scale = e.deltaY < 0 ? 0.9 : 1.1;
      const newW = this.view.w * scale, newH = this.view.h * scale;
      this.view.x = wx - (px / rect.width) * newW;
      this.view.y = wy - (py / rect.height) * newH;
      this.view.w = Math.max(400, Math.min(6000, newW));
      this.view.h = Math.max(300, Math.min(4000, newH));
    },
    onPointerDown(e) {
      this.dragging = true;
      this.dragStart = { x: e.clientX, y: e.clientY };
      this.viewStart  = { x: this.view.x, y: this.view.y };
    },
    onPointerMove(e) {
      if (!this.dragging) return;
      const rect = this.$refs.canvasEl.getBoundingClientRect();
      const dx = ((e.clientX - this.dragStart.x) / rect.width) * this.view.w;
      const dy = ((e.clientY - this.dragStart.y) / rect.height) * this.view.h;
      this.view.x = this.viewStart.x - dx;
      this.view.y = this.viewStart.y - dy;
    },
    onPointerUp() { this.dragging = false; },

    resizeToContainer() { if (this.$refs.canvasEl) { this.view.w = 1600; this.view.h = 900; } },

    displayName(n) { return this.langRU ? (n.name || "Без названия") : (n.name || "Nomsiz"); },
    displaySubtitle(n) {
      const base = n.type === "center" ? "Центр"
                : n.type === "manage" ? "Управление"
                : n.type === "dept" ? "Отдел"
                : n.type === "sector" ? "Сектор/группа"
                : "Иное";
      return n.position ? `${base} • ${n.position}` : base;
    },
    fillByType(t) {
      return t === "center" ? "#ff8a3d"
           : t === "manage" ? "#7a64ff"
           : t === "dept"   ? "#173a6a"
           : t === "sector" ? "#37c2c0"
           : "#5a6b84";
    },
    strokeByType(t) {
      return t === "center" ? "#ff8a3d"
           : t === "manage" ? "#7a64ff"
           : t === "dept"   ? "#2a5da0"
           : t === "sector" ? "#37c2c0"
           : "#7c8aa3";
    },
  },
};
</script>
<template>
  <div class="orgflat" :class="{ dark: isDark }">
    <!-- верхняя панель (опционально) -->
    <div class="topbar">
      <div />
      <div class="actions">
        <button class="btn add center" @click="$emit('add-center')">+ Центр</button>
        <button class="btn add manage" @click="$emit('add-manage')">+ Управление</button>
        <button class="btn add dept" @click="$emit('add-dept')">+ Отдел</button>
        <button class="btn add sector" @click="$emit('add-sector')">+ Сектор/Группа</button>
        <button class="btn add other" @click="$emit('add-other')">+ Иное</button>
      </div>
    </div>

    <!-- холст -->
    <div class="canvas"
         ref="canvasEl"
         @wheel.prevent="onWheel"
         @mousedown="onPointerDown"
         @mousemove="onPointerMove"
         @mouseup="onPointerUp"
         @mouseleave="onPointerUp">
      <svg class="chart"
           :viewBox="`${view.x} ${view.y} ${view.w} ${view.h}`"
           preserveAspectRatio="xMidYMid meet">

        <!-- рёбра -->
        <g class="edges">
          <path v-for="e in links()" :key="e.id"
                class="edge" :d="e.d" :stroke="e.stroke"
                fill="none" stroke-width="2"/>
        </g>

        <!-- узлы -->
        <g class="nodes">
          <g v-for="n in laidOutNodes" :key="n.id"
             class="node"
             :transform="`translate(${n.x}, ${n.y})`"
             @click="$emit('pick-node', n.raw)">
            <rect :width="NODE_W" :height="NODE_H" rx="12" :fill="fillByType(n.raw.type)"/>
            <text class="title" x="10" y="22">{{ displayName(n.raw) }}</text>
            <text class="subtitle" x="10" y="40">{{ displaySubtitle(n.raw) }}</text>
          </g>
        </g>
      </svg>

      <div v-if="error" class="error-badge">{{ error }}</div>
      <div class="hint">Колесо — масштаб, ЛКМ — перетаскивание</div>
      <div class="debug-badge" v-if="_debug">nodes: {{ _debug.nodes }} · roots: {{ _debug.roots }}</div>
    </div>
  </div>
</template>


<style scoped>
.orgflat { display:flex; flex-direction:column; gap:12px; height:100%; color:#17202a }
.orgflat.dark { color:#e7edf6 }
.topbar { display:grid; grid-template-columns:1fr auto; align-items:center; padding:8px 12px }
.actions { display:flex; gap:8px; flex-wrap:wrap }
.btn{ padding:8px 12px; border-radius:12px; border:1px solid transparent; background:#f2f4f8; font-weight:600; cursor:pointer; transition:transform .05s, box-shadow .2s, background .2s; box-shadow:0 1px 2px rgba(16,24,40,.06) }
.btn:hover{ transform:translateY(-1px) }
.btn.add.center{ background:#ffe8d7; border-color:#ff8a3d33 }
.btn.add.manage{ background:#ece8ff; border-color:#7a64ff33 }
.btn.add.dept{ background:#e1ebff; border-color:#2a5da033 }
.btn.add.sector{ background:#d9f6f5; border-color:#37c2c033 }
.btn.add.other{ background:#eef1f6; border-color:#8896a633 }

.canvas{ position:relative; flex:1; background:radial-gradient(1200px 600px at 30% 20%, #3b4654 0%, #2e3844 60%, #26303a 100%); border-radius:16px; overflow:hidden; box-shadow:inset 0 0 0 1px rgba(255,255,255,.04); min-height:520px }
.orgflat:not(.dark) .canvas{ background:#f7f8fb; box-shadow:inset 0 0 0 1px rgba(16,24,40,.06) }
.chart{ width:100%; height:100%; user-select:none; -webkit-user-select:none; display:block }
.edge{ stroke-linecap:round; transition:stroke .3s ease }
.node .title{ font-size:13px; font-weight:700; fill:#0b1621 }
.node .subtitle{ font-size:11px; fill:#243548; opacity:.85 }
.orgflat.dark .node .title, .orgflat.dark .node .subtitle{ fill:#fff; opacity:.92 }
.hint{ position:absolute; right:10px; bottom:8px; font-size:12px; opacity:.7; background:rgba(0,0,0,.25); color:#fff; padding:4px 8px; border-radius:8px }
.orgflat:not(.dark) .hint{ background:rgba(0,0,0,.05); color:#3b4654 }

.debug-badge{ position:absolute; left:10px; bottom:8px; font-size:12px; background:rgba(0,0,0,.25); color:#fff; padding:4px 8px; border-radius:8px }
.orgflat:not(.dark) .debug-badge{ background:rgba(0,0,0,.05); color:#3b4654 }

.error-badge{ position:absolute; left:10px; top:10px; font-size:12px; background:#fee2e2; color:#b91c1c; padding:6px 10px; border-radius:8px; border:1px solid #fecaca; max-width:60%; box-shadow:0 8px 18px rgba(0,0,0,.08) }
</style>
