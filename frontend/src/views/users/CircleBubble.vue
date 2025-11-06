<template>
  <div
    class="tile"
    :class="side"
    :style="{ width: size + 'px', height: size + 'px' }"
    :data-key="dataKey"
    @mouseenter="hovering = true"
    @mouseleave="hovering = false"
    @click.stop="$emit('focus', $event)"
  >
    <div class="tile-extrude"></div>
    <div class="tile-face">
      <div class="avatar-figure">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <circle cx="12" cy="8" r="4" />
          <path d="M4 20a8 8 0 0 1 16 0" />
        </svg>
      </div>
    </div>

    <div class="label top" v-if="title">{{ title }}</div>
    <div class="label role">{{ role }}</div>
    <div class="label fio" v-if="subtitle">
      <span v-for="(line, i) in fioLines" :key="i">{{ line }}</span>
    </div>
  </div>
</template>

<script>
export default {
  name: "CircleBubble",
  props: {
    title: String,
    subtitle: String,
    role: String,
    side: { type: String, default: "staff" }, // center|management|department|staff
    dataKey: String,
  },
  emits: ["focus"],
  data() {
    return { hovering: false };
  },
  computed: {
    size() {
      return this.side === "center"
        ? 160
        : this.side === "management"
        ? 130
        : this.side === "department"
        ? 110
        : 90;
    },
    fioLines() {
      if (!this.subtitle) return [];
      const words = String(this.subtitle).split(/\s+/);
      const lines = [""];
      for (const w of words) {
        const cur = lines[lines.length - 1];
        if ((cur + " " + w).trim().length > 22) lines.push(w);
        else lines[lines.length - 1] = (cur + " " + w).trim();
      }
      return lines.slice(0, 3).filter(Boolean);
    },
  },
};
</script>

<style scoped>
/* Палитра под задачу */
:root {
  --tile-center:#ff8746;     --tile-center-dark:#cc6b36;   /* оранжевый */
  --tile-mgmt:#8b5cf6;       --tile-mgmt-dark:#6d28d9;     /* фиолетовый */
  --tile-dep:#1f3b63;        --tile-dep-dark:#162a45;      /* тёмно-синий */
  --tile-staff:#59d1c7;      --tile-staff-dark:#2a9e95;    /* светло сине-зелёный */
}

.tile {
  position: relative;
  transform: rotate(45deg);
  transform-style: preserve-3d;
  filter: drop-shadow(0 14px 30px rgba(0,0,0,.25));
  transition: transform .18s ease, filter .18s ease;
}
.tile:hover { transform: rotate(45deg) scale(1.04); }

.tile-face{
  position:absolute; inset:0;
  border-radius:14px;
  background: var(--c, #fff);
  display:grid; place-items:center;
}
.tile-extrude{
  content:""; position:absolute; inset:0;
  border-radius:14px;
  background: var(--c-dark, #d1d5db);
  transform: translate(10px,10px);
  z-index:-1;
}

.avatar-figure{ width:40%; aspect-ratio:1/1; transform: rotate(-45deg); }
.avatar-figure svg{ width:100%; height:100%; fill:#ffffff; }

.label{
  position:absolute; left:50%; transform: translateX(-50%) rotate(-45deg);
  color:#eaf2ff; text-align:center; font-weight:600; text-shadow:0 1px 2px rgba(0,0,0,.35);
}
.label.top{ top:-46px; width:220px; font-size:12px; line-height:1.15; }
.label.role{ bottom:-22px; font-size:12px; }
.label.fio{ bottom:-40px; width:220px; font-size:12px; display:flex; flex-direction:column; gap:2px; }

.center     { --c:var(--tile-center); --c-dark:var(--tile-center-dark); }
.management { --c:var(--tile-mgmt);   --c-dark:var(--tile-mgmt-dark); }
.department { --c:var(--tile-dep);    --c-dark:var(--tile-dep-dark); }
.staff      { --c:var(--tile-staff);  --c-dark:var(--tile-staff-dark); }
</style>
