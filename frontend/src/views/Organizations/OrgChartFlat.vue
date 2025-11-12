<template>
  <div class="orgflat" :class="{ dark: isDark }">
    <!-- Топбар -->
    <div class="topbar" ref="topbarEl">
      <div class="actions">
        <button class="btn add primary" @click="showAddUnit = true">+ Добавить структуру</button>
        <button class="btn add secondary" @click="showAddEmp = true">+ Добавить сотрудника</button>
      </div>
      <div class="meta" v-if="roots.length">
        {{ roots.length }} корневых подразделения
      </div>
    </div>

    <!-- Канвас -->
    <div class="canvas" ref="canvasEl" @wheel.prevent="onWheel" @contextmenu.prevent>
      <svg
        class="chart"
        ref="chartEl"
        :class="{ panning: dragging }"
        :viewBox="`${view.x} ${view.y} ${view.w} ${view.h}`"
        preserveAspectRatio="xMidYMid meet"
        @pointerdown="onPointerDown"
        @mousedown.prevent="onMouseDown"
        @click="onChartClick"
        @auxclick.prevent
      >
        <CardChartFlat
          :roots="roots"
          :tile="TILE"
          :langRU="langRU"
          :selected-id="selectedId"
          @node-click="onPickNode"
        />
      </svg>

      <div v-if="error" class="error-badge">{{ error }}</div>
      <div class="hint">Колесо — зум • Средняя кнопка — перетаскивание</div>

      <!-- Просмотр юнита (если используешь) -->
      <UnitInfoModal
        :open="showModal"
        :unit="selectedUnit"
        :head="headData"
        :headLoading="headLoading"
        :headError="headError"
        :langRU="langRU"
        :isDark="isDark"
        :panelTop="12"
        @close="closeModal"
      />
    </div>

    <!-- Модалки добавления -->
    <AddUnitModal
      v-if="showAddUnit"
      :open="showAddUnit"
      :units="flatUnits"
      :langRU="langRU"
      :isDark="isDark"
      @close="showAddUnit = false"
      @submit="handleCreateUnit"
    />

    <AddEmployeeModal
      v-if="showAddEmp"
      :open="showAddEmp"
      :units="flatUnits"
      :langRU="langRU"
      :isDark="isDark"
      @close="showAddEmp = false"
      @submit="handleCreateEmployee"
    />
  </div>
</template>

<script>
import axios from "axios";
import { API_BASE_URL } from "@/API.js";
import CardChartFlat from "./CardChartFlat.vue";
import UnitInfoModal from "./UnitInfoModal.vue";
import AddUnitModal from "./AddUnitModal.vue";
import AddEmployeeModal from "./AddEmployeeModal.vue";

export default {
  name: "OrgChartFlat",
  components: { CardChartFlat, UnitInfoModal, AddUnitModal, AddEmployeeModal },

  props: {
    organizationSlug: { type: String, default: "" },
    organizationId: { type: [String, Number], default: null },
    includeEmployees: { type: Boolean, default: true },
    useCredentials: { type: Boolean, default: false },
    isDark: { type: Boolean, default: false },
    langRU: { type: Boolean, default: true },
    fitOnLoad: { type: Boolean, default: true },
    initialZoom: { type: Number, default: 1 },
  },

  emits: [
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
      dragStart: { x: 0, y: 0, rectW: 1, rectH: 1 },
      viewStart: { x: 0, y: 0 },
      dragMoved: false,
      TILE: 120,

      panelTop: 60,
      showModal: false,
      selectedId: null,
      selectedUnit: null,
      selectedNode: null,
      headLoading: false,
      headError: "",
      headData: null,

      showAddUnit: false,
      showAddEmp: false,
    };
  },

  computed: {
    flatUnits() {
      // плоский список для select родителя
      const out = [];
      const walk = (n, depth = 0) => {
        out.push({ id: String(n.id), name: n.name, type: n.type, depth });
        (n.children || []).forEach((c) => walk(c, depth + 1));
      };
      this.roots.forEach(walk);
      return out;
    },
  },

  mounted() {
    this.measureTopbar();
    window.addEventListener("resize", this.measureTopbar, { passive: true });
    window.addEventListener("keydown", this.onKeyDown);
    this.fetchData();
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.measureTopbar);
    window.removeEventListener("keydown", this.onKeyDown);
  },

  methods: {
    measureTopbar() {
      this.$nextTick(() => {
        const h = this.$refs.topbarEl?.offsetHeight || 0;
        this.panelTop = h + 12;
      });
    },

    /* ----------------- загрузка данных ----------------- */
    async fetchData() {
      this.loading = true;
      this.error = "";
      try {
        const base = `${API_BASE_URL}api/organizations-staff/units/`;
        const opts = { withCredentials: this.useCredentials };
        let resp = null;

        if (this.organizationId)
          resp = await axios.get(base, { params: { organization_id: this.organizationId }, ...opts });
        else if (this.organizationSlug)
          resp = await axios.get(base, { params: { organization: this.organizationSlug }, ...opts });
        else
          resp = await axios.get(base, opts);

        const raw = resp?.data;
        const units = Array.isArray(raw?.results)
          ? raw.results
          : Array.isArray(raw)
          ? raw
          : [];

        this.roots = this.buildTree(units);
        this.$emit("loaded", this.roots);

        this.$nextTick(() => {
          if (this.fitOnLoad) this.fitToContent(120);
          else if (this.initialZoom && this.initialZoom !== 1) this.setZoom(this.initialZoom);
        });
      } catch (e) {
        this.error = `Не удалось загрузить подразделения: ${e?.response?.statusText || e?.message || "Ошибка"}`;
        this.$emit("error", this.error);
      } finally {
        this.loading = false;
      }
    },

    buildTree(units) {
      const normalizeType = (t) => {
        if (!t) return "other";
        t = String(t).toLowerCase();
        if (["directorate", "дирекция", "центр", "center", "centre"].includes(t)) return "center";
        if (["management", "управление", "manage"].includes(t)) return "manage";
        if (["department", "dept", "отдел"].includes(t)) return "dept";
        if (["section", "sector", "group", "сектор", "группа"].includes(t)) return "sector";
        return "other";
      };

      const nodes = units.map((u) => {
        const id = u.id != null ? String(u.id) : null;
        let parentId = u.parent_id != null ? String(u.parent_id) : null;
        if (id && parentId && id === parentId) parentId = null;
        return {
          id,
          type: normalizeType(u.type),
          name: u.name || `Unit #${id}`,
          parent_id: parentId,
          children: [],
          order: Number.isFinite(u.order) ? u.order : 0,
          _raw: u,
        };
      });

      const byId = new Map(nodes.map((n) => [n.id, n]));
      const roots = [];
      for (const n of nodes) {
        if (n.parent_id && byId.has(n.parent_id) && n.parent_id !== n.id)
          byId.get(n.parent_id).children.push(n);
        else roots.push(n);
      }

      const typeRank = (t) => ({ center: 0, manage: 1, dept: 2, sector: 3, other: 4 }[t] ?? 9);
      const sortRec = (node) => {
        node.children.sort(
          (a, b) =>
            typeRank(a.type) - typeRank(b.type) ||
            a.order - b.order ||
            a.name.localeCompare(b.name, "ru")
        );
        node.children.forEach(sortRec);
      };
      roots.forEach(sortRec);
      return roots;
    },

    /* ----------------- выбор/сброс ----------------- */
    async onPickNode(raw) {
      if (this.dragMoved) {
        this.dragMoved = false;
        return;
      }
      this.selectedId = String(raw?.id ?? "");
      this.selectedUnit = raw;
      this.showModal = true;
      await this.loadHead(raw?.id);
      this.$emit("pick-node", raw);
    },
    clearSelection() {
      this.selectedId = null;
      this.selectedUnit = null;
      this.showModal = false;
      this.headData = null;
      this.headError = "";
    },
    closeModal() {
      this.clearSelection();
    },
    onChartClick(e) {
      if (this.dragMoved) {
        this.dragMoved = false;
        return;
      }
      const t = e.target;
      if (!(t && typeof t.closest === "function" && t.closest(".node"))) {
        this.clearSelection();
      }
    },
    onKeyDown(e) {
      if (e.key === "Escape") this.clearSelection();
    },

    /* ----------------- руководитель юнита ----------------- */
    async loadHead(unitId) {
      this.headData = null;
      this.headError = "";
      if (!unitId) return;
      try {
        this.headLoading = true;
        const url = `${API_BASE_URL}api/organizations-staff/employees/`;
        const { data } = await axios.get(url, {
          params: { unit: unitId, is_head: true },
          withCredentials: this.useCredentials,
        });
        const list = Array.isArray(data?.results) ? data.results : Array.isArray(data) ? data : [];
        this.headData = list[0] || null;
      } catch (e) {
        this.headError = e?.response?.statusText || e?.message || "Ошибка загрузки руководителя";
      } finally {
        this.headLoading = false;
      }
    },

    /* ----------------- Пан/зум ----------------- */
    onPointerDown(e) {
      const t = e.target;
      if (t && typeof t.closest === "function" && t.closest(".node")) return;
      if (e.button !== 1) return;
      e.preventDefault();

      const el = this.$refs.chartEl || this.$refs.canvasEl;
      const rect = el.getBoundingClientRect();

      this.dragging = true;
      this.dragMoved = false;
      this.dragStart = { x: e.clientX, y: e.clientY, rectW: rect.width, rectH: rect.height };
      this.viewStart = { x: this.view.x, y: this.view.y };

      try {
        el.setPointerCapture?.(e.pointerId);
      } catch {}
      window.addEventListener("pointermove", this.onPointerMove, { passive: false });
      window.addEventListener("pointerup", this.onPointerUp, { passive: false, once: true });
      window.addEventListener("pointercancel", this.onPointerUp, { passive: false, once: true });
    },
    onMouseDown(e) {
      const t = e.target;
      if (t && typeof t.closest === "function" && t.closest(".node")) return;
      if (!(e.buttons & 4)) return;

      const rect = (this.$refs.chartEl || this.$refs.canvasEl).getBoundingClientRect();
      this.dragging = true;
      this.dragMoved = false;
      this.dragStart = { x: e.clientX, y: e.clientY, rectW: rect.width, rectH: rect.height };
      this.viewStart = { x: this.view.x, y: this.view.y };

      window.addEventListener("mousemove", this.onMouseMove, { passive: false });
      window.addEventListener("mouseup", this.onMouseUp, { passive: true, once: true });
    },
    onPointerMove(e) {
      if (!this.dragging) return;
      if (!(e.buttons & 4)) return;
      e.preventDefault();
      const dx = ((e.clientX - this.dragStart.x) / this.dragStart.rectW) * this.view.w;
      const dy = ((e.clientY - this.dragStart.y) / this.dragStart.rectH) * this.view.h;
      if (Math.abs(dx) > 2 || Math.abs(dy) > 2) this.dragMoved = true;
      this.view.x = this.viewStart.x - dx;
      this.view.y = this.viewStart.y - dy;
    },
    onPointerUp(e) {
      this.dragging = false;
      try {
        (this.$refs.chartEl || this.$refs.canvasEl).releasePointerCapture?.(e.pointerId);
      } catch {}
      window.removeEventListener("pointermove", this.onPointerMove);
      window.removeEventListener("pointercancel", this.onPointerUp);
    },
    onMouseMove(e) {
      if (!this.dragging) return;
      if (!(e.buttons & 4)) return;
      e.preventDefault();
      const dx = ((e.clientX - this.dragStart.x) / this.dragStart.rectW) * this.view.w;
      const dy = ((e.clientY - this.dragStart.y) / this.dragStart.rectH) * this.view.h;
      if (Math.abs(dx) > 2 || Math.abs(dy) > 2) this.dragMoved = true;
      this.view.x = this.viewStart.x - dx;
      this.view.y = this.viewStart.y - dy;
    },
    onMouseUp() {
      this.dragging = false;
      window.removeEventListener("mousemove", this.onMouseMove);
    },
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

    /* ----------------- Fit / Zoom при старте ----------------- */
    setZoom(scale = 1, center = null) {
      if (scale <= 0) return;
      const cx = center?.x ?? this.view.x + this.view.w / 2;
      const cy = center?.y ?? this.view.y + this.view.h / 2;
      const newW = this.view.w / scale;
      const newH = this.view.h / scale;
      this.view.x = cx - newW / 2;
      this.view.y = cy - newH / 2;
      this.view.w = Math.max(400, Math.min(6000, newW));
      this.view.h = Math.max(300, Math.min(4000, newH));
    },
    fitToContent(pad = 100) {
      this.$nextTick(() => {
        const svg = this.$refs.chartEl;
        if (!svg) return;
        const nodesG = svg.querySelector(".nodes");
        if (!nodesG) return;
        const bb = nodesG.getBBox();
        if (!bb || !isFinite(bb.width) || !isFinite(bb.height)) return;
        const rect = this.$refs.canvasEl.getBoundingClientRect();
        const aspect = rect.width / rect.height;
        let w = Math.max(1, bb.width + pad * 2);
        let h = Math.max(1, bb.height + pad * 2);
        const bAspect = w / h;
        if (bAspect > aspect) h = w / aspect;
        else w = h * aspect;
        const extraX = (w - (bb.width + pad * 2)) / 2;
        const extraY = (h - (bb.height + pad * 2)) / 2;
        this.view.x = bb.x - pad - extraX;
        this.view.y = bb.y - pad - extraY;
        this.view.w = w;
        this.view.h = h;
      });
    },

    /* ----------------- Создание: структура и сотрудник ----------------- */
    async handleCreateUnit(form) {
      // form: { name, type, parentId, addHead, head:{full_name,position,phone,email,is_director} }
      try {
        // 1) создать юнит
        const payloadUnit = {
          name: form.name,
          type: form.type,
          parent_id: form.parentId || null,
        };
        const { data: unit } = await axios.post(
          `${API_BASE_URL}api/organizations-staff/units/`,
          payloadUnit,
          { withCredentials: this.useCredentials }
        );

        // 2) при необходимости — создать руководителя
        if (form.addHead && unit?.id) {
          const head = form.head || {};
          const payloadHead = {
            unit: unit.id,
            full_name: head.full_name,
            position: head.position || "Руководитель",
            phone: head.phone || "",
            email: head.email || "",
            is_head: true,
            is_director: !!head.is_director,
          };
          await axios.post(
            `${API_BASE_URL}api/organizations-staff/employees/`,
            payloadHead,
            { withCredentials: this.useCredentials }
          );
        }

        this.showAddUnit = false;
        await this.fetchData(); // перерисовать
      } catch (e) {
        alert(`Ошибка создания структуры: ${e?.response?.data?.detail || e.message}`);
      }
    },

    async handleCreateEmployee(form) {
      // form: { unitId, full_name, position, phone, email, is_head, is_director }
      try {
        const payload = {
          unit: form.unitId,
          full_name: form.full_name,
          position: form.position || "",
          phone: form.phone || "",
          email: form.email || "",
          is_head: !!form.is_head,
          is_director: !!form.is_director,
        };
        await axios.post(`${API_BASE_URL}api/organizations-staff/employees/`, payload, {
          withCredentials: this.useCredentials,
        });
        this.showAddEmp = false;
        await this.fetchData();
      } catch (e) {
        alert(`Ошибка создания сотрудника: ${e?.response?.data?.detail || e.message}`);
      }
    },
  },
};
</script>

<style scoped>
.orgflat { position: relative; display: flex; flex-direction: column; gap: 12px; height: 100%; color: #17202a; }
.orgflat.dark { color: #e7edf6; }

.topbar {  
  display: grid; 
  grid-template-columns: 1fr auto; 
  align-items: center; 
  padding: 8px 12px; 
  width: 98.2%;
}
.actions { display: flex; gap: 8px; flex-wrap: wrap; }
.meta { font-size: 12px; opacity: .6; }

.btn { padding: 8px 12px; border-radius: 9px; border: 1px solid transparent; background: #f2f4f8; font-weight: 700; cursor: pointer; transition: transform .05s, box-shadow .2s, background .2s; box-shadow: 0 1px 2px rgba(16,24,40,.06); }
.btn:hover { transform: translateY(-1px); }
.btn.add.primary { background: #e7f1ff; border-color: #3086ff33; }
.btn.add.secondary { background: #eef7ef; border-color: #38a16933; }

.canvas { position: relative; flex: 1; background: #f7f8fb; border-radius: 16px; overflow: hidden; box-shadow: inset 0 0 0 1px rgba(16,24,40,.06); min-height: 520px; touch-action: none; z-index: 1; }
.orgflat.dark .canvas { background: radial-gradient(1200px 600px at 30% 20%, #3b4654 0%, #2e3844 60%, #26303a 100%); box-shadow: inset 0 0 0 1px rgba(255,255,255,.04); }

.chart { cursor: grab; width: 100%; height: 100%; user-select: none; display: block; }
.chart.panning { cursor: grabbing; }

.hint { position: absolute; right: 10px; bottom: 8px; font-size: 12px; opacity: .7; background: rgba(0,0,0,.05); color: #3b4654; padding: 4px 8px; border-radius: 8px; }
.orgflat.dark .hint { background: rgba(0,0,0,.25); color: #fff; }

.error-badge { position: absolute; left: 10px; top: 10px; font-size: 12px; background: #fee2e2; color: #b91c1c; padding: 6px 10px; border-radius: 8px; border: 1px solid #fecaca; max-width: 60%; box-shadow: 0 8px 18px rgba(0,0,0,.08); }
</style>
