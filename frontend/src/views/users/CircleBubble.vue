<template>
  <div
    class="bubble"
    :style="{
      width: size + 'px',
      height: size + 'px',
      '--fs-top': fsTop + 'px',
      '--fs-role': fsRole + 'px',
      '--fs-fio': fsFio + 'px',
    }"
    :data-key="dataKey"
    @mouseenter="hovering = true"
    @mouseleave="hovering = false"
    @click.stop="$emit('focus', $event)"
  >
    <!-- (+) можно оставить/убрать; по задаче — убираем, но оставляю на будущее. Комментируйте блок если не нужен -->
    <!--
    <button
      class="sidebtn left"
      v-show="hovering"
      :data-key="dataKey"
      title="Добавить"
      @click.stop="$emit('openAdd', $event)"
    >
      +
    </button>
    -->

    <!-- иконка -->
    <div class="avatar-figure">
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <circle cx="12" cy="8" r="4" />
        <path d="M4 20a8 8 0 0 1 16 0" />
      </svg>
    </div>

    <!-- подписи -->
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
  emits: [
    "focus",
    // "openAdd"
  ],
  data() {
    return { hovering: false };
  },
  computed: {
    size() {
      return this.side === "center"
        ? 240
        : this.side === "management"
        ? 180
        : this.side === "department"
        ? 150
        : 115;
    },
    fsTop() {
      const l = (this.title || "").length;
      const base = this.side === "center" ? 14 : this.side === "management" ? 12 : 11;
      if (l > 60) return base - 4;
      if (l > 40) return base - 2;
      return base;
    },
    fsRole() {
      return this.side === "center" ? 14 : this.side === "management" ? 12 : 11;
    },
    fsFio() {
      const l = (this.subtitle || "").length;
      const base = this.side === "center" ? 14 : 8;
      if (l > 40) return base - 3;
      if (l > 26) return base - 1;
      return base;
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
.bubble {
  position: relative;
  border-radius: 50%;
  background: #fff;
  border: 2px solid #e5e7eb;
  display: grid;
  place-items: center;
  box-shadow: 0 10px 26px rgba(0, 0, 0, 0.18);
  transition: transform 0.18s ease;
}
.bubble:hover {
  transform: scale(1.02);
}

.avatar-figure {
  width: 44%;
  aspect-ratio: 1/1;
}
.avatar-figure svg {
  width: 100%;
  height: 100%;
  fill: #000;
}

.label {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  color: #111;
  text-align: center;
  font-weight: 500;
  overflow: hidden;
}
.label.top {
  top: 10%;
  width: 78%;
  font-size: 9px;
  line-height: 1.15;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}
.label.role {
  bottom: 22%;
  width: 82%;
  font-size: var(--fs-role, 14px);
  white-space: nowrap;
  text-overflow: ellipsis;
}
.label.fio {
  bottom: 8%;
  width: 82%;
  font-size: var(--fs-fio, 16px);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

/* .sidebtn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: #111;
  color: #fff;
  font-weight: 800;
  display: grid;
  place-items: center;
  cursor: pointer;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.25);
}
.sidebtn.left {
  left: -22px;
} */
</style>
