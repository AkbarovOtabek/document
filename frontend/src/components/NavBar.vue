<template>
  <div class="navigation" :class="{ dark: !isDark }">
    <ul>
      <li
        v-for="(value, i) in items"
        :key="value.to"
        class="list"
        :class="{ active: isActive(value) }"
      >
        <RouterLink :to="value.to">
          <span class="icon"><ion-icon :name="value.icon" /></span>
          <span class="text">{{ value.label }}</span>
        </RouterLink>
      </li>

      <!-- индикатор по computed activeIndex -->
      <div class="indicator" :style="indicatorStyle"></div>
    </ul>
  </div>
</template>

<script>
export default {
  name: "NavBar",
  props: {
    isDark: { type: Boolean, required: true },
  },
  data() {
    return {
      items: [
        // Раздел “Организации”: считаем активным также category/list/detail
        {
          to: "/",
          icon: "home-outline",
          label: "Организации",
          match: ["/", "/category/organizations"], // <-- новые префиксы
        },
        { to: "/users", icon: "person-outline", label: "Пользователи", match: ["/users"] },
        {
          to: "/search-documents",
          icon: "chatbubble-ellipses-outline",
          label: "Поиск писем",
          match: ["/search-documents"],
        },
        {
          to: "/statistika",
          icon: "analytics-outline",
          label: "Статистика",
          match: ["/statistika"],
        },
        { to: "/account", icon: "settings-outline", label: "Аккаунт", match: ["/account"] },
      ],
      stepPx: 110, // шаг индикатора (подогнан под твою верстку)
      baseOffsetPx: 0, // если нужно сдвинуть базу — поменяй
    };
  },
  computed: {
    // индекс активного пункта
    activeIndex() {
      const idx = this.items.findIndex((it) => this.isActive(it));
      return idx === -1 ? 0 : idx;
    },
    // стиль индикатора
    indicatorStyle() {
      const x = this.baseOffsetPx + this.stepPx * this.activeIndex;
      return { transform: `translateX(${x}px)` };
    },
  },
  methods: {
    norm(p) {
      return String(p || "").replace(/\/+$/, "") || "/";
    },
    isActive(item) {
      const current = this.norm(this.$route.path);
      // точное совпадение с to
      if (current === this.norm(item.to)) return true;
      // префиксное совпадение по любому match
      if (Array.isArray(item.match)) {
        return item.match.some((prefix) => {
          const pref = this.norm(prefix);
          // чтобы '/' не съедал все, проверяем отдельно
          if (pref === "/") return current === "/";
          return current.startsWith(pref);
        });
      }
      return false;
    },
  },
};
</script>

<style scoped>
.navigation {
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  position: fixed;
  height: 70px;
  background: #fff;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  z-index: 50;
}

.navigation ul {
  display: flex;
  width: 550px;
  position: relative;
}
.navigation ul li {
  position: relative;
  width: 130px;
  height: 70px;
  z-index: 1;
}
.navigation ul li a {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  width: 100%;
  text-align: center;
  font-weight: 500;
}
.navigation ul li a .icon {
  line-height: 75px;
  font-size: 1.5em;
  transition: 0.5s;
  color: var(--clr);
}
.navigation ul li.active a .icon {
  transform: translateY(-32px);
}
.navigation ul li a .text {
  position: absolute;
  color: var(--clr);
  font-weight: 400;
  font-size: 0.75em;
  letter-spacing: 0.05em;
  transition: 0.5s;
  opacity: 0;
  transform: translateY(20px);
}
.navigation ul li.active a .text {
  opacity: 1;
  transform: translateY(10px);
}

/* индикатор теперь двигаем через :style */
.indicator {
  position: absolute;
  top: -50%;
  width: 70px;
  height: 70px;
  left: 20px;
  background: var(--button-green-dark);
  border-radius: 50%;
  border: 7px solid var(--clr);
  transition: transform 0.35s cubic-bezier(0.22, 0.61, 0.36, 1);
}
.indicator::before,
.indicator::after {
  content: "";
  position: absolute;
  top: 50%;
  width: 20px;
  height: 20px;
  background: transparent;
}
.indicator::before {
  left: -22.5px;
  border-top-right-radius: 20px;
  box-shadow: 0 -10px 0 0 var(--clr);
}
.indicator::after {
  right: -22.5px;
  border-top-left-radius: 20px;
  box-shadow: -1px -10px 0 0 var(--clr);
}

/* тёмная тема */
.navigation.dark {
  background: var(--clr);
}
.navigation.dark ul li a .icon,
.navigation.dark ul li a .text {
  color: #fff;
}
.navigation.dark .indicator {
  border: 7px solid #fff;
}
.navigation.dark .indicator::before,
.navigation.dark .indicator::after {
  box-shadow: 0 -10px 0 0 #fff;
}
</style>
