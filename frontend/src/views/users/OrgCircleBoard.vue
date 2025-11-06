<template>
  <div class="board" ref="board">
    <div
      class="viewport"
      @wheel.prevent="onWheel"
      @mousedown="onMouseDown"
      @mousemove="onMouseMove"
      @mouseup="onMouseUp"
      @mouseleave="onMouseUp"
      @click.self="clearFocus"           <!-- клик по фону снимает выделение -->
    >
      <div class="content" :style="contentStyle" @click.self="clearFocus">
        <!-- ЛИНИИ -->
        <svg class="wires" :width="bw" :height="bh">
          <g>
            <template v-for="(e, i) in graph.edges" :key="i">
              <line
                :x1="cx + e.a.x" :y1="cy + e.a.y"
                :x2="cx + e.b.x" :y2="cy + e.b.y"
                :class="{ 'hl': isHighlighted(e) }"
              />
              <circle :cx="cx + e.a.x" :cy="cy + e.a.y" r="3" :class="{ 'hl': isHighlighted(e) }" />
              <circle :cx="cx + e.b.x" :cy="cy + e.b.y" r="3" :class="{ 'hl': isHighlighted(e) }" />
            </template>
          </g>
        </svg>

        <!-- Центр -->
        <div class="node center" :class="nodeClass(keyC(center), 'center')" :style="translate(posCenter)">
          <CircleBubble
            :title="center.name"
            :subtitle="center.director?.fio || '—'"
            :role="center.director?.position || 'Директор центра'"
            side="center"
            :dataKey="keyC(center)"
            @focus="focusOn({ key: keyC(center), level: 'center', payload: center })"
          />
        </div>

        <!-- Управления / Отделы / Сотрудники -->
        <template v-for="(m, mi) in center.managements" :key="m.id">
          <div class="node mgmt" :class="nodeClass(keyMU(m), 'management')" :style="translate(posMU(mi))">
            <CircleBubble
              :title="m.name"
              :subtitle="m.director?.fio || '—'"
              :role="m.director?.position || 'Директор управления'"
              side="management"
              :dataKey="keyMU(m)"
              @focus="focusOn({ key: keyMU(m), level: 'management', payload: m, ctx: { mi } })"
            />
          </div>

          <template v-for="(d, di) in m.departments" :key="d.id">
            <div class="node dep" :class="nodeClass(keyDep(d), 'department')" :style="translate(posDEP(mi, di, m.departments.length))">
              <CircleBubble
                :title="d.name"
                :subtitle="d.head?.fio || '—'"
                :role="d.head?.position || 'Начальник отдела'"
                side="department"
                :dataKey="keyDep(d)"
                @focus="focusOn({ key: keyDep(d), level: 'department', payload: d, ctx: { mi, di, m } })"
              />
            </div>

            <template v-for="(s, si) in d.staff" :key="s.id">
              <div class="node staff" :class="nodeClass(keyStaff(s), 'staff')" :style="translate(posSTAFF(mi, di, si, d.staff.length))">
                <CircleBubble
                  :title="fio(s)"
                  :subtitle="''"
                  :role="s.position || 'Сотрудник'"
                  side="staff"
                  :dataKey="keyStaff(s)"
                  @focus="focusOn({ key: keyStaff(s), level: 'staff', payload: s, ctx: { mi, di, si, m, d } })"
                />
              </div>
            </template>
          </template>
        </template>
      </div>
    </div>

    <!-- Карточка информации -->
    <div v-if="infoCard" class="info-panel">
      <div class="info-title">{{ infoCard.title }}</div>
      <div class="info-role">{{ infoCard.role }}</div>

      <div class="info-lines">
        <div class="row" v-for="(ln, i) in infoCard.lines" :key="i">
          <span class="k">{{ ln.k }}:</span>
          <span class="v">{{ ln.v }}</span>
        </div>
      </div>

      <!-- Дополнительные «сырые» поля (если есть) -->
      <div v-if="infoCard.extra && infoCard.extra.length" class="info-extra">
        <div class="extra-title">Дополнительно</div>
        <div class="row" v-for="(ln, i) in infoCard.extra" :key="'x'+i">
          <span class="k">{{ ln.k }}:</span>
          <span class="v">{{ ln.v }}</span>
        </div>
      </div>

      <!-- Кнопка закрыть -->
      <button class="close-btn" @click="clearFocus" title="Скрыть">×</button>
    </div>
  </div>
</template>

<script>
import CircleBubble from "./CircleBubble.vue";

export default {
  name: "OrgCircleBoard",
  components: { CircleBubble },
  props: { center: { type: Object, required: true } },
  data() {
    return {
      gapMgmt: 340,
      gapDep: 220,
      gapStaff: 140,
      cx: 0, cy: 0, bw: 0, bh: 0,
      scale: 1, minScale: 0.4, maxScale: 2.5,
      tx: 0, ty: 0,
      activeKey: null, infoCard: null,
      isPanning: false, panBtn: 1, lastX: 0, lastY: 0,
    };
  },
  computed: {
    posCenter() { return { x: 0, y: 0 }; },
    contentStyle() {
      return { transform: `translate(${this.tx}px, ${this.ty}px) scale(${this.scale})`, transformOrigin: "0 0" };
    },

    /* граф: рёбра + родительские связи */
    graph() {
      const edges = [];
      const parentOf = {};
      this.center.managements?.forEach((m, mi) => {
        const kC = this.keyC(this.center);
        const kM = this.keyMU(m);
        edges.push({ a: this.posCenter, b: this.posMU(mi), aKey: kC, bKey: kM });
        parentOf[kM] = kC;

        m.departments?.forEach((d, di) => {
          const kD = this.keyDep(d);
          edges.push({ a: this.posMU(mi), b: this.posDEP(mi, di, m.departments.length), aKey: kM, bKey: kD });
          parentOf[kD] = kM;

          d.staff?.forEach((s, si) => {
            const kS = this.keyStaff(s);
            edges.push({ a: this.posDEP(mi, di, m.departments.length), b: this.posSTAFF(mi, di, si, d.staff.length), aKey: kD, bKey: kS });
            parentOf[kS] = kD;
          });
        });
      });
      return { edges, parentOf };
    },

    /* цепочка подсветки до центра */
    highlighted() {
      const set = new Set();
      let k = this.activeKey;
      const parentOf = this.graph.parentOf;
      while (k && parentOf[k]) {
        const p = parentOf[k];
        set.add(`${k}|${p}`); // child|parent
        k = p;
      }
      return set;
    },
  },
  mounted() {
    this.recalcBoard();
    window.addEventListener("resize", this.recalcBoard, { passive: true });
    window.addEventListener("keydown", this.onKeyDown); // Esc сброс
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.recalcBoard);
    window.removeEventListener("keydown", this.onKeyDown);
  },
  methods: {
    keyC(c) { return `c:${c.id}`; },
    keyMU(m) { return `m:${m.id}`; },
    keyDep(d) { return `d:${d.id}`; },
    keyStaff(s) { return `s:${s.id}`; },

    recalcBoard() {
      const box = this.$refs.board.getBoundingClientRect();
      this.cx = box.width / 2; this.cy = box.height / 2;
      this.bw = box.width;     this.bh = box.height;
    },
    translate(p) { return { transform: `translate(calc(-50% + ${p.x}px), calc(-50% + ${p.y}px))` }; },
    polar(i, n, r, shift = 0) {
      const a = (i / Math.max(1, n)) * 2 * Math.PI - Math.PI / 2 + shift;
      return { x: Math.cos(a) * r, y: Math.sin(a) * r };
    },
    posMU(mi) {
      const n = this.center?.managements?.length || 1;
      const r = this.gapMgmt + Math.max(0, n - 8) * 16;
      return this.polar(mi, n, r);
    },
    posDEP(mi, di, dn) {
      const mu = this.posMU(mi);
      const localR = this.gapDep + Math.max(0, dn - 6) * 12;
      const local = this.polar(di, dn, localR, (mi * 10 * Math.PI) / 180);
      return { x: mu.x + local.x, y: mu.y + local.y };
    },
    posSTAFF(mi, di, si, sn) {
      const dep = this.posDEP(mi, di, 1);
      const localR = this.gapStaff + Math.max(0, sn - 8) * 8;
      const local = this.polar(si, sn, localR, ((mi + di) * 8 * Math.PI) / 180);
      return { x: dep.x + local.x, y: dep.y + local.y };
    },
    fio(s) {
      if (!s) return "—";
      if (s.fio) return s.fio;
      const parts = [s.last_name, s.first_name, s.second_name].filter(Boolean);
      return parts.length ? parts.join(" ") : s.username || "—";
    },

    /* КЛИК: выбор + формирование полной карточки, без зума */
    focusOn({ key, level, payload, ctx = {} }) {
      this.activeKey = key;
      this.infoCard = this.composeInfo(level, payload, ctx);
    },

    clearFocus() {
      this.activeKey = null;
      this.infoCard = null;
    },
    onKeyDown(e) {
      if (e.key === "Escape") this.clearFocus();
    },

    /* Формируем «полные» данные */
    composeInfo(level, payload, ctx) {
      const lines = [];
      const extra = [];

      const push = (k, v) => { if (v !== undefined && v !== null && v !== "") lines.push({ k, v: String(v) }); };
      const pushExtra = (obj, skip = []) => {
        if (!obj || typeof obj !== "object") return;
        const flatKeys = Object.keys(obj).filter(k =>
          !Array.isArray(obj[k]) && typeof obj[k] !== "object" && !skip.includes(k)
        );
        for (const k of flatKeys) extra.push({ k, v: String(obj[k]) });
      };

      if (level === "staff") {
        const s = payload;
        push("ФИО", this.fio(s));
        push("Должность", s.position || "Сотрудник");
        push("Отдел", this.findDepartmentName(s.department) || ctx?.d?.name || "—");
        push("Управление", this.findManagementName(s.management) || ctx?.m?.name || "—");

        // типовые возможные поля
        push("Email", s.email);
        push("Телефон", s.phone);
        push("Логин", s.username);
        push("ID", s.id);

        // прочие простые поля сотрудника
        pushExtra(s, ["id","fio","position","email","phone","username","department","management"]);

        return { title: this.fio(s), role: s.position || "Сотрудник", lines, extra };
      }

      if (level === "department") {
        const d = payload;
        push("Отдел", d.name);
        push("Начальник", d.head?.fio || "—");
        push("Должность начальника", d.head?.position || "Начальник отдела");
        push("ID", d.id);
        pushExtra(d, ["id","name","head","staff","management"]);
        return { title: d.head?.fio || d.name, role: d.head?.position || "Начальник отдела", lines, extra };
      }

      if (level === "management") {
        const m = payload;
        push("Управление", m.name);
        push("Директор", m.director?.fio || "—");
        push("Должность директора", m.director?.position || "Директор управления");
        push("ID", m.id);
        pushExtra(m, ["id","name","director","departments"]);
        return { title: m.director?.fio || m.name, role: m.director?.position || "Директор управления", lines, extra };
      }

      if (level === "center") {
        const c = payload;
        push("Центр", c.name);
        push("Директор", c.director?.fio || "—");
        push("Должность директора", c.director?.position || "Директор центра");
        push("ID", c.id);
        pushExtra(c, ["id","name","director","managements"]);
        return { title: c.director?.fio || c.name, role: c.director?.position || "Директор центра", lines, extra };
      }

      return null;
    },

    findManagementName(m) {
      const id = typeof m === "object" ? m?.id : m;
      return this.center.managements.find((x) => x.id === id)?.name;
    },
    findDepartmentName(d) {
      const id = typeof d === "object" ? d?.id : d;
      for (const mu of this.center.managements)
        for (const dep of mu.departments) if (dep.id === id) return dep.name;
      return null;
    },

    nodeClass(key, levelClass) {
      if (!this.activeKey) return levelClass;
      return this.activeKey === key ? `focused ${levelClass}` : `faded ${levelClass}`;
    },

    // Зум колесом и панорамирование
    onWheel(e) {
      const factor = Math.exp(-e.deltaY * 0.001 * 0.2);
      const newScale = Math.min(this.maxScale, Math.max(this.minScale, this.scale * factor));
      const rect = this.$refs.board.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;
      const wx = (mx - this.tx) / this.scale;
      const wy = (my - this.ty) / this.scale;
      this.scale = newScale;
      this.tx = mx - wx * this.scale;
      this.ty = my - wy * this.scale;
    },
    onMouseDown(e) {
      if (e.button !== this.panBtn) return;
      this.isPanning = true; this.lastX = e.clientX; this.lastY = e.clientY;
    },
    onMouseMove(e) {
      if (!this.isPanning) return;
      const dx = e.clientX - this.lastX, dy = e.clientY - this.lastY;
      this.tx += dx; this.ty += dy; this.lastX = e.clientX; this.lastY = e.clientY;
    },
    onMouseUp() { this.isPanning = false; },

    isHighlighted(e) {
      return this.highlighted.has(`${e.bKey}|${e.aKey}`); // b=child, a=parent
    },
  },
};
</script>

<style scoped>
.board {
  position: relative; width: 100%; height: 80vh; min-height: 680px;
  background: #2b3441;
  overflow: hidden;
}
.viewport { position: absolute; inset: 0; overflow: hidden; cursor: grab; }
.viewport:active { cursor: grabbing; }
.content { position: absolute; inset: 0; }

/* ЛИНИИ: сплошные. По умолчанию приглушённые, у цепочки — яркие */
.wires { position:absolute; inset:0; pointer-events:none; }
.wires line { stroke:#8fa3b7; stroke-width:2; stroke-linecap:round; opacity:.55; }
.wires circle { fill:#8fa3b7; opacity:.55; }
.wires .hl { opacity:1; stroke:#e9f2ff; fill:#e9f2ff; }

/* Узлы и состояния: «подъём» активного как параллакс */
.node { position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); transition: transform .22s ease, opacity .2s ease, filter .2s ease; }
.node.focused { z-index:20; transform: translate(-50%, -50%) translateY(-80px); filter: drop-shadow(0 18px 36px rgba(0,0,0,.4)); }
.node.faded { opacity:.32; filter:grayscale(50%); }

/* Инфо-панель */
.info-panel{
  position:absolute; right:20px; bottom:20px; width:340px;
  background:#fff; border:1px solid #e2e8f0; border-radius:12px;
  box-shadow:0 14px 30px rgba(0,0,0,.25); padding:12px 14px 16px; z-index:999;
}
.info-title{ font-weight:700; font-size:16px; }
.info-role{ color:#475569; margin-top:2px; }
.info-lines{ margin-top:8px; display:grid; gap:6px; }
.info-extra{ margin-top:10px; border-top:1px dashed #e2e8f0; padding-top:8px; }
.info-lines .row .k, .info-extra .row .k{ color:#64748b; margin-right:6px; }
.info-lines .row .v, .info-extra .row .v{ font-weight:600; word-break: break-word; }

/* Кнопка закрыть */
.close-btn{
  position:absolute; top:8px; right:10px; width:28px; height:28px;
  border:none; border-radius:6px; background:#f1f5f9; cursor:pointer; font-size:18px; line-height:1;
}
.close-btn:hover{ background:#e2e8f0; }
</style>
