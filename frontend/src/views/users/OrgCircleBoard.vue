<!-- src/components/users/OrgCircleBoard.vue -->
<template>
  <div class="board" ref="board">
    <!-- Пан/зум слой -->
    <div
      class="viewport"
      @wheel.prevent="onWheel"
      @mousedown="onMouseDown"
      @mousemove="onMouseMove"
      @mouseup="onMouseUp"
      @mouseleave="onMouseUp"
      @contextmenu.prevent
    >
      <div class="content" :style="contentStyle">
        <!-- ====== СЦЕНА (масштабируется/двигается) ====== -->

        <!-- ЛИНИИ: Центр → Управления -->
        <svg class="links" :width="bw" :height="bh" v-if="center?.managements?.length">
          <g stroke="#C9CDD1" stroke-width="1.6" stroke-linecap="round" fill="none">
            <template v-for="(m, mi) in center.managements" :key="'L-m-'+m.id">
              <line
                :x1="cx + posCenter.x" :y1="cy + posCenter.y"
                :x2="cx + posMU(mi).x" :y2="cy + posMU(mi).y"
              />
            </template>
          </g>
        </svg>

        <!-- ЦЕНТР -->
        <div class="node center" :style="translate(posCenter)"
             @mouseenter="hoverKey = keyC(center)" @mouseleave="closeFlyout()">
          <CircleBubble
            :title="center.name"
            :subtitle="center.director?.fio || '—'"
            :role="center.director?.position || 'Директор центра'"
            side="center"
            :dataKey="keyC(center)"
            @openInfo="$emit('open-modal', center.director)"
            @openAdd="openFlyout({ key: keyC(center), level:'center', payload:center })"
          />
        </div>

        <!-- УПРАВЛЕНИЯ -->
        <template v-for="(m, mi) in center.managements" :key="m.id">
          <!-- ЛИНИИ: Управление → Отделы -->
          <svg class="links" :width="bw" :height="bh" v-if="m.departments?.length">
            <g stroke="#D5D8DC" stroke-width="1.4" stroke-linecap="round" fill="none">
              <template v-for="(d, di) in m.departments" :key="'L-d-'+d.id">
                <line
                  :x1="cx + posMU(mi).x" :y1="cy + posMU(mi).y"
                  :x2="cx + posDEP(mi, di, m.departments.length).x"
                  :y2="cy + posDEP(mi, di, m.departments.length).y"
                />
              </template>
            </g>
          </svg>

          <div class="node mgmt" :style="translate(posMU(mi))"
               @mouseenter="hoverKey = keyMU(m)" @mouseleave="closeFlyout()">
            <CircleBubble
              :title="m.name"
              :subtitle="m.director?.fio || '—'"
              :role="m.director?.position || 'Директор управления'"
              side="management"
              :dataKey="keyMU(m)"
              @openInfo="$emit('open-modal', m.director)"
              @openAdd="openFlyout({ key: keyMU(m), level:'management', payload:m })"
            />
          </div>

          <!-- ОТДЕЛЫ -->
          <template v-for="(d, di) in m.departments" :key="d.id">
            <!-- ЛИНИИ: Отдел → Сотрудники -->
            <svg class="links" :width="bw" :height="bh" v-if="d.staff?.length">
              <g stroke="#DFE2E6" stroke-width="1.2" stroke-linecap="round" fill="none">
                <template v-for="(s, si) in d.staff" :key="'L-s-'+s.id">
                  <line
                    :x1="cx + posDEP(mi, di, m.departments.length).x"
                    :y1="cy + posDEP(mi, di, m.departments.length).y"
                    :x2="cx + posSTAFF(mi, di, si, d.staff.length).x"
                    :y2="cy + posSTAFF(mi, di, si, d.staff.length).y"
                  />
                </template>
              </g>
            </svg>

            <div class="node dep" :style="translate(posDEP(mi, di, m.departments.length))"
                 @mouseenter="hoverKey = keyDep(d)" @mouseleave="closeFlyout()">
              <CircleBubble
                :title="d.name"
                :subtitle="d.head?.fio || '—'"
                :role="d.head?.position || 'Начальник отдела'"
                side="department"
                :dataKey="keyDep(d)"
                @openInfo="$emit('open-modal', d.head)"
                @openAdd="openFlyout({ key: keyDep(d), level:'department', payload:d })"
              />
            </div>

            <!-- СОТРУДНИКИ -->
            <template v-for="(s, si) in d.staff" :key="s.id">
              <div class="node staff" :style="translate(posSTAFF(mi, di, si, d.staff.length))"
                   @mouseenter="hoverKey = keyStaff(s)" @mouseleave="closeFlyout()">
                <CircleBubble
                  :title="fio(s)"
                  :subtitle="''"
                  :role="s.position || 'Сотрудник'"
                  side="staff"
                  :dataKey="keyStaff(s)"
                  @openInfo="$emit('open-modal', s)"
                  @openAdd="openFlyout({ key: keyStaff(s), level:'staff', payload:s })"
                />
              </div>
            </template>
          </template>
        </template>
        <!-- ====== /СЦЕНА ====== -->
      </div>
    </div>

    <!-- Flyout — не масштабируется -->
    <div v-if="flyout.show" class="flyout" :style="flyoutStyle"
         @mouseenter="flyout.pin = true" @mouseleave="closeFlyout(true)">
      <button class="fx-btn" title="Добавить руководителя/сотрудника" @click="doFly('addPerson')">
        <svg viewBox="0 0 24 24"><path d="M15 11a4 4 0 1 0-8 0 4 4 0 0 0 8 0z"/><path d="M3 20a7 7 0 0 1 14 0"/><path d="M19 8v6M16 11h6"/></svg>
      </button>
      <button class="fx-btn" title="Добавить дочернюю сущность" @click="doFly('addChild')">
        <svg viewBox="0 0 24 24"><path d="M7 7h10v10H7z"/><path d="M3 3h4v4H3zM17 3h4v4h-4zM3 17h4v4H3zM17 17h4v4h-4z"/></svg>
      </button>
      <button class="fx-btn danger" title="Удалить" @click="doFly('delete')">
        <svg viewBox="0 0 24 24"><path d="M5 12h14"/></svg>
      </button>
      <button class="fx-btn" title="Изменить/настройки" @click="doFly('edit')">
        <svg viewBox="0 0 24 24"><path d="M12 15.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7z"/></svg>
      </button>
    </div>
  </div>
</template>

<script>
import CircleBubble from "./CircleBubble.vue";

export default {
  name: "OrgCircleBoard",
  components: { CircleBubble },
  props: { center: { type: Object, required: true } },
  emits: ["open-modal", "open-add", "action"],
  data() {
    return {
      // БАЗОВЫЕ РАССТОЯНИЯ (регулируй под задачу)
      gapMgmt: 460,  // центр → управление
      gapDep:  280,  // управление → отдел
      gapStaff:160,  // отдел → сотрудник

      // размеры сцены
      cx: 0, cy: 0, bw: 0, bh: 0,

      // hover/flyout
      hoverKey: null,
      flyout: { show:false, x:0, y:0, level:null, payload:null, pin:false },

      // пан/зум (как в Figma)
      scale: 1,
      minScale: 0.4,
      maxScale: 2.5,
      tx: 0,
      ty: 0,
      isPanning: false,
      panBtn: 1, // 1 — средняя кнопка мыши
      lastX: 0,
      lastY: 0,
    };
  },
  computed: {
    posCenter(){ return {x:0, y:0}; },
    flyoutStyle(){ return { left: this.flyout.x + "px", top: this.flyout.y + "px" }; },
    contentStyle(){
      return { transform: `translate(${this.tx}px, ${this.ty}px) scale(${this.scale})`,
               transformOrigin: "0 0" };
    },
  },
  mounted() {
    this.recalcBoard();
    window.addEventListener("resize", this.recalcBoard, { passive:true });
  },
  beforeUnmount(){ window.removeEventListener("resize", this.recalcBoard); },
  methods: {
    // ===== Ключи для конкретных кругов (чтобы flyout открывался около нужного)
    keyC(c){ return `c:${c.id}`; },
    keyMU(m){ return `m:${m.id}`; },
    keyDep(d){ return `d:${d.id}`; },
    keyStaff(s){ return `s:${s.id}`; },

    // ===== Геометрия
    recalcBoard(){
      const box = this.$refs.board.getBoundingClientRect();
      this.cx = box.width / 2; this.cy = box.height / 2;
      this.bw = box.width;     this.bh = box.height;
    },
    translate(p){
      return { transform: `translate(calc(-50% + ${p.x}px), calc(-50% + ${p.y}px))` };
    },
    polar(idx, total, r, shift=0){
      const n = Math.max(1, total);
      const a = (idx/n)*2*Math.PI - Math.PI/2 + shift;
      return { x: Math.cos(a)*r, y: Math.sin(a)*r };
    },
    posMU(mi){
      const n = this.center?.managements?.length || 1;
      const r = this.gapMgmt + Math.max(0, n-8)*16;
      return this.polar(mi, n, r);
    },
    posDEP(mi, di, dn){
      const mu = this.posMU(mi);
      const localR = this.gapDep + Math.max(0, dn-6)*12;
      const local  = this.polar(di, dn, localR, (mi*10)*Math.PI/180);
      return { x: mu.x + local.x, y: mu.y + local.y };
    },
    posSTAFF(mi, di, si, sn){
      const dep    = this.posDEP(mi, di, 1);
      const localR = this.gapStaff + Math.max(0, sn-8)*8;
      const local  = this.polar(si, sn, localR, ((mi+di)*8)*Math.PI/180);
      return { x: dep.x + local.x, y: dep.y + local.y };
    },

    fio(s){
      if(!s) return "—";
      if(s.fio) return s.fio;
      const parts = [s.last_name, s.first_name, s.second_name].filter(Boolean);
      return parts.length ? parts.join(" ") : s.username || "—";
    },

    // ===== Flyout
    openFlyout({ key, level, payload, evt }) {
      const board = this.$refs.board.getBoundingClientRect();
      let rect = null;
      if (evt && evt.target && typeof evt.target.closest === 'function') {
        const bubble = evt.target.closest('.bubble');
        if (bubble) rect = bubble.getBoundingClientRect();
      }
      if (!rect) {
        // fallback по data-key
        const el = this.$el.querySelector(`[data-key="${key}"]`);
        rect = (el ? el.getBoundingClientRect() : board);
      }

      const x = rect.left - board.left - 10;            // слева от круга
      const y = rect.top  - board.top  + rect.height/2;  // по центру круга
      this.flyout = { show:true, x, y, level, payload, pin:false };
    },
    closeFlyout(fromHover=false){
      this.hoverKey = null;
      if(fromHover && this.flyout.pin) return;
      this.flyout.show = false;
    },
    doFly(type){
      const { level, payload } = this.flyout;
      if(type === "addPerson"){
        this.$emit("open-add", {
          type:
            level === "department" ? "staff" :
            level === "management" ? "director_management" :
            level === "center"     ? "director_center" : "staff",
          context: payload
        });
      }else if(type === "addChild"){
        this.$emit("open-add", {
          type:
            level === "center"     ? "management" :
            level === "management" ? "department" : "staff",
          context: payload
        });
      }else if(type === "edit"){
        this.$emit("action", { type:"edit", level, payload });
      }else if(type === "delete"){
        this.$emit("action", { type:"delete", level, payload });
      }
      this.flyout.show = false;
    },

    // ===== Пан/зум (как в Figma)
    onWheel(e){
      const speed = 0.2;
      const factor = Math.exp(-e.deltaY * 0.001 * speed);
      const newScale = Math.min(this.maxScale, Math.max(this.minScale, this.scale * factor));

      // Зум к курсору — сохраняем мировую точку под курсором
      const rect = this.$refs.board.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;

      const wx = (mx - this.tx) / this.scale;
      const wy = (my - this.ty) / this.scale;

      this.scale = newScale;
      this.tx = mx - wx * this.scale;
      this.ty = my - wy * this.scale;
    },
    onMouseDown(e){
      if (e.button !== this.panBtn) return; // только средняя кнопка мыши
      this.isPanning = true;
      this.lastX = e.clientX; this.lastY = e.clientY;
    },
    onMouseMove(e){
      if (!this.isPanning) return;
      const dx = e.clientX - this.lastX;
      const dy = e.clientY - this.lastY;
      this.tx += dx; this.ty += dy;
      this.lastX = e.clientX; this.lastY = e.clientY;
    },
    onMouseUp(){ this.isPanning = false; },
  }
};
</script>

<style scoped>
.board{
  position:relative;
  width:100%;
  height:80vh;
  min-height:680px;
  background:#555;        /* фон как на референс-скрине */
  overflow:hidden;
}

/* Пан/зум контейнер */
.viewport{
  position:absolute;
  inset:0;
  overflow:hidden;
  cursor: grab;
}
.viewport:active{ cursor: grabbing; }

.content{
  position:absolute;
  inset:0;
  /* Весь контент масштабируется transform-ом из contentStyle */
}

/* Линии и узлы */
.links{ position:absolute; inset:0; pointer-events:none; z-index:0; }
.node { position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); z-index:1; }
.node.center{ z-index:2; }

/* --------- базовая стилизация пузырей переносится в CircleBubble.vue --------- */

/* Flyout — поверх и НЕ масштабируется */
.flyout{
  position:absolute;
  width:220px; height:220px;
  transform:translate(-50%,-50%);
  z-index:3;
  pointer-events:auto;
}
.flyout::before{
  content:"";
  position:absolute; inset:0;
  clip-path:polygon(0% 50%, 75% 10%, 75% 90%);
  background:#e9e9ec;
  border-radius:16px;
  box-shadow:0 10px 26px rgba(0,0,0,.25) inset, 0 6px 16px rgba(0,0,0,.25);
}
.fx-btn{
  position:absolute; width:46px; height:46px; border-radius:14px;
  background:#fff; border:none; display:grid; place-items:center; cursor:pointer;
  box-shadow:0 6px 16px rgba(0,0,0,.18);
}
.fx-btn svg{ width:26px; height:26px; stroke:#111; fill:none; stroke-width:1.8; }
.fx-btn.danger svg{ stroke:#b91c1c; }
.fx-btn:nth-child(1){ left:14px; top:26px; }
.fx-btn:nth-child(2){ left:14px; top:90px; }
.fx-btn:nth-child(3){ left:150px; top:90px; border-radius:999px; } /* «−» на носике */
.fx-btn:nth-child(4){ left:14px; bottom:26px; }
</style>
