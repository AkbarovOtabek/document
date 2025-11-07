<template>
  <div class="tile" :class="side" @click.stop="$emit('focus', $event)">
    <div class="cube">
      <!-- верхняя грань -->
      <div class="face top"></div>
      <!-- боковые грани -->
      <div class="face left"></div>
      <div class="face right"></div>

      <!-- человек, «стоит» на верхней грани -->
      <div class="avatar-figure">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <circle cx="12" cy="4.2" r="2.6" />
          <rect x="9.4" y="7"  width="5.2" height="8"  rx="1.3" />
          <rect x="14.8" y="10.2" width="2.2" height="7.2" rx="1.2" transform="rotate(-15 5.4 11.8)" />
          <rect x="7.0" y="9.6" width="2.2" height="7.2" rx="1.2" transform="rotate(13 18.6 11.8)" />
          <rect x="9"  y="15"  width="2.6" height="7.6" rx="1.1" transform="rotate(6 11.3 18.8)" />
          <rect x="12.6" y="15"  width="2.6" height="7.6" rx="1.1" transform="rotate(-6 12.9 18.8)" />
        </svg>
      </div>
    </div>

    <div class="label top" v-if="title">{{ title }}</div>
  </div>
</template>

<script>
export default {
  name: "CircleBubble",
  props: {
    title: String,
    subtitle: String,
    role: String,
    side: { type: String, default: "staff" }, 
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
/* размеры и поворот узла для твоего графа */
.tile{
  position:relative;
  width:140px; height:140px;
  transform: rotate(45deg);
  cursor:pointer;
  perspective: 900px;
}

/* контейнер с 3D-наследованием */
.cube{
  position:absolute; inset:0;
  display:grid; place-items:center;
  transform: rotate(-45deg);           /* выпрямляем внутренности */
  transform-style: preserve-3d;  
  transform: rotateX(55deg) rotateZ(0deg)  rotateY(-45deg);      /* сохраняем 3D для детей */
}

:root {}
.face{ position:absolute;}

/* верх — квадрат, приподнят */
.face.top{
  width:110px; height:110px;
  background: var(--c);
  transform: translateZ(24px) rotateX(0deg);
  box-shadow: 0 10px 18px rgba(0,0,0,.25);
  z-index:3;
}

/* левая грань */
.face.left{
  width:110px; height:24px;            /* высота «толщины» */
  background: var(--c-dark);
  transform-origin: top;
  transform: rotateX(90deg) translateY( 1px ) translateZ(-67px) rotateY(0deg);

}
/* правая грань */
.face.right{
  width:110px; height:24px;
  background: var(--c-dark2);
  transform-origin: top;
  transform: rotateX(90deg) translateY(0.5px ) translateX( 55px ) translateZ(-12px) rotateY(90deg);
 
}
/* человек «на крышке» */
.avatar-figure{
  position:absolute;
  left:50%;
  top:50%;
  width:80%;
  transform-style: preserve-3d;
  /* порядок важен (справа налево): сначала центрируем, затем
     компенсируем rotateY/rotateX куба, и поднимаем на крышку */
  transform: translateZ(20px) translateX(-35%) translateY(-72%) rotateY(0deg) rotateZ(0deg) rotateX(-75deg) ;
  transform-origin: 50% 100%; /* низ фигуры как «ступни» */
  z-index:4;
  pointer-events: none;
}
.avatar-figure svg{ width:100%; height:100%; fill:#fff; }

/* заголовок (чуть правее и дальше от плитки) */
.label.top {
  position: absolute;
  top: -70px;           /* чуть выше плитки */
  left: 70%;            /* сдвигаем правее относительно центра */
  transform: rotate(-45deg);  /* под тот же угол, что и сцена */
  width: 260px;         /* ширина текста */
  text-align: left;
  color: #eaf2ff;
  font-size: 12px;
  font-weight: 700;
  line-height: 1.4;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.35);
}

/* палитра */
.center     { --c:#ff8746; --c-dark:#cc6b36; --c-dark2:#a7521e; }
.management { --c:#8b5cf6; --c-dark:#6d28d9; --c-dark2:#5a21b3; }
.department { --c:#1f3b63; --c-dark:#162a45; --c-dark2:#0d1f36; }
.staff      { --c:#59d1c7; --c-dark:#2a9e95; --c-dark2:#207a72; }
</style>