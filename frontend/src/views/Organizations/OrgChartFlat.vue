<script>
import OrgChartBoard from "./OrgChartBoard.vue";

export default {
  name: "OrgChartFlat",
  components: { OrgChartBoard },
  props: {
    // массив корней (управления/дирекции и т.д.)
    tree: { type: Array, default: () => [] },
    showCounters: { type: Boolean, default: true },
  },
  data() {
    return { sideStack: [] };
  },
  methods: {
    typeInfo(t) {
      const map = {
        directorate: { label: "Дирекция", color: "var(--c-dir)" },
        management: { label: "Управление", color: "var(--c-mng)" },
        department: { label: "Отдел", color: "var(--c-dep)" },
        section: { label: "Сектор", color: "var(--c-sec)" },
        other: { label: "Подразделение", color: "var(--c-oth)" },
      };
      return map[t] || map.other;
    },
    empCount(n) {
      return n?.employees?.length || 0;
    },
    kidsCount(n) {
      return n?.children?.length || 0;
    },

    onPick({ node, level }) {
      // Yangi tanlangan uzelni o‘ngdagi “stack”ga qo‘shamiz (avvalgilari saqlanadi)
      this.sideStack.push({ node, level, ts: Date.now() });
    },
    clearAll() {
      this.sideStack = [];
    },

    initials(s) {
      return (
        String(s || "")
          .trim()
          .split(/\s+/)
          .map((w) => w[0])
          .join("")
          .slice(0, 2)
          .toUpperCase() || "👤"
      );
    },
    fio(e) {
      return e?.fio || e?.full_name || e?.username || "";
    },
    position(e) {
      return e?.position_display || e?.position_title || e?.position || "";
    },
    phone(e) {
      return e?.phone || e?.work_phone || e?.mobile || "";
    },
    email(e) {
      return e?.email || e?.work_email || "";
    },
    tel(v) {
      return v ? `tel:${String(v).replace(/\s+/g, "")}` : "#";
    },
    mail(v) {
      return v ? `mailto:${v}` : "#";
    },
  },
};
</script>

<template>
  <!-- To‘liq kenglikdagi obёрtka: chapda sxema, o‘ngda kontaktlar -->
  <div class="flat-layout">
    <!-- CHAP: bir nechta root’lar alohida bloklarda, “yopishmasin” -->
    <div class="flat-left">
      <div class="forest">
        <div class="root-box" v-for="r in tree" :key="r.id">
          <div class="root-title">
            {{ r.name }}
            <span class="root-meta" v-if="showCounters">
              <span v-if="kidsCount(r)">{{ kidsCount(r) }} подр.</span>
              <span v-if="empCount(r)"> · {{ empCount(r) }} сотрудн.</span>
            </span>
          </div>

          <!-- Har bir root uchun alohida Board, o‘z strelkalari bilan -->
          <OrgChartBoard :root="r" :show-counters="showCounters" @select="onPick" />
        </div>
      </div>
    </div>

    <!-- O‘NG: tanlangan uzellar bo‘yicha kontaktlar steki -->
    <aside class="flat-right">
      <div class="right-head">
        <div class="muted" v-if="!sideStack.length">Нажмите на блок в схеме</div>
        <button v-else class="btn clear" @click="clearAll">Очистить</button>
      </div>

      <div
        v-for="(it, idx) in sideStack"
        :key="(it.node?.id ?? idx) + '-' + it.level + '-' + it.ts"
        class="side-card"
      >
        <div class="side-line">
          <div class="side-type" :style="{ background: typeInfo(it.node.type).color }">
            {{ typeInfo(it.node.type).label }}
          </div>
        </div>

        <div class="side-title">{{ it.node.name }}</div>
        <div class="side-meta">
          <span v-if="empCount(it.node)">{{ empCount(it.node) }} сотрудн.</span>
          <span v-if="kidsCount(it.node)"> · {{ kidsCount(it.node) }} подраздел.</span>
        </div>

        <!-- Bo‘limning o‘z kontakt maydonlari (agar bo‘lsa) -->
        <div class="unit-contacts" v-if="it.node.phone || it.node.email || it.node.address">
          <div class="uc-row" v-if="it.node.phone">
            ☎ <a :href="tel(it.node.phone)">{{ it.node.phone }}</a>
          </div>
          <div class="uc-row" v-if="it.node.email">
            ✉ <a :href="mail(it.node.email)">{{ it.node.email }}</a>
          </div>
          <div class="uc-row muted" v-if="it.node.address">📍 {{ it.node.address }}</div>
        </div>

        <!-- Hodimlar ro‘yxati -->
        <div class="emp-list" v-if="empCount(it.node)">
          <div v-for="(e, i) in it.node.employees" :key="e.id || i" class="emp-item">
            <div class="emp-avatar">{{ initials(fio(e)) }}</div>
            <div class="emp-main">
              <div class="emp-name">{{ fio(e) }}</div>
              <div class="emp-sub">{{ position(e) || "—" }}</div>
              <div class="emp-links">
                <a v-if="phone(e)" :href="tel(phone(e))">☎ {{ phone(e) }}</a>
                <a v-if="email(e)" :href="mail(email(e))">✉ {{ email(e) }}</a>
              </div>
            </div>
          </div>
        </div>

        <div class="muted" v-else>Сотрудники не указаны.</div>
      </div>
    </aside>
  </div>
</template>

<style scoped>
:root {
  /* Ranglar OrganizationDetail’dan meros oladi; defaultlar: */
  --panel: #fff;
  --ink: #0f141a;
  --muted: #6b7280;
  --line: #e6e8ee;

  --c-dir: #8b5cf6;
  --c-mng: #22c55e;
  --c-dep: #06b6d4;
  --c-sec: #f59e0b;
  --c-oth: #9ca3af;
}

/* To‘liq kenglik: chap 1fr, o‘ng 360px (sticky) */
.flat-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 16px;
  align-items: start;
  width: 100%;
}
@media (max-width: 1100px) {
  .flat-layout {
    grid-template-columns: 1fr;
  }
}

/* CHAP panel */
.flat-left {
  position: relative;
  padding: 16px;
  border: 1px solid var(--line);
  border-radius: 16px;
  background: var(--panel);
}

/* Bir nechta root “yopishmasin” */
.forest {
  display: flex;
  flex-direction: column;
  gap: 28px;
}
.root-box {
  border: 1px dashed var(--line);
  border-radius: 14px;
  padding: 10px 12px;
  background: rgba(0, 0, 0, 0.02);
}
.root-title {
  font-weight: 900;
  margin: 4px 0 8px;
  color: #475569;
  display: flex;
  align-items: center;
  gap: 8px;
}
.root-meta {
  font-weight: 600;
  font-size: 12px;
  color: var(--muted);
}

/* O‘NG panel */
.flat-right {
  position: sticky;
  top: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.right-head {
  display: flex;
  justify-content: flex-end;
  min-height: 28px;
  align-items: center;
}
.btn.clear {
  height: 30px;
  padding: 0 10px;
  border-radius: 10px;
  border: 1px solid var(--line);
  background: var(--panel);
  color: var(--ink);
  cursor: pointer;
}

/* O‘ngdagi kartalar */
.side-card {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 14px;
  box-shadow: 0 10px 22px rgba(0, 0, 0, 0.06);
}
.side-line {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}
.side-type {
  color: #fff;
  font-size: 11px;
  font-weight: 900;
  height: 22px;
  padding: 0 10px;
  border-radius: 999px;
}
.side-title {
  margin: 8px 0 2px;
  font-size: 18px;
  font-weight: 900;
}
.side-meta {
  color: var(--muted);
  font-size: 12px;
  margin-bottom: 8px;
}

/* Bo‘lim kontaktlari */
.unit-contacts {
  display: grid;
  gap: 4px;
  margin: 6px 0 10px;
}
.uc-row a {
  color: inherit;
  text-decoration: none;
}

.emp-list {
  display: grid;
  gap: 10px;
}
.emp-item {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 10px;
  align-items: flex-start;
  padding: 10px;
  border: 1px solid var(--line);
  border-radius: 14px;
  background: var(--panel);
}
.emp-avatar {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  background: #effaf3;
  color: #0ea95b;
  font-weight: 900;
  border: 1px solid #d9f3e4;
}
.emp-name {
  font-weight: 900;
}
.emp-sub {
  font-size: 13px;
  color: var(--muted);
  margin-top: 2px;
}
.emp-links {
  display: flex;
  gap: 12px;
  margin-top: 4px;
  flex-wrap: wrap;
}

.muted {
  color: var(--muted);
}
</style>
