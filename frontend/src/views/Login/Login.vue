<!-- src/views/Login.vue -->
<template>
  <div class="login-scene" :class="{ dark: isDark }">
    <div class="bg-radial"></div>

    <!-- Контейнер -->
    <div class="wrap">
      <!-- Карточка -->
      <form class="card" @submit.prevent="onSubmit" @mousemove="tilt" @mouseleave="resetTilt">
        <div class="brand">
          <span class="dot"></span>
          <span class="name">DocFlow</span>
        </div>

        <h1 class="title">Вход в систему</h1>

        <div class="field">
          <label>Логин</label>
          <input
            v-model.trim="form.username"
            type="text"
            placeholder="username"
            autocomplete="username"
          />
        </div>

        <div class="field">
          <label>Пароль</label>
          <div class="pwd">
            <input
              v-model.trim="form.password"
              :type="show ? 'text' : 'password'"
              placeholder="••••••••"
              autocomplete="current-password"
            />
            <button class="eye" type="button" @click="show=!show" :aria-label="show ? 'Скрыть' : 'Показать'">
              <svg viewBox="0 0 24 24"><path d="M12 5c5.4 0 9.9 5.1 9.9 7s-4.5 7-9.9 7S2.1 12.9 2.1 12 6.6 5 12 5zm0 4a3 3 0 1 0 0 6 3 3 0 0 0 0-6z" fill="currentColor"/></svg>
            </button>
          </div>
        </div>

        <button class="btn" type="submit" :disabled="loading">
          <span v-if="!loading">Enter</span>
          <span v-else class="spinner"></span>
        </button>

        <p class="error" v-if="error">Данные не верны</p>
      </form>

      <!-- 3D куб справа -->
      <div class="cube-zone" @mousemove="onCubeMove" @mouseleave="resetCube">
        <div class="cube" :style="cubeStyle">
          <div class="face f1">BANK</div>
          <div class="face f2"></div>
          <div class="face f3"></div>
          <div class="face f4"></div>
          <div class="face f5"></div>
          <div class="face f6"></div>
        </div>
        <div class="halo"></div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { API_BASE_URL } from '@/API.js'

const TOKEN_URL = `${API_BASE_URL}api/auth/token/`

export default {
  name: 'Login',
  props: { isDark: { type: Boolean, default: false } },
  data() {
    return {
      form: { username: '', password: '' },
      show: false,
      loading: false,
      error: false,
      // 3D
      rx: 0, ry: 0,
    }
  },
  computed: {
    cubeStyle() {
      return { transform: `rotateX(${this.rx}deg) rotateY(${this.ry}deg)` }
    }
  },
  methods: {
    async onSubmit() {
      if (!this.form.username || !this.form.password) return
      this.loading = true; this.error = false
      try {
        const { data } = await axios.post(TOKEN_URL, this.form)
        localStorage.setItem('access', data.access)
        localStorage.setItem('refresh', data.refresh)
        axios.defaults.headers.common.Authorization = `Bearer ${data.access}`
        this.$router.replace('/')
      } catch {
        this.error = true
      } finally {
        this.loading = false
      }
    },
    // 3D карточка
    tilt(e) {
      const card = e.currentTarget
      const r = card.getBoundingClientRect()
      const x = ((e.clientX - r.left) / r.width - 0.5) * 2
      const y = ((e.clientY - r.top) / r.height - 0.5) * 2
      card.style.transform = `rotateX(${-y * 4.5}deg) rotateY(${x * 6}deg)`
      card.style.boxShadow = `${-x * 18}px ${y * 20}px 50px rgba(0,0,0,.15)`
    },
    resetTilt(e) {
      const card = e.currentTarget
      card.style.transform = ''
      card.style.boxShadow = ''
    },
    // 3D куб
    onCubeMove(e) {
      const r = e.currentTarget.getBoundingClientRect()
      const cx = r.left + r.width / 2
      const cy = r.top + r.height / 2
      const dx = (e.clientX - cx) / r.width
      const dy = (e.clientY - cy) / r.height
      this.ry = dx * 30; this.rx = -dy * 20
    },
    resetCube() { this.rx = 0; this.ry = 0 },
  }
}
</script>

<style scoped>
/* ====== СЦЕНА ====== */
.login-scene{
  --bg:#f5f7fb; --panel:#fff; --ink:#0f141a; --muted:#667085;
  --primary:#19c46d; --line:#e8edf3; --ring:rgba(25,196,109,.22);
  min-height:100vh; display:flex; align-items:center; justify-content:center;
  background: radial-gradient(1200px 600px at 75% -120px, rgba(25,196,109,.14), transparent 60%), var(--bg);
}
.login-scene.dark{
  --bg:#0f1118; --panel:#151b22; --ink:#eaf0f6; --muted:#94a3b8;
  --primary:#2bdf83; --line:#222a36; --ring:rgba(43,223,131,.18);
  background: radial-gradient(1300px 700px at 75% -120px, rgba(43,223,131,.16), transparent 60%), var(--bg);
}
.bg-radial{ position:absolute; inset:0; background: radial-gradient(600px 300px at 12% 0, rgba(25,196,109,.14), transparent 50%); pointer-events:none; }
.wrap{ position:relative; width:min(1100px, 92vw); margin:auto; display:grid; grid-template-columns: 520px 1fr; gap:28px; align-items:center; }
@media (max-width: 980px){ .wrap{ grid-template-columns: 1fr; } }

/* ====== КАРТОЧКА ====== */
.card{
  background: linear-gradient(180deg, rgba(255,255,255,.65), rgba(255,255,255,.55)), var(--panel);
  backdrop-filter: blur(14px);
  border:1px solid var(--line);
  border-radius:20px; padding:24px 22px;
  box-shadow: 0 30px 70px rgba(22, 29, 39, .12);
  transition: transform .25s ease, box-shadow .25s ease;
  transform-style: preserve-3d;
}
.login-scene.dark .card{
  background: linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,.02)), var(--panel);
}
.brand{ display:flex; align-items:center; gap:8px; color:var(--muted); font-weight:800; margin-bottom:6px; }
.dot{ width:10px; height:10px; border-radius:999px; background:var(--primary); box-shadow:0 0 0 6px rgba(25,196,109,.12); }
.title{ margin:6px 0 12px; font-size:28px; font-weight:900; color:var(--ink); }

.field{ display:grid; gap:6px; margin:10px 0; }
label{ font-size:12px; color:var(--muted); font-weight:800; }
input{
  height:44px; border-radius:12px; border:1px solid var(--line);
  padding:0 12px; background:#fff; color:var(--ink); outline:0;
}
.login-scene.dark input{ background:transparent; color:var(--ink); }
input:focus{ border-color:var(--primary); box-shadow:0 0 0 4px var(--ring); }

.pwd{ position:relative; }
.eye{
  position:absolute; right:6px; top:50%; transform:translateY(-50%);
  width:34px; height:34px; display:grid; place-items:center; color:var(--muted);
  background:transparent; border:none; cursor:pointer;
}

.btn{
  width:100%; height:46px; margin-top:12px;
  border-radius:12px; border:0; cursor:pointer; font-weight:900; color:#fff;
  background: linear-gradient(180deg, #27d77d, #19c46d);
  box-shadow: 0 18px 38px rgba(21, 200, 110, .35);
  transition: transform .15s ease;
}
.btn:hover{ transform: translateY(-1px); }
.btn:active{ transform: translateY(1px); }

.error{ margin-top:10px; color:#ef4444; font-weight:800; text-align:center; }

/* loader */
.spinner{
  width:18px; height:18px; border:3px solid rgba(255,255,255,.35); border-top-color:#fff;
  border-radius:50%; display:inline-block; animation: spin .8s linear infinite;
}
@keyframes spin { to{ transform: rotate(360deg) } }

/* ====== КУБ ====== */
.cube-zone{ position:relative; width:min(520px, 90vw); aspect-ratio: 1/1; margin:0 auto; perspective: 900px; }
.cube{ position:absolute; inset:0; transform-style:preserve-3d; animation: idle 9s ease-in-out infinite alternate; }
@keyframes idle{ 0%{ transform: rotateX(-8deg) rotateY(18deg); } 100%{ transform: rotateX(6deg) rotateY(-18deg); } }
.face{
  position:absolute; inset:0; display:flex; align-items:center; justify-content:center;
  font-weight:900; letter-spacing:2px; color:#fff;
  background: linear-gradient(160deg, #2fe082, #19c46d);
  border-radius:14px; box-shadow: inset 0 0 0 1px rgba(255,255,255,.18);
}
.f1{ transform: translateZ(95px); }
.f2{ transform: rotateY(90deg) translateZ(95px); }
.f3{ transform: rotateY(180deg) translateZ(95px); }
.f4{ transform: rotateY(-90deg) translateZ(95px); }
.f5{ transform: rotateX(90deg) translateZ(95px); }
.f6{ transform: rotateX(-90deg) translateZ(95px); }
.halo{ position:absolute; inset:auto 0 -22px 0; height:28px; filter:blur(10px);
  background: radial-gradient(closest-side, rgba(25,196,109,.55), transparent 70%); }
</style>
