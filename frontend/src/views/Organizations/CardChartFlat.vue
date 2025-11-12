<template>
  <g>
    <!-- Рёбра -->
    <g class="edges">
      <path
        v-for="e in edges"
        :key="e.id"
        class="edge"
        :class="{ 'edge--active': e.active, 'edge--dim': hasSelection && !e.active }"
        :d="e.d"
        :stroke="e.stroke"
        fill="none"
        stroke-width="2"
      />
    </g>

    <!-- Узлы-карточки -->
    <g class="nodes">
      <g
        v-for="n in laidOut"
        :key="n.id"
        :class="[
          'node',
          {
            active: String(n.id) === String(selectedId),
            'node--chain': inChain(n),
            'node--dim': hasSelection && !inChain(n) && String(n.id) !== String(selectedId),
          },
        ]"
        @pointerdown.stop
        @click.stop="$emit('node-click', n.raw)"
      >
        <!-- Карточка -->
        <rect
          :x="n.x - cardW / 2"
          :y="n.y - n.h / 2"
          :width="cardW"
          :height="n.h"
          rx="14"
          ry="14"
          :fill="fillByType(n.raw.type, isRoot(n))"
          stroke="rgba(0,0,0,.10)"
          stroke-width="1"
          opacity="0.98"
        />
        <!-- Верхняя плашка -->
        <rect
          :x="n.x - cardW / 2"
          :y="n.y - n.h / 2"
          :width="cardW"
          height="30"
          rx="14"
          ry="14"
          :fill="topFill(isRoot(n), n.raw.type)"
          opacity="0.95"
        />

        <!-- Контент карточки с переносами -->
        <foreignObject
  :x="n.x - cardW / 2 + 12"
  :y="n.y - n.h / 2 + 8"
  :width="cardW - 24"
  :height="n.h - 16"
>
  <div xmlns="http://www.w3.org/1999/xhtml" class="card-body">
    <!-- Шапка-пилюля -->
    <div class="type-chip">{{ typeLabel(n.raw.type) }}</div>

    <!-- Название подразделения -->
    <div class="unit" :title="displayName(n.raw)">
      {{ displayName(n.raw) }}
    </div>

    <!-- Тонкий разделитель, если есть руководитель -->
    <div v-if="headName(n.raw)" class="divider"></div>

    <!-- Руководитель -->
    <div v-if="headName(n.raw)" class="head" :title="headName(n.raw)">
      <span class="head-icon" aria-hidden="true"></span>
      <span class="head-label">{{ langRU ? 'Руководитель' : 'Rahbar' }}:</span>
      <span class="head-name">{{ headName(n.raw) }}</span>
    </div>
  </div>
</foreignObject>
      </g>
    </g>
  </g>
</template>

<script>
export default {
  name: "CardChartFlat",
  props: {
    roots: { type: Array, default: () => [] }, // дерево подразделений
    tile: { type: Number, default: 120 }, // базовый масштаб (оставлен для совместимости)
    langRU: { type: Boolean, default: true },
    selectedId: { type: [String, Number], default: null },
  },
  emits: ["node-click"],
  data() {
    return {
      // Геометрия раскладки внутри кластера (root и его поддерево)
      RADIAL_R0: 0,
      RADIAL_STEP: 420,
      JITTER: 28,
      GAP_FRAC: 0.22,

      // Карточка
      cardW: 260,
      baseH: 96,
      lineH: 18,
      paddingV: 12,

      // Разнос кластеров главных родителей
      CLUSTER_X_STEP: 1000,
      CLUSTER_Y_STEP: 520,
      CLUSTER_COLS: 3,

      _measureCtx: null,
    };
  },
  computed: {
    CENTER() {
      return { x: 0, y: 0 };
    },

    /** Множество id узлов от выбранного до корня */
    selectedChain() {
      const set = new Set();
      if (!this.selectedId) return set;

      const byId = new Map(this._laidBase.map((n) => [String(n.id), n]));
      let cur = String(this.selectedId);
      while (cur && byId.has(cur)) {
        set.add(cur);
        const parent = byId.get(cur)?.parent;
        cur = parent ? String(parent) : "";
      }
      return set;
    },

    hasSelection() {
      return !!this.selectedId;
    },

    /** Базовая раскладка (x,y,parent) без вычисления высот */
    _laidBase() {
      if (!this.roots.length) return [];

      const placed = new Map();

      // Локальная выкладка поддерева вокруг (0,0)
      const layoutSubtree = (node, depth, a0, a1, parent = null) => {
        const baseR = this.RADIAL_R0 + depth * this.RADIAL_STEP;
        const kids = Array.isArray(node.children) ? node.children.filter(Boolean) : [];

        if (parent) {
          const mid = (a0 + a1) / 2;
          const r = baseR + (parent._childIdx % 2 ? this.JITTER : 0);
          const x = r * Math.cos(mid);
          const y = r * Math.sin(mid);
          placed.set(node.id, {
            id: node.id,
            x,
            y,
            raw: node,
            parent: parent.id,
          });
        } else {
          placed.set(node.id, {
            id: node.id,
            x: 0,
            y: 0,
            raw: node,
            parent: null,
          });
        }

        if (!kids.length) return;
        const span = a1 - a0;
        const k = kids.length;
        const step = span / k;
        const pad = step * this.GAP_FRAC;

        for (let i = 0; i < k; i++) {
          const ch = kids[i];
          ch._childIdx = i;
          const s0 = a0 + i * step + pad / 2;
          const s1 = a0 + (i + 1) * step - pad / 2;
          layoutSubtree(ch, depth + 1, s0, s1, node);
        }
      };

      // Оффсеты для кластеров
      const clusterOffsets = [];
      const roots = this.roots;

      if (roots.length === 1) {
        clusterOffsets.push({ x: 0, y: 0 });
      } else if (roots.length === 2) {
        clusterOffsets.push({ x: -this.CLUSTER_X_STEP / 2, y: 0 });
        clusterOffsets.push({ x: this.CLUSTER_X_STEP / 2, y: 0 });
      } else {
        for (let i = 0; i < roots.length; i++) {
          const col = i % this.CLUSTER_COLS;
          const row = Math.floor(i / this.CLUSTER_COLS);
          const x = (col - (this.CLUSTER_COLS - 1) / 2) * this.CLUSTER_X_STEP;
          const y = row * this.CLUSTER_Y_STEP;
          clusterOffsets.push({ x, y });
        }
      }

      // Для каждого root — локальная раскладка и перенос кластера
      for (let r = 0; r < roots.length; r++) {
        const root = roots[r];

        // центр кластера
        placed.set(root.id, {
          id: root.id,
          x: 0,
          y: 0,
          raw: root,
          parent: null,
        });

        const kids = Array.isArray(root.children) ? root.children : [];
        const k = Math.max(1, kids.length);
        for (let i = 0; i < k; i++) {
          const a0 = (2 * Math.PI * i) / k;
          const a1 = (2 * Math.PI * (i + 1)) / k;
          kids[i] && layoutSubtree(kids[i], 1, a0, a1, root);
        }

        // перенос всего поддерева root'а
        const offset = clusterOffsets[r] || { x: 0, y: 0 };
        const moveSubtree = (node) => {
          const p = placed.get(node.id);
          if (p) {
            p.x += offset.x;
            p.y += offset.y;
          }
          (node.children || []).forEach(moveSubtree);
        };
        moveSubtree(root);
      }

      return Array.from(placed.values());
    },

    /** Итоговая раскладка + вычисление высоты карточки под контент */
    laidOut() {
      const arr = this._laidBase.map((n) => ({ ...n }));
      arr.forEach((n) => {
        const name = this.displayName(n.raw);
        const fio = this.headName(n.raw) || "";
        const innerW = this.cardW - 24; // ширина текста внутри foreignObject

        const linesName = this.wrapLines(name, innerW, 14, "600");
        const linesFio = fio ? this.wrapLines(fio, innerW, 13, "600") : [];

        const blocks =
          1 /* type row */ +
          Math.max(1, linesName.length) +
          (linesFio.length ? linesFio.length : 0);

        n.h = Math.max(this.baseH, 30 /* шапка */ + this.paddingV + blocks * this.lineH);
      });
      return arr;
    },

    /** Рёбра; отмечаем активность если оба конца в цепочке */
    edges() {
      const byId = new Map(this.laidOut.map((n) => [n.id, n]));
      const out = [];

      const walk = (node) => {
        const kids = Array.isArray(node.children) ? node.children : [];
        const p = byId.get(node.id);
        for (const ch of kids) {
          const c = byId.get(ch.id);
          if (p && c) {
            const mx = (p.x + c.x) / 2,
              my = (p.y + c.y) / 2;

            const active =
              this.selectedChain.has(String(node.id)) &&
              this.selectedChain.has(String(ch.id));

            out.push({
              id: `${node.id}->${ch.id}`,
              d: `M ${p.x} ${p.y} Q ${mx} ${my}, ${c.x} ${c.y}`,
              stroke: this.strokeByType(ch.type),
              active,
            });
          }
          walk(ch);
        }
      };
      this.roots.forEach(walk);
      return out;
    },
  },
  methods: {
    isRoot(n) {
      return this.roots.length && n.raw?.id === this.roots[0].id;
    },
    displayName(n) {
      return this.langRU ? n.name || "Без названия" : n.name || "Nomsiz";
    },
    headName(raw) {
      return raw?._head?.full_name || raw?.head_full_name || raw?.head_name || "";
    },
    typeLabel(t) {
      t = t || "other";
      return t === "center"
        ? "Центр"
        : t === "manage"
        ? "Управление"
        : t === "dept"
        ? "Отдел"
        : t === "sector"
        ? "Сектор/группа"
        : "Иное";
    },
    cut(s, n) {
      s = String(s || "");
      return s.length > n ? s.slice(0, n) + "…" : s;
    },
    fillByType(t, isRoot=false){
  const base = isRoot ? '#ff9d5c'
    : t==='center' ? '#ffb17d'
    : t==='manage' ? '#7a64ff'
    : t==='dept'   ? '#2a5da0'
    : t==='sector' ? '#37c2c0'
    : '#7c8aa3';
  // небольшой оверлей зададим отдельным прямоугольником (см. ниже)
  return base;
},
    topFill(isRoot, t) {
      if (isRoot) return "#ff8a3d";
      return this.strokeByType(t);
    },
    strokeByType(t) {
      return t === "center"
        ? "#ff8a3d"
        : t === "manage"
        ? "#7a64ff"
        : t === "dept"
        ? "#2a5da0"
        : t === "sector"
        ? "#37c2c0"
        : "#7c8aa3";
    },
    inChain(n) {
      return this.selectedChain.has(String(n.id));
    },

    /** Перенос строк по ширине при помощи измерения текста */
    wrapLines(text, maxWidth, fontSize = 14, fontWeight = "600") {
      const ctx =
        this._measureCtx ||
        (this._measureCtx = document.createElement("canvas").getContext("2d"));
      ctx.font = `${fontWeight} ${fontSize}px Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial`;
      const words = String(text || "").split(/\s+/);
      const lines = [];
      let cur = "";
      for (const w of words) {
        const test = cur ? cur + " " + w : w;
        if (ctx.measureText(test).width <= maxWidth) {
          cur = test;
        } else {
          if (cur) lines.push(cur);
          // слово длиннее строки — жёсткий перенос по символам
          if (ctx.measureText(w).width > maxWidth) {
            let run = "";
            for (const ch of w) {
              const t = run + ch;
              if (ctx.measureText(t).width <= maxWidth) run = t;
              else {
                lines.push(run);
                run = ch;
              }
            }
            cur = run;
          } else {
            cur = w;
          }
        }
      }
      if (cur) lines.push(cur);
      return lines;
    },
  },
};
</script>

<style scoped>
/* Рёбра */
.edge {
  stroke-linecap: round;
  opacity: 0.55;
  transition: opacity 0.15s, stroke-width 0.15s, filter 0.15s;
}
.edge.edge--active {
  opacity: 1;
  stroke-width: 3.5;
  filter: drop-shadow(0 0 6px rgba(0, 0, 0, 0.12));
}
.edge.edge--dim {
  opacity: 0.18;
}

/* Узлы */
.node {
  transition: transform 0.12s ease, filter 0.12s ease, opacity 0.12s ease;
}
.node.active {
  transform: scale(1.06);
  filter: drop-shadow(0 6px 16px rgba(0, 0, 0, 0.22));
}
.node--chain .card-body .unit,
.node--chain .card-body .head {
  opacity: 1;
}
.node--dim {
  opacity: 0.55;
}

/* Текст внутри карточек (foreignObject) */
.card-body {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  color: #0b1621;
  overflow: hidden;
}
.type {
  margin-top: 2px;
  height: 22px;
  font-size: 12px;
  font-weight: 800;
  text-align: center;
}
.unit {
  margin-top: 4px;
  font-size: 14px;
  font-weight: 600;
  line-height: 18px;
  word-break: break-word;
  white-space: normal;
}
.head {
  margin-top: 6px;
  font-size: 13px;
  font-weight: 600;
  line-height: 18px;
  word-break: break-word;
  white-space: normal;
}
.head .label {
  opacity: 0.7;
  font-weight: 700;
  margin-right: 6px;
}

/* Тёмная тема (если нужен селектор окружения) */
:host-context(.dark) .card-body {
  color: #fff;
}

.card-body{
  display:flex; flex-direction:column;
  width:100%; height:100%;
  color:#0b1621;
}

/* Шапка-пилюля */
.type-chip{
  align-self:center;
  padding:4px 10px;
  border-radius:9999px;
  font-size:12px; font-weight:800; letter-spacing:.2px;
  background:rgba(255,255,255,.22);
  color:#fff;
  border:1px solid rgba(255,255,255,.28);
  backdrop-filter: blur(2px);
}

/* Название подразделения — главный акцент */
.unit{
  margin-top:10px;
  font-size:15px; line-height:20px;
  font-weight:700;
  color:#07131d;
  word-break:break-word; white-space:normal;
}

/* Разделитель */
.divider{
  margin:10px 0 8px;
  height:1px;
  background:linear-gradient(90deg, rgba(255,255,255,.0), rgba(0,0,0,.20), rgba(255,255,255,.0));
  opacity:.55;
}

/* Строка руководителя с "аватаркой"-точкой */
.head{
  display:flex; align-items:center; gap:8px;
  font-size:13px; line-height:18px;
  font-weight:600;
  color:#0b1621;
  word-break:break-word; white-space:normal;
}
.head-icon{
  width:10px; height:10px; border-radius:50%;
  background:#ffffff; box-shadow:inset 0 0 0 2px rgba(0,0,0,.12);
  display:inline-block; flex:0 0 10px;
}
.head-label{ opacity:.7; font-weight:700; }
.head-name{ font-weight:700; }

/* Состояния: актив/цепочка — чуть ярче */
.node.active .type-chip{ box-shadow:0 2px 10px rgba(0,0,0,.18); }
.node--chain .unit, .node--chain .head{ opacity:1; }

/* Димминг для фоновых узлов, когда есть выбор */
.node--dim .card-body{ opacity:.65; }

/* Тёмная тема (если компонент обёрнут .dark) */
:host-context(.dark) .card-body { color:#f5f8ff; }
:host-context(.dark) .unit{ color:#fff; }
:host-context(.dark) .type-chip{
  background:rgba(0,0,0,.25);
  border-color:rgba(255,255,255,.22);
  color:#eaf1ff;
}
:host-context(.dark) .divider{
  background:linear-gradient(90deg, rgba(0,0,0,0), rgba(255,255,255,.35), rgba(0,0,0,0));
  opacity:.6;
}
:host-context(.dark) .head{ color:#eef4ff; }
</style>
