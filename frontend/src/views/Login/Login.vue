<template>
  <div class="login-scene" :class="{ dark: isDark }">
    <div class="bg-radial"></div>

    <div class="wrap">
      <!-- Карточка входа -->
      <form class="card" :class="{ 'card--active': focusedCount > 0 }" @submit.prevent="onSubmit">
        <div class="brand">
          <span class="dot"></span>
          <span class="name">DocFlow</span>
        </div>

        <h1 class="title">Вход в систему</h1>

        <!-- Логин: плавающая метка -->
        <div class="field floating">
          <input
            v-model.trim="form.username"
            type="text"
            placeholder=" "
            autocomplete="username"
            @focus="onFocus"
            @blur="onBlur"
          />
          <label>Логин</label>
          <span class="focus-ring"></span>
        </div>

        <!-- Пароль: плавающая метка, кнопка показать/скрыть -->
        <div class="field floating with-eye">
          <input
            v-model.trim="form.password"
            :type="show ? 'text' : 'password'"
            placeholder=" "
            autocomplete="current-password"
            @focus="onFocus"
            @blur="onBlur"
          />
          <label>Пароль</label>

          <button
            class="eye"
            type="button"
            @click="show = !show"
            :aria-label="show ? 'Скрыть' : 'Показать'"
            @focus="onFocus"
            @blur="onBlur"
          >
            <svg viewBox="0 0 24 24">
              <path
                d="M12 5c5.4 0 9.9 5.1 9.9 7s-4.5 7-9.9 7S2.1 12.9 2.1 12 6.6 5 12 5zm0 4a3 3 0 1 0 0 6 3 3 0 0 0 0-6z"
                fill="currentColor"
              />
            </svg>
          </button>

          <span class="focus-ring"></span>
        </div>

        <button class="btn" type="submit" :disabled="loading">
          <span v-if="!loading">Войти</span>
          <span v-else class="spinner"></span>
        </button>

        <p class="error" v-if="error">Данные не верны</p>
      </form>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { API_BASE_URL } from "@/API.js";

const TOKEN_URL = `${API_BASE_URL}api/token/`;

export default {
  name: "Login",
  props: { isDark: { type: Boolean, default: false } },
  data() {
    return {
      form: { username: "", password: "" },
      show: false,
      loading: false,
      error: false,
      focusedCount: 0, // сколько элементов в фокусе (для 3D-анимации карточки)
    };
  },
  methods: {
    async onSubmit() {
      if (!this.form.username || !this.form.password) return;
      this.loading = true;
      this.error = false;
      try {
        const { data } = await axios.post(TOKEN_URL, this.form);
        localStorage.setItem("access", data.access);
        localStorage.setItem("refresh", data.refresh);
        axios.defaults.headers.common.Authorization = `Bearer ${data.access}`;
        this.$router.replace("/");
      } catch {
        this.error = true;
      } finally {
        this.loading = false;
      }
    },
    onFocus() {
      this.focusedCount++;
    },
    onBlur() {
      this.focusedCount = Math.max(0, this.focusedCount - 1);
    },
  },
};
</script>

<style scoped>
/* ====== СЦЕНА ====== */
.login-scene {
  --bg: #f5f7fb;
  --panel: #ffffff;
  --ink: #0f141a;
  --muted: #667085;
  --primary: #19c46d;
  --primary-ink: #14a85b;
  --line: #e8edf3;
  --ring: rgba(25, 196, 109, 0.22);

  height: 100vh;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;

  background: radial-gradient(1200px 600px at 75% -120px, rgba(25, 196, 109, 0.14), transparent 60%),
    radial-gradient(600px 300px at 12% 0, rgba(25, 196, 109, 0.1), transparent 55%), var(--bg);
}
.login-scene.dark {
  --bg: #0f1118;
  --panel: #151b22;
  --ink: #eaf0f6;
  --muted: #94a3b8;
  --primary: #2bdf83;
  --primary-ink: #17b469;
  --line: #222a36;
  --ring: rgba(43, 223, 131, 0.2);

  background: radial-gradient(1300px 700px at 75% -120px, rgba(43, 223, 131, 0.16), transparent 60%),
    radial-gradient(700px 320px at 10% 5%, rgba(43, 223, 131, 0.12), transparent 55%), var(--bg);
}
.bg-radial {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.wrap {
  position: relative;
  width: min(980px, 92vw);
  margin: auto;
  padding: 0 8px;
}

/* ====== КАРТОЧКА ====== */
.card {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.72), rgba(255, 255, 255, 0.56)),
    var(--panel);
  backdrop-filter: blur(14px);
  border: 1px solid var(--line);
  border-radius: 20px;
  padding: 26px 22px;
  box-shadow: 0 28px 65px rgba(22, 29, 39, 0.12);
  transform-style: preserve-3d;
  transition: transform 0.35s ease, box-shadow 0.35s ease, border-color 0.25s ease;
  max-width: 520px;
  margin: 0 auto;
}
.login-scene.dark .card {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.06), rgba(255, 255, 255, 0.03)),
    var(--panel);
}
.card--active {
  transform: perspective(1000px) translateY(-4px) rotateX(3deg);
  box-shadow: 0 38px 90px rgba(21, 200, 110, 0.28);
  border-color: rgba(25, 196, 109, 0.35);
}

.brand {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--muted);
  font-weight: 800;
  margin-bottom: 6px;
}
.dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: var(--primary);
  box-shadow: 0 0 0 6px rgba(25, 196, 109, 0.12);
}
.title {
  margin: 6px 0 14px;
  font-size: 28px;
  font-weight: 900;
  color: var(--ink);
}

/* ====== Плавающие метки ====== */
.field {
  position: relative;
  margin: 14px 0;
}
.floating input {
  width: 100%;
  height: 48px;
  border-radius: 12px;
  border: 1px solid var(--line);
  padding: 18px 12px 10px 12px; /* запас под поднятую метку */
  background: #fff;
  color: var(--ink);
  outline: 0;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.15s ease;
}
.login-scene.dark .floating input {
  background: transparent;
  color: var(--ink);
}
.floating input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 4px var(--ring);
  transform: translateZ(1px);
}

/* Лейбл поверх поля */
.floating label {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--muted);
  pointer-events: none;
  transition: transform 0.18s ease, color 0.18s ease, top 0.18s ease, font-size 0.18s ease,
    background-color 0.18s ease, padding 0.18s ease;
  background: transparent;
  padding: 0 6px;
}

/* Магия: placeholder=" " + :placeholder-shown — опускаем/поднимаем метку */
.floating input:focus + label,
.floating input:not(:placeholder-shown) + label {
  top: 2px;
  transform: translateY(0) scale(0.92);
  color: var(--primary-ink);
  font-weight: 700;
  background: var(--panel);
  border-radius: 6px;
}

/* декоративное свечение под инпутом */
.focus-ring {
  content: "";
  position: absolute;
  left: 10px;
  right: 10px;
  bottom: -6px;
  height: 10px;
  filter: blur(12px);
  background: radial-gradient(closest-side, rgba(25, 196, 109, 0.25), transparent 70%);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.25s ease;
}
.floating input:focus ~ .focus-ring {
  opacity: 1;
}

/* Кнопка «глаз» */
.with-eye .eye {
  position: absolute;
  right: 6px;
  top: 50%;
  transform: translateY(-50%);
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  color: var(--muted);
  background: transparent;
  border: none;
  cursor: pointer;
  border-radius: 10px;
}
.with-eye .eye:hover {
  background: rgba(0, 0, 0, 0.04);
}
.login-scene.dark .with-eye .eye:hover {
  background: rgba(255, 255, 255, 0.06);
}

/* ====== КНОПКА ВХОДА ====== */
.btn {
  width: 100%;
  height: 48px;
  margin-top: 14px;
  border-radius: 12px;
  border: 0;
  cursor: pointer;
  font-weight: 900;
  color: #fff;
  background: linear-gradient(180deg, #27d77d, #19c46d);
  box-shadow: 0 18px 38px rgba(21, 200, 110, 0.35);
  transition: transform 0.15s ease, box-shadow 0.2s ease, filter 0.2s ease;
}
.btn:hover {
  transform: translateY(-1px);
  filter: brightness(1.03);
}
.btn:active {
  transform: translateY(1px);
}

/* Ошибка */
.error {
  margin-top: 10px;
  color: #ef4444;
  font-weight: 800;
  text-align: center;
}

/* Лоадер */
.spinner {
  width: 18px;
  height: 18px;
  border: 3px solid rgba(255, 255, 255, 0.35);
  border-top-color: #fff;
  border-radius: 50%;
  display: inline-block;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Адаптив */
@media (max-width: 560px) {
  .title {
    font-size: 24px;
  }
}
</style>
