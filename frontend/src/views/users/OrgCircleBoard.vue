<template>
  <div class="board" ref="board">
    <div
      class="viewport"
      @wheel.prevent="onWheel"
      @mousedown="onMouseDown"
      @mousemove="onMouseMove"
      @mouseup="onMouseUp"
      @mouseleave="onMouseUp"
      @click.self="clearFocus"
    >
      <div class="content" :style="contentStyle" @click.self="clearFocus">
        <!-- ЛИНИИ -->
        <svg class="wires" :width="bw" :height="bh">
          <g>
            <template v-for="(e, i) in graph.edges" :key="i">
              <line
                :x1="cx + e.da.x" :y1="cy + e.da.y"
                :x2="cx + e.db.x" :y2="cy + e.db.y"
                vector-effect="non-scaling-stroke"
                stroke-linecap="round"
                :class="{ hl: isHighlighted(e) }"
              />
              <circle :cx="cx + e.db.x" :cy="cy + e.db.y" r="4"
                vector-effect="non-scaling-stroke"
                :class="{ hl: isHighlighted(e) }"/>
              <circle :cx="cx + e.da.x" :cy="cy + e.da.y" r="4"
                vector-effect="non-scaling-stroke"
                :class="{ hl: isHighlighted(e) }"/>
            </template>
          </g>
        </svg>

        <!-- Центр -->
        <div class="node center" :class="nodeClass(keyC(center), 'center')" :style="translate(posCenter)">
          <CircleBubble
            :title="center.name"
            :subtitle="center.director?.fio || '—'"
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

    <!-- Инфо-панель -->
    <div v-if="infoCard" class="info-panel">
      <div class="ip-header">
        <div class="ip-avatar" aria-hidden="true">
          <svg viewBox="0 0 24 24">
            <circle cx="12" cy="5" r="3"/>
            <path d="M4 20a8 8 0 0 1 16 0" />
          </svg>
        </div>

        <div class="ip-titles">
          <div class="ip-title">{{ infoCard.title }}</div>
          <div class="ip-role">{{ infoCard.role }}</div>
        </div>

        <button
          v-if="canEdit && infoCard"
          class="ip-edit"
          @click.stop="onEdit"
          title="Редактировать"
          aria-label="Редактировать"
        >✎</button>

        <button class="ip-close" @click="clearFocus" title="Скрыть" aria-label="Скрыть">✕</button>
      </div>

      <div class="ip-body">
        <div class="ip-row" v-for="(ln, i) in infoCard.lines" :key="i">
          <div class="k">{{ ln.k }}</div>
          <div class="v">{{ ln.v }}</div>
        </div>
      </div>

      <details v-if="infoCard.extra && infoCard.extra.length" class="ip-extra">
        <summary>Дополнительно</summary>
        <div class="ip-body">
          <div class="ip-row" v-for="(ln, i) in infoCard.extra" :key="'x'+i">
            <div class="k">{{ ln.k }}</div>
            <div class="v">{{ ln.v }}</div>
          </div>
        </div>
      </details>
    </div>
  </div>
</template>

<script>
import CircleBubble from "./CircleBubble.vue";

export default {
  name: "OrgCircleBoard",
  components: { CircleBubble },
  props: {
    center: { type: Object, required: true },
    canEdit: { type: Boolean, default: true },
  },
  emits: ["edit-entity"],
  data() {
    return {
      personCache: new Map(),
      gapMgmt: 650,
      gapDep: 340,
      gapStaff: 200,
      cx: 0, cy: 0, bw: 0, bh: 0,
      scale: 0.5, minScale: 0.1, maxScale: 2.5,
      tx: 400, ty: 400,
      activeKey: null, infoCard: null,
      isPanning: false, panBtn: 1, lastX: 0, lastY: 0,   // panBtn=1 → средняя кнопка (Mouse3)
    };
  },
  computed: {
    posCenter() { return { x: 0, y: 0 }; },
    contentStyle() {
      return { transform: `translate(${this.tx}px, ${this.ty}px) scale(${this.scale})`, transformOrigin: "0 0" };
    },
    peopleIndex() {
      const by = new Map();
      const put = (k, v) => { if (k !== undefined && k !== null && k !== "") by.set(String(k), v); };

      this.center?.managements?.forEach(m => {
        m?.departments?.forEach(d => {
          d?.staff?.forEach(s => {
            put(s.id, s);
            put(s.username, s);
            put(s.slug, s);
            if (s.person_id) put(s.person_id, s);
            if (s.user_id)   put(s.user_id, s);
          });
        });
        if (m?.director && typeof m.director === 'object') {
          const s = m.director;
          put(s.id, s); put(s.username, s); put(s.slug, s);
        }
      });

      if (this.center?.director && typeof this.center.director === 'object') {
        const s = this.center.director;
        put(s.id, s); put(s.username, s); put(s.slug, s);
      }
      return by;
    },
    graph() {
      const overdraw = 2;
      const extend = (A, B, t = overdraw) => {
        const dx = B.x - A.x, dy = B.y - A.y;
        const len = Math.max(1, Math.hypot(dx, dy));
        const clamped = Math.min(t, (len - 1) / 2);
        const nx = dx / len, ny = dy / len;
        return {
          a: { x: A.x - nx * clamped, y: A.y - ny * clamped },
          b: { x: B.x + nx * clamped, y: B.y + ny * clamped },
        };
      };

      const edges = [];
      const parentOf = {};

      this.center.managements?.forEach((m, mi) => {
        const kC = this.keyC(this.center);
        const kM = this.keyMU(m);
        const A = this.posCenter, B = this.posMU(mi);
        const { a, b } = extend(A, B);
        edges.push({ a: A, b: B, da: a, db: b, aKey: kC, bKey: kM });
        parentOf[kM] = kC;

        m.departments?.forEach((d, di) => {
          const kD = this.keyDep(d);
          const A2 = this.posMU(mi), B2 = this.posDEP(mi, di, m.departments.length);
          const { a: a2, b: b2 } = extend(A2, B2);
          edges.push({ a: A2, b: B2, da: a2, db: b2, aKey: kM, bKey: kD });
          parentOf[kD] = kM;

          d.staff?.forEach((s, si) => {
            const kS = this.keyStaff(s);
            const A3 = this.posDEP(mi, di, m.departments.length), B3 = this.posSTAFF(mi, di, si, d.staff.length);
            const { a: a3, b: b3 } = extend(A3, B3);
            edges.push({ a: A3, b: B3, da: a3, db: b3, aKey: kD, bKey: kS });
            parentOf[kS] = kD;
          });
        });
      });

      return { edges, parentOf };
    },
    highlighted() {
      const set = new Set();
      let k = this.activeKey;
      const parentOf = this.graph.parentOf;
      while (k && parentOf[k]) {
        const p = parentOf[k];
        set.add(`${k}|${p}`);
        k = p;
      }
      return set;
    },
  },
  mounted() {
    this.recalcBoard();
    window.addEventListener("resize", this.recalcBoard, { passive: true });
    window.addEventListener("keydown", this.onKeyDown);
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.recalcBoard);
    window.removeEventListener("keydown", this.onKeyDown);
  },
  methods: {
    onEdit() {
      if (!this.infoCard) return;
      this.$emit("edit-entity", {
        level: this.infoCard.level,
        entity: this.infoCard.entity,
        ids: this.infoCard.ids || {},
        ctx: this.infoCard.ctx || {}
      });
    },

    keyC(c) { return `c:${c.id}`; },
    keyMU(m) { return `m:${m.id}`; },
    keyDep(d) { return `d:${d.id}`; },
    keyStaff(s) { return `s:${s.id}`; },

    resolvePerson(p) {
      if (p && typeof p === 'object') return p;
      const cand = this.peopleIndex.get(String(p));
      return cand || null;
    },
    async fetchJSON(url) {
      const r = await fetch(url, { credentials: "include" });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return await r.json();
    },
    pickKey(p) {
      if (!p) return null;
      return p.id ?? p.user_id ?? p.person_id ?? p.username ?? p.slug ?? null;
    },
    async fetchPersonRemote(key) {
      if (!key) return null;
      const tryDetail = async () => {
        if (/^\d+$/.test(String(key))) {
          try { return await this.fetchJSON(`/api/staff/users/${key}/`); } catch {}
        }
        return null;
      };
      const tryQuery = async () => {
        const variants = [
          `?id=${encodeURIComponent(key)}`,
          `?username=${encodeURIComponent(key)}`,
          `?slug=${encodeURIComponent(key)}`
        ];
        for (const q of variants) {
          try {
            const res = await this.fetchJSON(`/api/staff/users/${q}`);
            const arr = Array.isArray(res) ? res
                      : Array.isArray(res?.results) ? res.results
                      : res ? [res] : [];
            if (arr.length) return arr[0];
          } catch {}
        }
        return null;
      };
      return (await tryDetail()) ?? (await tryQuery());
    },
    mergePerson(base, extra) {
      if (!extra) return base;
      const out = { ...(base || {}) };
      for (const [k, v] of Object.entries(extra)) {
        if (v !== undefined && v !== null && v !== "") out[k] = v;
      }
      out.fio = out.fio || out.full_name || [out.last_name, out.first_name, out.second_name].filter(Boolean).join(" ");
      return out;
    },
    async ensurePerson(p) {
      if (p && typeof p === "object" && (p.email || p.phone || p.lotus)) return p;
      const idxHit = this.resolvePerson(p);
      const key = this.pickKey(idxHit || p);
      if (!key) return idxHit || (typeof p === "object" ? p : null);
      if (this.personCache.has(String(key))) {
        return this.mergePerson(idxHit || p, this.personCache.get(String(key)));
      }
      const remote = await this.fetchPersonRemote(key);
      if (remote) this.personCache.set(String(key), remote);
      return this.mergePerson(idxHit || p, remote);
    },

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

    clearFocus() {
      this.activeKey = null;
      this.infoCard = null;
    },
    onKeyDown(e) {
      if (e.key === "Escape") this.clearFocus();
    },

    async focusOn({ key, level, payload, ctx = {} }) {
      this.activeKey = key;
      this.infoCard = await this.composeInfo(level, payload, ctx);
    },
    translatePosition(pos) {
      if (!pos) return "—";
      const map = {
        director: "Директор",
        deputy_director: "Заместитель директора (по управлению)",
        head_of_department: "Начальник отдела",
        chief_expert: "Главный эксперт",
        lead_expert: "Ведущий эксперт",
        expert_l1: "Эксперт первого уровня",
        employee: "Сотрудник",
        records_clerk: "Делопроизводитель",
      };
      const key = String(pos).trim().toLowerCase();
      return map[key] || pos;
    },
    async composeInfo(level, payload, ctx) {
      const lines = [];
      const extra = [];
      const push = (k, v) => { if (v !== undefined && v !== null && v !== "") lines.push({ k, v: String(v) }); };
      const pushExtra = (obj, skip = []) => {
        if (!obj || typeof obj !== "object") return;
        const keys = Object.keys(obj).filter(k =>
          !Array.isArray(obj[k]) && typeof obj[k] !== "object" && !skip.includes(k)
        );
        for (const k of keys) extra.push({ k, v: String(obj[k]) });
      };

      // сотрудник
      if (level === "staff") {
        const s = await this.ensurePerson(payload);
        const depName = this.findDepartmentName(s.department) || ctx?.d?.name || "—";
        const mName   = this.findManagementName(s.management) || ctx?.m?.name || "—";

        push("ФИО", this.fio(s));
        push("Должность", this.translatePosition(s.position) || "Сотрудник");
        push("Отдел", depName);
        push("Управление", mName);
        push("Lotus", s.lotus);
        push("Email", s.email || s.work_email);
        push("Телефон", s.phone || s.work_phone);
        push("Логин", s.username);
        pushExtra(s, ["id","fio","full_name","position","email","work_email","phone","work_phone","username","department","management","slug","role","management_flag","is_active"]);

        return {
          title: this.fio(s),
          role: s.position || "Сотрудник",
          lines, extra,
          level,
          entity: s,
          ids: {
            centerId: this.center?.id,
            managementId: ctx?.m?.id || s.management,
            departmentId: ctx?.d?.id || s.department,
            staffId: s.id ?? s.user_id ?? s.person_id
          },
          ctx
        };
      }

      // отдел
      if (level === "department") {
        const d = payload;
        const head = await this.ensurePerson(d.head ?? d.head_id ?? d.manager ?? d.manager_id);

        push("Отдел", d.name);
        push("Управление", this.findManagementName(d.management) || ctx?.m?.name || "—");
        push("Начальник", this.fio(head) || "—");
        push("Должность начальника", this.translatePosition(head?.position) || "Начальник отдела");
        if (head) {
          push("Lotus", head.lotus);
          push("Email", head.email || head.work_email);
          push("Телефон", head.phone || head.work_phone);
          push("Логин", head.username);
        }
        pushExtra(d, ["id","name","head","head_id","management","staff","slug"]);

        return {
          title: this.fio(head) || d.name,
          role: head?.position || "Начальник отдела",
          lines, extra,
          level,
          entity: d,
          ids: {
            centerId: this.center?.id,
            managementId: ctx?.m?.id || d.management,
            departmentId: d.id
          },
          ctx
        };
      }

      // управление
      if (level === "management") {
        const m = payload;
        const dir = await this.ensurePerson(m.director ?? m.director_id);

        push("Управление", m.name);
        push("Директор", this.fio(dir) || "—");
        push("Должность директора", this.translatePosition(dir?.position) || "Директор управления");
        if (dir) {
          push("Lotus", dir.lotus);
          push("Email", dir.email || dir.work_email);
          push("Телефон", dir.phone || dir.work_phone);
          push("Логин", dir.username);
        }
        pushExtra(m, ["id","name","director","director_id","departments","slug"]);

        return {
          title: this.fio(dir) || m.name,
          role: dir?.position || "Директор управления",
          lines, extra,
          level,
          entity: m,
          ids: { centerId: this.center?.id, managementId: m.id },
          ctx
        };
      }

      // центр
      if (level === "center") {
        const c = payload;
        const dir = await this.ensurePerson(c.director ?? c.director_id);

        push("Центр", c.name);
        push("Директор", this.fio(dir) || "—");
        push("Должность директора", this.translatePosition(dir?.position) || "Директор центра");
        if (dir) {
          push("Lotus", dir.lotus);
          push("Email", dir.email || dir.work_email);
          push("Телефон", dir.phone || dir.work_phone);
          push("Логин", dir.username);
        }
        pushExtra(c, ["id","name","director","director_id","managements","slug"]);

        return {
          title: this.fio(dir) || c.name,
          role: dir?.position || "Директор центра",
          lines, extra,
          level,
          entity: c,
          ids: { centerId: c.id },
          ctx
        };
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

    // Зум колесом
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

    // Панорамирование — средней кнопкой (Mouse3)
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
      return this.highlighted.has(`${e.bKey}|${e.aKey}`);
    },
  },
};
</script>

<style scoped>
.board {
  position: relative; width: 100%; height: 83vh; min-height: 680px;
  background: #2b3441;
  overflow: hidden;
}
.viewport { position: absolute; inset: 0; overflow: hidden; cursor: grab; }
.viewport:active { cursor: grabbing; }
.content { position: absolute; inset: 0; }

/* Линии */
.wires { position:absolute; inset:0; pointer-events:none; }
.wires line { stroke:#8fa3b7; stroke-width:2; stroke-linecap:round; opacity:.55; }
.wires circle { fill:#8fa3b7; opacity:.55; }
.wires .hl{
  opacity: 1;
  stroke: #ffffff;
  fill:   #ffffff;
  stroke-width: 7;
  filter: drop-shadow(0 0 6px rgba(255,255,255,.75));
}

/* Узлы */
.node { position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); transition: transform .22s ease, opacity .2s ease, filter .2s ease; }
.node.focused { z-index:20; transform: translate(-50%, -50%) translateY(-80px); filter: drop-shadow(0 18px 36px rgba(0,0,0,.4)); }
.node.faded { opacity:1; filter:grayscale(80%); }

/* Инфо-панель */
.info-panel{
  --acc: #8b5cf6;
  position:absolute;
  right:20px; bottom:24px;
  min-width:340px; max-width:420px;
  padding:12px;
  border-radius:16px;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(10px) saturate(120%);
  border: 1px solid rgba(148, 163, 184, .25);
  box-shadow: 0 20px 50px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.05);
  color:#e5ecf5;
  z-index: 999;
}
.info-panel::after{
  content:"";
  position:absolute;
  bottom:-10px; right:48px;
  width:18px; height:18px;
  transform: rotate(45deg);
  background: inherit;
  border-bottom: 1px solid rgba(148,163,184,.25);
  border-right: 1px solid rgba(148,163,184,.25);
  backdrop-filter: inherit;
}

/* Header */
.ip-header{
  display:flex; align-items:center; gap:10px;
  padding:8px 8px 10px 8px;
  border-bottom: 1px dashed rgba(148,163,184,.25);
}
.ip-avatar{
  width:36px; height:36px; border-radius:10px;
  display:grid; place-items:center;
  background: radial-gradient(120% 120% at 30% 20%, var(--acc), transparent 70%);
  box-shadow: inset 0 0 0 1px rgba(255,255,255,.06);
}
.ip-avatar svg{ width:22px; height:22px; fill:#fff; opacity:.95; }

.ip-titles{ flex:1; min-width:0; }
.ip-title{
  font-weight:800; letter-spacing:.2px; font-size:15px; line-height:1.2;
  color:#f8fbff; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;
}
.ip-role{ margin-top:2px; font-size:12px; color:#a8b3c6; }

.ip-edit{
  border:none; background:transparent; color:#cbd5e1; font-size:16px;
  width:30px; height:30px; border-radius:8px; cursor:pointer; margin-right:4px;
}
.ip-edit:hover{ background:rgba(148,163,184,.12); color:#ffffff; }

.ip-close{
  border:none; background:transparent; color:#cbd5e1; font-size:18px;
  width:30px; height:30px; border-radius:8px; cursor:pointer;
}
.ip-close:hover{ background:rgba(148,163,184,.12); color:#ffffff; }

/* Body */
.ip-body{ padding:10px 4px 2px; display:grid; gap:6px; }
.ip-row{
  display:grid; grid-template-columns: 120px 1fr; align-items:start;
  gap:10px; padding:8px 10px;
  background: linear-gradient(180deg, rgba(255,255,255,.02), rgba(255,255,255,0));
  border: 1px solid rgba(148,163,184,.12);
  border-radius:10px;
}
.ip-row .k{ color:#9fb0c7; font-size:12px; text-transform:uppercase; letter-spacing:.4px; }
.ip-row .v{ color:#eef5ff; font-weight:600; word-break:break-word; }

.ip-extra{ margin-top:8px; border-top:1px dashed rgba(148,163,184,.25); padding-top:6px; }
.ip-extra > summary{
  list-style:none; cursor:pointer; padding:8px 6px; border-radius:8px;
  color:#cfe1ff; font-weight:700; font-size:13px;
}
.ip-extra > summary::-webkit-details-marker{ display:none; }
.ip-extra[open] > summary{ background:rgba(148,163,184,.08); }
.ip-row:hover{ border-color: rgba(148,163,184,.28); background: linear-gradient(180deg, rgba(255,255,255,.04), rgba(255,255,255,.01)); }
</style>
