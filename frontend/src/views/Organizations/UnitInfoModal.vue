<template>
  <aside
    v-if="open"
    ref="panel"
    class="user-panel"
    :class="{ dark: isDark }"
    :style="{ right: '12px', top: panelTop + 'px', bottom: '12px', width: '420px' }"
    @click.stop
  >
    <header class="head">
      <div class="titlebox">
        <div class="avatar"><span>{{ initials }}</span></div>
        <div class="titler">
          <div class="name" :title="unit?.name">{{ unitName }}</div>
          <div class="rolechip"><i class="dot"></i>{{ typeLabel(unit?.type) }}</div>
        </div>
      </div>
      <button class="close" @click="emitClose" aria-label="Закрыть">✕</button>
    </header>

    <section class="grid">
      <!-- k/v — как у тебя -->
      <div class="kv"><div class="k">ФИО</div><div class="v">{{ head?.fio || head?.full_name || '—' }}</div></div>
      <div class="kv"><div class="k">ДОЛЖНОСТЬ</div><div class="v">{{ head?.position_display || head?.position_title || '—' }}</div></div>
      <div class="kv"><div class="k">ОТДЕЛ</div><div class="v">{{ unitName }}</div></div>
      <div class="kv"><div class="k">УПРАВЛЕНИЕ</div><div class="v">{{ parentText }}</div></div>
      <div class="kv"><div class="k">EMAIL</div><div class="v">{{ head?.email || '—' }}</div></div>
      <div class="kv"><div class="k">ТЕЛЕФОН</div><div class="v">{{ head?.phone || head?.work_phone || '—' }}</div></div>

      <div class="kv" v-if="headLoading"><div class="k">СТАТУС</div><div class="v muted">Загрузка…</div></div>
      <div class="kv" v-else-if="headError"><div class="k">СТАТУС</div><div class="v error">{{ headError }}</div></div>
      <div class="kv" v-else-if="head?.is_head"><div class="k">СТАТУС</div><div class="v">Руководитель</div></div>
    </section>

    <footer class="foot">
      <button class="btn ghost" @click="emitClose">Закрыть</button>
    </footer>
  </aside>
</template>

<script>
export default {
  name: "UnitInfoModal",
  props: {
    open: { type: Boolean, default: false },
    unit: { type: Object, default: null },
    head: { type: Object, default: null },
    headLoading: { type: Boolean, default: false },
    headError: { type: String, default: "" },
    langRU: { type: Boolean, default: true },
    isDark: { type: Boolean, default: false },
    panelTop: { type: Number, default: 12 },
  },
  emits: ["close"],
  computed: {
    unitName(){ return (this.unit && this.unit.name) || (this.langRU ? "Без названия" : "Nomsiz"); },
    initials(){
      const s = (this.unit && this.unit.name) ? this.unit.name.trim() : "";
      if (!s) return "🏢";
      return s.split(/\s+/).map(w=>w[0]).join("").slice(0,2).toUpperCase();
    },
    parentText(){
      const pid = this.unit && this.unit.parent_id;
      return (pid != null && pid !== "") ? `#${pid}` : "—";
    }
  },
  mounted(){
    // Закрываем по клику вне панели только ЛКМ
    document.addEventListener("pointerdown", this.onDocPointer, true);
    document.addEventListener("keydown", this.onKey);
  },
  beforeUnmount(){
    document.removeEventListener("pointerdown", this.onDocPointer, true);
    document.removeEventListener("keydown", this.onKey);
  },
  methods: {
    onKey(e){ if (e.key === "Escape" && this.open) this.emitClose(); },
    emitClose(){ this.$emit("close"); },
    onDocPointer(e){
      if (!this.open) return;
      // закрываем только ЛКМ (button === 0)
      if (e.button !== 0) return;
      const p = this.$refs.panel;
      if (p && p.contains(e.target)) return; // клик по панели — не закрываем
      this.emitClose();
    },
    typeLabel(t) {
      t = (t || "other");
      return t === "center" ? "Центр"
           : t === "manage" ? "Управление"
           : t === "dept"   ? "Отдел"
           : t === "sector" ? "Сектор/группа"
           : "Иное";
    },
  }
};
</script>

<style scoped>
.user-panel{
  position:absolute;
  right:12px; top:12px; bottom:12px; width:420px;
  border-radius:16px;
  background:#0f1720; color:#e9eef7;
  box-shadow:0 20px 56px rgba(0,0,0,.38), inset 0 0 0 1px rgba(255,255,255,.06);
  display:grid; grid-template-rows:auto 1fr auto;
  overflow:hidden; z-index:8;
}
.user-panel.dark{ background:#0f1720; color:#e9eef7 }
.user-panel:not(.dark){ background:#fff; color:#0f141a; box-shadow:0 20px 56px rgba(16,24,40,.18), inset 0 0 0 1px rgba(16,24,40,.06) }

.head{ display:flex; align-items:center; justify-content:space-between; gap:12px; padding:14px 16px; border-bottom:1px solid rgba(255,255,255,.06) }
.user-panel:not(.dark) .head{ border-bottom:1px solid #eef2f7 }

.titlebox{ display:flex; gap:12px; align-items:center }
.avatar{ width:36px; height:36px; border-radius:50%; display:grid; place-items:center; background:linear-gradient(180deg,#8b5cf6,#22d3ee); color:#fff; font-weight:900; font-size:14px }
.titler{ display:grid; gap:4px }
.name{ font-weight:800; font-size:16px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis }
.rolechip{ display:inline-flex; align-items:center; gap:6px; font-size:12px; padding:2px 8px; border-radius:999px; background:rgba(255,255,255,.08) }
.user-panel:not(.dark) .rolechip{ background:#f3f4f6; color:#111827 }
.dot{ width:6px; height:6px; border-radius:50%; background:#87e8de; display:inline-block }

.grid{ padding:12px 14px; display:grid; gap:10px; overflow:auto }
.kv{ display:grid; grid-template-columns:140px 1fr; gap:10px; align-items:start; background:rgba(255,255,255,.04); border:1px solid rgba(255,255,255,.06); border-radius:12px; padding:10px 12px }
.user-panel:not(.dark) .kv{ background:#fafbfc; border:1px solid #eef2f7 }
.k{ font-weight:700; opacity:.75; font-size:12px; text-transform:uppercase; letter-spacing:.02em }
.v{ font-weight:600; font-size:14px; word-break:break-word }
.muted{ color:#94a3b8 } .error{ color:#ef4444 }

.foot{ padding:12px 14px; border-top:1px solid rgba(255,255,255,.06); display:flex; justify-content:flex-end }
.user-panel:not(.dark) .foot{ border-top:1px solid #eef2f7 }
.btn.ghost{ padding:8px 12px; border-radius:10px; font-weight:700; cursor:pointer; border:1px solid rgba(255,255,255,.14); background:transparent; color:inherit }
.user-panel:not(.dark) .btn.ghost{ border:1px solid #e5e7eb }
.close{ border:0; background:transparent; color:inherit; font-size:18px; cursor:pointer; padding:6px 8px }
</style>
