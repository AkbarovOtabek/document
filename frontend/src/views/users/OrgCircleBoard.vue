<!-- src/components/users/OrgCircleBoard.vue -->
<template>
  <div class="board">
    <!-- Центральный круг: Центр -->
    <div class="node center">
      <div class="avatar"></div>
      <div class="title">{{ center.name }}</div>
      <div class="sub">
        {{ center.director?.fio || "—" }}
        <span class="muted"> · {{ center.director?.position || "Директор центра" }}</span>
      </div>

      <!-- кнопка добавить/изменить -->
      <div class="actions">
        <button class="pill" @click="$emit('open-add', { type: 'management' })">
          + Управление
        </button>
        <button class="pill" @click="$emit('open-modal', center.director)">О директоре</button>
      </div>
    </div>

    <!-- РАДИУС 1: Управления -->
    <div class="ring ring-mgmt">
      <div
        v-for="(m, mi) in center.managements"
        :key="m.id"
        class="node mgmt"
        :style="polar(mi, center.managements.length, 260)"
      >
        <div class="avatar small"></div>
        <div class="title">{{ m.name }}</div>
        <div class="sub">
          {{ m.director?.fio || "—" }}
          <span class="muted"> · {{ m.director?.position || "Директор управления" }}</span>
        </div>

        <div class="actions tiny">
          <button
            class="circle"
            title="Добавить отдел"
            @click="$emit('open-add', { type: 'department', management: m })"
          >
            +
          </button>
          <button class="circle" title="Открыть" @click="$emit('open-modal', m.director)">i</button>
        </div>

        <!-- РАДИУС 2: Отделы вокруг управления -->
        <div class="ring ring-dep">
          <div
            v-for="(d, di) in m.departments"
            :key="d.id"
            class="node dep"
            :style="polar(di, m.departments.length, 120)"
          >
            <div class="avatar tiny"></div>
            <div class="title">{{ d.name }}</div>
            <div class="sub">
              {{ d.head?.fio || "—" }}
              <span class="muted"> · {{ d.head?.position || "Начальник отдела" }}</span>
            </div>

            <div class="actions micro">
              <button
                class="circle"
                title="Добавить сотрудника"
                @click="$emit('open-add', { type: 'staff', department: d })"
              >
                +
              </button>
              <button class="circle" title="Открыть" @click="$emit('open-modal', d.head)">i</button>
            </div>

            <!-- РАДИУС 3: Сотрудники вокруг отдела -->
            <div class="ring ring-staff" v-if="d.staff?.length">
              <div
                v-for="(s, si) in d.staff"
                :key="s.id"
                class="node staff"
                :style="polar(si, d.staff.length, 70)"
                @click="$emit('open-modal', s)"
                title="Открыть карточку"
              >
                <div class="avatar micro"></div>
                <div class="title ellipsis">{{ fio(s) }}</div>
                <div class="sub muted small ellipsis">{{ s.position || "Сотрудник" }}</div>
              </div>
            </div>
            <!-- /Сотрудники -->
          </div>
        </div>
        <!-- /Отделы -->
      </div>
    </div>
    <!-- /Управления -->
  </div>
</template>

<script>
export default {
  name: "OrgCircleBoard",
  props: {
    center: { type: Object, required: true },
  },
  emits: ["open-modal", "open-add"],
  methods: {
    /** Раскладывает элементы по окружности.
     *  @param {number} idx - индекс элемента в группе
     *  @param {number} total - всего элементов в группе
     *  @param {number} radius - радиус (px)
     *  Возвращает инлайн-стили translate(x,y).
     */
    polar(idx, total, radius) {
      if (!total) return {};
      const angle = (idx / total) * 2 * Math.PI - Math.PI / 2; // старт сверху
      const x = Math.cos(angle) * radius;
      const y = Math.sin(angle) * radius;
      return { transform: `translate(${x}px, ${y}px)` };
    },
    fio(s) {
      if (!s) return "—";
      if (s.fio) return s.fio;
      const parts = [s.last_name, s.first_name, s.second_name].filter(Boolean);
      return parts.length ? parts.join(" ") : s.username || "—";
    },
  },
};
</script>

<style scoped>
.board {
  position: relative;
  width: 100%;
  height: 80vh;
  min-height: 640px;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  background: #f8fafc;
  overflow: hidden;
}

/* Центр сцены */
.board {
  display: grid;
  place-items: center;
}

/* Общие стили узлов */
.node {
  position: absolute;
  top: 50%;
  left: 50%;
  translate: -50% -50%;
  width: 220px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 999px;
  padding: 16px 18px 12px;
  text-align: center;
  box-shadow: 0 6px 18px rgba(2, 6, 23, 0.06);
}

.node .title {
  font-weight: 700;
  color: #0f172a;
  margin-top: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sub {
  margin-top: 4px;
  font-size: 12px;
  color: #334155;
}
.muted {
  color: #64748b;
}
.small {
  font-size: 11px;
}
.ellipsis {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Аватары как круглые заглушки */
.avatar {
  width: 64px;
  height: 64px;
  border-radius: 999px;
  margin: 0 auto;
  background: #e5e7eb;
}
.avatar.small {
  width: 48px;
  height: 48px;
}
.avatar.tiny {
  width: 36px;
  height: 36px;
}
.avatar.micro {
  width: 28px;
  height: 28px;
}

/* Центр крупнее */
.node.center {
  width: 280px;
  padding: 22px 20px 16px;
  border-width: 2px;
  border-color: #c7d2fe;
}

/* Управления */
.ring-mgmt .node.mgmt {
  width: 210px;
}

/* Отделы */
.ring-dep .node.dep {
  width: 190px;
  padding: 14px 14px 10px;
}

/* Сотрудники */
.ring-staff .node.staff {
  width: 140px;
  padding: 10px 10px 8px;
  cursor: pointer;
}
.ring-staff .node.staff:hover {
  box-shadow: 0 8px 22px rgba(2, 6, 23, 0.12);
  border-color: #cbd5e1;
}

/* Контейнеры-«кольца» */
.ring {
  position: absolute;
  top: 50%;
  left: 50%;
  translate: -50% -50%;
  pointer-events: none; /* чтобы клики шли в узлы */
}
.ring .node {
  pointer-events: auto;
}

/* Мини-кнопки действий */
.actions {
  margin-top: 10px;
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-wrap: wrap;
}
.pill {
  height: 28px;
  padding: 0 10px;
  border: 1px solid #e2e8f0;
  background: #fff;
  border-radius: 16px;
  cursor: pointer;
  font-weight: 700;
}
.actions.tiny {
  gap: 6px;
  margin-top: 8px;
}
.actions.micro {
  gap: 4px;
  margin-top: 6px;
}

.circle {
  width: 26px;
  height: 26px;
  border: 1px solid #e2e8f0;
  border-radius: 999px;
  background: #fff;
  font-weight: 800;
  line-height: 1;
  cursor: pointer;
}
</style>
