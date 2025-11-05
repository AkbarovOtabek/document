<template>
  <div class="board" ref="board">
    <div
      class="viewport"
      @wheel.prevent="onWheel"
      @mousedown="onMouseDown"
      @mousemove="onMouseMove"
      @mouseup="onMouseUp"
      @mouseleave="onMouseUp"
    >
      <div class="content" :style="contentStyle">
        <!-- Центр -->
        <div class="node center" :class="nodeClass(keyC(center))" :style="translate(posCenter)">
          <CircleBubble
            :title="center.name"
            :subtitle="center.director?.fio || '—'"
            :role="center.director?.position || 'Директор центра'"
            side="center"
            :dataKey="keyC(center)"
            @focus="focusOn({ key: keyC(center), level: 'center', payload: center, evt: $event })"
          />
        </div>

        <!-- Управления -->
        <template v-for="(m, mi) in center.managements" :key="m.id">
          <div class="node mgmt" :class="nodeClass(keyMU(m))" :style="translate(posMU(mi))">
            <CircleBubble
              :title="m.name"
              :subtitle="m.director?.fio || '—'"
              :role="m.director?.position || 'Директор управления'"
              side="management"
              :dataKey="keyMU(m)"
              @focus="focusOn({ key: keyMU(m), level: 'management', payload: m, evt: $event })"
            />
          </div>

          <!-- Отделы -->
          <template v-for="(d, di) in m.departments" :key="d.id">
            <div
              class="node dep"
              :class="nodeClass(keyDep(d))"
              :style="translate(posDEP(mi, di, m.departments.length))"
            >
              <CircleBubble
                :title="d.name"
                :subtitle="d.head?.fio || '—'"
                :role="d.head?.position || 'Начальник отдела'"
                side="department"
                :dataKey="keyDep(d)"
                @focus="focusOn({ key: keyDep(d), level: 'department', payload: d, evt: $event })"
              />
            </div>

            <!-- Сотрудники -->
            <template v-for="(s, si) in d.staff" :key="s.id">
              <div
                class="node staff"
                :class="nodeClass(keyStaff(s))"
                :style="translate(posSTAFF(mi, di, si, d.staff.length))"
              >
                <CircleBubble
                  :title="fio(s)"
                  :subtitle="''"
                  :role="s.position || 'Сотрудник'"
                  side="staff"
                  :dataKey="keyStaff(s)"
                  @focus="focusOn({ key: keyStaff(s), level: 'staff', payload: s, evt: $event })"
                />
              </div>
            </template>
          </template>
        </template>
      </div>
    </div>

    <!-- Панель информации -->
    <div v-if="infoCard" class="info-panel">
      <div class="info-title">{{ infoCard.title }}</div>
      <div class="info-role">{{ infoCard.role }}</div>
      <div class="info-lines">
        <div class="row" v-for="(ln, i) in infoCard.lines" :key="i">
          <span class="k">{{ ln.k }}:</span>
          <span class="v">{{ ln.v }}</span>
        </div>
      </div>
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
      gapMgmt: 460,
      gapDep: 280,
      gapStaff: 160,
      cx: 0,
      cy: 0,
      bw: 0,
      bh: 0,
      scale: 1,
      minScale: 0.4,
      maxScale: 2.5,
      tx: 0,
      ty: 0,
      activeKey: null,
      infoCard: null,
      isPanning: false,
      panBtn: 1,
      lastX: 0,
      lastY: 0,
    };
  },
  computed: {
    posCenter() {
      return { x: 0, y: 0 };
    },
    contentStyle() {
      return {
        transform: `translate(${this.tx}px, ${this.ty}px) scale(${this.scale})`,
        transformOrigin: "0 0",
      };
    },
  },
  mounted() {
    this.recalcBoard();
    window.addEventListener("resize", this.recalcBoard, { passive: true });
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.recalcBoard);
  },
  methods: {
    keyC(c) {
      return `c:${c.id}`;
    },
    keyMU(m) {
      return `m:${m.id}`;
    },
    keyDep(d) {
      return `d:${d.id}`;
    },
    keyStaff(s) {
      return `s:${s.id}`;
    },

    recalcBoard() {
      const box = this.$refs.board.getBoundingClientRect();
      this.cx = box.width / 2;
      this.cy = box.height / 2;
      this.bw = box.width;
      this.bh = box.height;
    },
    translate(p) {
      return { transform: `translate(calc(-50% + ${p.x}px), calc(-50% + ${p.y}px))` };
    },
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

    // Клик: фокус + приближение + инфо
    focusOn({ key, level, payload, evt }) {
      this.activeKey = key;

      // Центрирование выбранного пузыря
      const boardBox = this.$refs.board.getBoundingClientRect();
      const el = this.$el.querySelector(`[data-key="${key}"]`);
      const rect = el ? el.getBoundingClientRect() : boardBox;

      const bx = rect.left - boardBox.left + rect.width / 2;
      const by = rect.top - boardBox.top + rect.height / 2;
      const cx = boardBox.width / 2;
      const cy = boardBox.height / 2;

      const newScale = Math.min(this.maxScale, Math.max(this.minScale, this.scale * 1.1));
      const wx = (bx - this.tx) / this.scale;
      const wy = (by - this.ty) / this.scale;

      this.scale = newScale;
      this.tx = cx - wx * this.scale;
      this.ty = cy - wy * this.scale;

      // Составляем карточку данных
      this.infoCard = this.composeInfo(level, payload);
    },

    composeInfo(level, payload) {
      if (level === "staff") {
        return {
          title: this.fio(payload),
          role: payload.position || "Сотрудник",
          lines: [
            { k: "Отдел", v: this.findDepartmentName(payload.department) || "—" },
            { k: "Управление", v: this.findManagementName(payload.management) || "—" },
          ],
        };
      }
      if (level === "department") {
        return {
          title: payload.head?.fio || "—",
          role: payload.head?.position || "Начальник отдела",
          lines: [{ k: "Отдел", v: payload.name }],
        };
      }
      if (level === "management") {
        return {
          title: payload.director?.fio || "—",
          role: payload.director?.position || "Директор управления",
          lines: [{ k: "Управление", v: payload.name }],
        };
      }
      if (level === "center") {
        return {
          title: payload.director?.fio || "—",
          role: payload.director?.position || "Директор центра",
          lines: [{ k: "Центр", v: payload.name }],
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

    nodeClass(key) {
      if (!this.activeKey) return null;
      return this.activeKey === key ? "focused" : "faded";
    },

    // Пан/зум
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
      this.isPanning = true;
      this.lastX = e.clientX;
      this.lastY = e.clientY;
    },
    onMouseMove(e) {
      if (!this.isPanning) return;
      const dx = e.clientX - this.lastX;
      const dy = e.clientY - this.lastY;
      this.tx += dx;
      this.ty += dy;
      this.lastX = e.clientX;
      this.lastY = e.clientY;
    },
    onMouseUp() {
      this.isPanning = false;
    },
  },
};
</script>

<style scoped>
.board {
  position: relative;
  width: 100%;
  height: 80vh;
  min-height: 680px;
  background: #555;
  overflow: hidden;
}
.viewport {
  position: absolute;
  inset: 0;
  overflow: hidden;
  cursor: grab;
}
.viewport:active {
  cursor: grabbing;
}
.content {
  position: absolute;
  inset: 0;
}

/* Визуальные состояния */
.node {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  transition: all 0.2s ease;
}
.node.focused {
  z-index: 10;
  transform: translate(-50%, -50%) scale(1.18);
}
.node.faded {
  opacity: 0.28;
  filter: grayscale(70%);
}

/* Карточка информации */
.info-panel {
  position: absolute;
  right: 20px;
  bottom: 20px;
  width: 320px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  box-shadow: 0 14px 30px rgba(0, 0, 0, 0.25);
  padding: 12px;
  z-index: 999;
}
.info-title {
  font-weight: 700;
  font-size: 16px;
}
.info-role {
  color: #475569;
  margin-top: 2px;
}
.info-lines {
  margin-top: 8px;
  display: grid;
  gap: 6px;
}
.info-lines .row .k {
  color: #64748b;
  margin-right: 6px;
}
.info-lines .row .v {
  font-weight: 600;
}
</style>
