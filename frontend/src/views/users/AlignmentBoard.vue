<script>
/**
 * AlignmentBoard — визуализация «как на гифке», но с 4 колонками:
 * Center → ManagementUnit → Department → Staff.
 *
 * props:
 *  - tree: { centers: [{ data, mus:[{data,deps:[{data,staff:[]}] }], floating:[] }] }
 *  - density: 'compact' | 'medium' | 'relaxed'
 *  - collapsed: Set<string>   // ключи: 'c:<id>' | 'mu:<id>' | 'dep:<id>'
 *
 * emits:
 *  - toggle-collapse (key) — сворачивание карточек
 *  - action ({type, level, payload}) — кнопки «+ Добавить / Изменить / Удалить / +Директор»
 *  - select-staff (staff) — клик по карточке сотрудника
 */
export default {
  name: "AlignmentBoard",
  props: {
    tree: { type: Object, required: true },
    density: { type: String, default: "compact" },
    collapsed: { type: Object, default: () => new Set() },
  },
  emits: ["toggle-collapse", "action", "select-staff"],
  data() {
    return {
      // Храним координаты карточек (для отрисовки линий)
      bbox: {
        center: new Map(),
        mu: new Map(),
        dep: new Map(),
        staff: new Map(),
      },
    };
  },
  computed: {
    gapY() {
      return this.density === "relaxed" ? 22 : this.density === "medium" ? 14 : 8;
    },
    laneGap() {
      return this.density === "relaxed" ? 140 : this.density === "medium" ? 110 : 90;
    },
    pad() {
      return this.density === "relaxed" ? 14 : this.density === "medium" ? 12 : 10;
    },
  },
  mounted() {
    this.$nextTick(this.measureAll);
  },
  updated() {
    this.$nextTick(this.measureAll);
  },
  methods: {
    // Ключи для collapsed-множества
    keyC(c) {
      return `c:${c.id}`;
    },
    keyMU(mu) {
      return `mu:${mu.id}`;
    },
    keyDep(dep) {
      return `dep:${dep.id}`;
    },

    // Перемеряем все карточки (нужно, чтобы проложить правильные линии)
    measureAll() {
      const root = this.$el.querySelector(".align-root");
      if (!root) return;
      const rootBox = root.getBoundingClientRect();

      const grab = (selector, map) => {
        map.clear();
        root.querySelectorAll(selector).forEach((el) => {
          const id = +el.getAttribute("data-id");
          if (!id) return;
          const b = el.getBoundingClientRect();
          const x1 = b.left - rootBox.left;
          const y1 = b.top - rootBox.top;
          map.set(id, { x1, y1, x2: x1 + b.width, y2: y1 + b.height, midY: y1 + b.height / 2 });
        });
      };

      grab(".card.center", this.bbox.center);
      grab(".card.mu", this.bbox.mu);
      grab(".card.dep", this.bbox.dep);
      grab(".card.staff", this.bbox.staff);
    },

    // Кривая Безье от правого края A к левому краю B
    curve(ax, ay, bx, by) {
      const dx = Math.max(50, (bx - ax) * 0.5);
      return `M ${ax},${ay} C ${ax + dx},${ay} ${bx - dx},${by} ${bx},${by}`;
    },

    // Счётчики для бейджей
    countForCenter(cNode) {
      const muCount = cNode.mus.length;
      const depCount = cNode.mus.reduce((s, m) => s + m.deps.length, 0);
      const staffCount =
        cNode.mus.reduce((s, m) => s + m.deps.reduce((t, d) => t + d.staff.length, 0), 0) +
        (cNode.floating?.length || 0);
      return { muCount, depCount, staffCount };
    },
    countForMU(muNode) {
      const depCount = muNode.deps.length;
      const staffCount = muNode.deps.reduce((s, d) => s + d.staff.length, 0);
      return { depCount, staffCount };
    },

    // Уведомляем родителя о действии (создать/редактировать/удалить/назначить директора)
    doAction(type, level, payload) {
      this.$emit("action", { type, level, payload });
    },
  },
};
</script>

<template>
  <div
    class="align-root"
    :style="{ '--gap-y': gapY + 'px', '--lane-gap': laneGap + 'px', '--pad': pad + 'px' }"
  >
    <!-- SVG провода -->
    <svg class="wires" xmlns="http://www.w3.org/2000/svg">
      <g stroke="#cbd5e1" stroke-width="2" fill="none" stroke-linecap="round">
        <!-- Center → MU -->
        <template v-for="c in tree.centers" :key="'w-c-' + c.data.id">
          <template v-if="!collapsed.has(keyC(c.data))">
            <template v-for="mu in c.mus" :key="'w-mu-' + mu.data.id">
              <path
                :d="
                  curve(
                    bbox.center.get(c.data.id)?.x2 || 0,
                    bbox.mu.get(mu.data.id)?.midY || 0,
                    bbox.mu.get(mu.data.id)?.x1 || 0,
                    bbox.mu.get(mu.data.id)?.midY || 0
                  )
                "
              />
            </template>
          </template>
        </template>

        <!-- MU → DEP -->
        <template v-for="c in tree.centers" :key="'w2-c-' + c.data.id">
          <template v-if="!collapsed.has(keyC(c.data))">
            <template v-for="mu in c.mus" :key="'w2-mu-' + mu.data.id">
              <template v-if="!collapsed.has(keyMU(mu.data))">
                <template v-for="d in mu.deps" :key="'w2-d-' + d.data.id">
                  <path
                    :d="
                      curve(
                        bbox.mu.get(mu.data.id)?.x2 || 0,
                        bbox.dep.get(d.data.id)?.midY || 0,
                        bbox.dep.get(d.data.id)?.x1 || 0,
                        bbox.dep.get(d.data.id)?.midY || 0
                      )
                    "
                  />
                </template>
              </template>
            </template>
          </template>
        </template>

        <!-- DEP → STAFF -->
        <template v-for="c in tree.centers" :key="'w3-c-' + c.data.id">
          <template v-if="!collapsed.has(keyC(c.data))">
            <template v-for="mu in c.mus" :key="'w3-mu-' + mu.data.id">
              <template v-if="!collapsed.has(keyMU(mu.data))">
                <template v-for="d in mu.deps" :key="'w3-d-' + d.data.id">
                  <template v-if="!collapsed.has(keyDep(d.data))">
                    <template v-for="s in d.staff" :key="'w3-s-' + s.id">
                      <path
                        :d="
                          curve(
                            bbox.dep.get(d.data.id)?.x2 || 0,
                            bbox.staff.get(s.id)?.midY || 0,
                            bbox.staff.get(s.id)?.x1 || 0,
                            bbox.staff.get(s.id)?.midY || 0
                          )
                        "
                      />
                    </template>
                  </template>
                </template>
              </template>
            </template>
          </template>
        </template>
      </g>
    </svg>

    <!-- Контентные колонки -->
    <div class="lanes">
      <!-- L0: Centers -->
      <div class="lane">
        <div
          v-for="c in tree.centers"
          :key="'c-' + c.data.id"
          class="card center"
          :data-id="c.data.id"
        >
          <div class="row">
            <div class="title">{{ c.data.name }}</div>
            <div class="progress" :style="{ '--p': (c.data.progress || 0) + '%' }">
              <span>{{ c.data.progress || 0 }}%</span>
            </div>
            <div class="actions">
              <button class="ghost" @click="$emit('toggle-collapse', keyC(c.data))">
                {{ collapsed.has(keyC(c.data)) ? "Expand" : "Collapse" }}
              </button>
              <button class="ghost" @click="doAction('addMU', 'center', c.data)">
                + Управление
              </button>
              <button class="ghost" @click="doAction('addDirector', 'center', c.data)">
                + Директор
              </button>
              <button class="ghost" @click="doAction('edit', 'center', c.data)">Изм.</button>
              <button class="danger" @click="doAction('delete', 'center', c.data)">Удалить</button>
            </div>
          </div>
          <div class="counts">
            <span class="badge">{{ countForCenter(c).muCount }} MU</span>
            <span class="dot">•</span>
            <span class="badge">{{ countForCenter(c).depCount }} отделов</span>
            <span class="dot">•</span>
            <span class="badge">{{ countForCenter(c).staffCount }} сотрудников</span>
          </div>
        </div>
      </div>

      <!-- L1: Management Units -->
      <div class="lane">
        <template v-for="c in tree.centers" :key="'lane-mu-' + c.data.id">
          <template v-if="!collapsed.has(keyC(c.data))">
            <div
              v-for="mu in c.mus"
              :key="'mu-' + mu.data.id"
              class="card mu"
              :data-id="mu.data.id"
            >
              <div class="row">
                <div class="title">{{ mu.data.name }}</div>
                <div class="progress" :style="{ '--p': (mu.data.progress || 0) + '%' }">
                  <span>{{ mu.data.progress || 0 }}%</span>
                </div>
                <div class="actions">
                  <button class="ghost" @click="$emit('toggle-collapse', keyMU(mu.data))">
                    {{ collapsed.has(keyMU(mu.data)) ? "Expand" : "Collapse" }}
                  </button>
                  <button class="ghost" @click="doAction('addDept', 'mu', mu.data)">+ Отдел</button>
                  <button class="ghost" @click="doAction('addDirector', 'mu', mu.data)">
                    + Директор упр.
                  </button>
                  <button class="ghost" @click="doAction('edit', 'mu', mu.data)">Изм.</button>
                  <button class="danger" @click="doAction('delete', 'mu', mu.data)">Удалить</button>
                </div>
              </div>
              <div class="counts">
                <span class="badge">{{ countForMU(mu).depCount }} отделов</span>
                <span class="dot">•</span>
                <span class="badge">{{ countForMU(mu).staffCount }} сотрудников</span>
              </div>
            </div>
          </template>
        </template>
      </div>

      <!-- L2: Departments -->
      <div class="lane">
        <template v-for="c in tree.centers" :key="'lane-dep-' + c.data.id">
          <template v-if="!collapsed.has(keyC(c.data))">
            <template v-for="mu in c.mus" :key="'lane-dep-mu-' + mu.data.id">
              <template v-if="!collapsed.has(keyMU(mu.data))">
                <div
                  v-for="d in mu.deps"
                  :key="'dep-' + d.data.id"
                  class="card dep"
                  :data-id="d.data.id"
                >
                  <div class="row">
                    <div class="title">{{ d.data.name }}</div>
                    <div class="progress" :style="{ '--p': (d.data.progress || 0) + '%' }">
                      <span>{{ d.data.progress || 0 }}%</span>
                    </div>
                    <div class="actions">
                      <button class="ghost" @click="$emit('toggle-collapse', keyDep(d.data))">
                        {{ collapsed.has(keyDep(d.data)) ? "Expand" : "Collapse" }}
                      </button>
                      <button class="ghost" @click="doAction('addStaff', 'dep', d.data)">
                        + Сотрудник
                      </button>
                      <button class="ghost" @click="doAction('edit', 'dep', d.data)">Изм.</button>
                      <button class="danger" @click="doAction('delete', 'dep', d.data)">
                        Удалить
                      </button>
                    </div>
                  </div>
                  <div class="counts">
                    <span class="badge">{{ d.staff.length }} сотрудников</span>
                  </div>
                </div>
              </template>
            </template>
          </template>
        </template>
      </div>

      <!-- L3: Staff -->
      <div class="lane">
        <template v-for="c in tree.centers" :key="'lane-staff-' + c.data.id">
          <template v-if="!collapsed.has(keyC(c.data))">
            <template v-for="mu in c.mus" :key="'lane-staff-mu-' + mu.data.id">
              <template v-if="!collapsed.has(keyMU(mu.data))">
                <template v-for="d in mu.deps" :key="'lane-staff-dep-' + d.data.id">
                  <template v-if="!collapsed.has(keyDep(d.data))">
                    <div
                      v-for="s in d.staff"
                      :key="'s-' + s.id"
                      class="card staff"
                      :data-id="s.id"
                      @click="$emit('select-staff', s)"
                    >
                      <div class="row">
                        <div class="title">
                          {{
                            s.fio ||
                            [s.last_name, s.first_name, s.second_name].filter(Boolean).join(" ") ||
                            s.username
                          }}
                        </div>
                        <div class="progress" :style="{ '--p': (s.progress || 0) + '%' }">
                          <span>{{ s.progress || 0 }}%</span>
                        </div>
                        <div class="actions">
                          <button class="ghost" @click.stop="doAction('edit', 'staff', s)">
                            Изм.
                          </button>
                          <button class="danger" @click.stop="doAction('delete', 'staff', s)">
                            Удалить
                          </button>
                        </div>
                      </div>
                      <div class="sub">
                        {{ s.position }}<span v-if="s.role"> · {{ s.role }}</span>
                      </div>
                    </div>
                  </template>
                </template>
              </template>
            </template>
          </template>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.align-root {
  --line: #e2e8f0;
  --ink: #0f172a;
  --muted: #64748b;
  --card: #fff;
  position: relative;
  background: #f5f7fa;
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 12px;
  overflow: auto;
}
.wires {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.lanes {
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: 360px;
  gap: var(--lane-gap);
}
.lane {
  display: flex;
  flex-direction: column;
  gap: var(--gap-y);
  padding: 8px 0;
}

.card {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: var(--pad);
  box-shadow: 0 6px 18px rgba(2, 6, 23, 0.06);
}
.card .row {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 10px;
  align-items: center;
}
.title {
  font-weight: 800;
  color: var(--ink);
  white-space: normal;
  overflow-wrap: anywhere;
}
.actions {
  display: flex;
  gap: 6px;
}
.ghost {
  border: 1px solid var(--line);
  background: #fff;
  border-radius: 8px;
  padding: 4px 8px;
  cursor: pointer;
}
.danger {
  border: 1px solid #fecaca;
  background: #fff;
  color: #b91c1c;
  border-radius: 8px;
  padding: 4px 8px;
  cursor: pointer;
}

.progress {
  --p: 0%;
  width: 76px;
  height: 30px;
  border-radius: 10px;
  border: 1px solid var(--line);
  background: conic-gradient(#22c55e var(--p), #e2e8f0 0) padding-box;
  -webkit-mask: radial-gradient(16px at right 50%, #0000 98%, #000), linear-gradient(#000 0 0);
  mask: radial-gradient(16px at right 50%, #0000 98%, #000), linear-gradient(#000 0 0);
  display: grid;
  place-items: center;
  font-weight: 800;
  font-size: 12px;
  padding-left: 18px;
}
.progress > span {
  user-select: none;
}
.counts {
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--muted);
}
.badge {
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 2px 8px;
  font-size: 12px;
}
.dot {
  opacity: 0.6;
}
.sub {
  margin-top: 6px;
  color: var(--muted);
  font-size: 12px;
}
</style>
