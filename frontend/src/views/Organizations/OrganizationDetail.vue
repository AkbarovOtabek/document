<script>
import axios from 'axios'
import { API_BASE_URL } from '@/API.js'

const ORG_DETAIL_URL = `${API_BASE_URL}api/organizations/`

export default {
  name: 'OrganizationDetail',
  props: {
    slug:   { type: String, required: true },
    isDark: { type: Boolean, default: false },
  },
  data(){
    return {
      loading: false,
      error: '',
      org: null,
      // 3D
      rx: 0, ry: 0,
    }
  },
  computed:{
    themeClass(){ return this.isDark ? 'dark' : '' },
    cubeStyle(){ return { transform: `rotateX(${this.rx}deg) rotateY(${this.ry}deg)` } },
    // fallback-аватар (если логотипа нет)
    avatarText(){
      if (!this.org || this.org.logo) return ''
      const initials = (this.org.name||'').split(' ').map(w=>w[0]).join('').slice(0,2).toUpperCase()
      return initials || '🏦'
    },
  },
  async mounted(){ await this.fetchDetail() },
  watch:{ slug: { async handler(){ await this.fetchDetail() } } },
  methods:{
    async fetchDetail(){
      try{
        this.loading = true; this.error = ''
        const { data } = await axios.get(`${ORG_DETAIL_URL}${this.slug}/`)
        this.org = data
      }catch(e){
        console.error(e)
        this.error = 'Не удалось загрузить организацию'
      }finally{
        this.loading = false
      }
    },
    goBack(){ this.$router.back() },

    // 3D — мягкий tilt
    onTilt(e){
      const card = e.currentTarget.querySelector('.card-inner')
      const r = e.currentTarget.getBoundingClientRect()
      const x = ((e.clientX - r.left) / r.width) * 2 - 1
      const y = ((e.clientY - r.top) / r.height) * 2 - 1
      card.style.transform = `rotateX(${-y * 6}deg) rotateY(${x * 6}deg) translateZ(6px)`
      card.style.boxShadow = `${-x * 14}px ${y * 16}px 40px rgba(0,0,0,.22)`
    },
    resetTilt(e){
      const card = e.currentTarget.querySelector('.card-inner')
      card.style.transform = ''
      card.style.boxShadow = ''
    },
    // удобные ссылки
    tel(h){ return h ? `tel:${String(h).replace(/\s+/g,'')}` : '#' },
    mail(m){ return m ? `mailto:${m}` : '#' },
    mapLink(addr){ return addr ? `https://maps.google.com/?q=${encodeURIComponent(addr)}` : '#' },
  }
}
</script>

<template>
  <div class="scene" :class="themeClass">
    <!-- HERO -->
    <header class="hero">
      <div class="hero-left">
        <button class="btn ghost" @click="goBack">← Назад</button>
        <h1 class="title">{{ org?.name || 'Организация' }}</h1>
        <div class="subtitle">
          <span class="pill">{{ org?.category_name || org?.category_slug || 'Категория' }}</span>
          <span class="muted">·</span>
          <span class="muted"><code>{{ org?.name || slug }}</code></span>
        </div>
      </div>
    </header>

    <p v-if="error" class="error">{{ error }}</p>

    <!-- КОНТЕНТ: только реальные поля API -->
    <section v-if="org" class="grid">
      <article class="card profile" @mousemove="onTilt" @mouseleave="resetTilt">
        <div class="card-inner">
          <div class="row head">
            <div class="avatar">
              <img v-if="org.logo" :src="org.logo" alt="" />
              <span v-else>{{ avatarText }}</span>
            </div>
            <div class="info">
              <div class="name">{{ org.name }}</div>
              <div class="tags">
                <span class="tag">{{ org.category_name || org.category_slug }}</span>
                <span class="tag ghost">Создано: {{ org.time_create }}</span>
                <span class="tag ghost">Обновлено: {{ org.updated }}</span>
              </div>
            </div>
          </div>

          <p v-if="org.description" class="desc">{{ org.description }}</p>

          <div class="details">
            <div>
              <strong>Адрес</strong>
              <a :href="mapLink(org.address)" target="_blank" class="muted link">{{ org.address || '—' }}</a>
            </div>
            <div>
              <strong>Lotus</strong>
              <span class="muted">{{ org.lotus || '—' }}</span>
            </div>
            <div>
              <strong>Телефон</strong>
              <a :href="tel(org.phone)" class="muted link">{{ org.phone || '—' }}</a>
            </div>
            <div>
              <strong>Email</strong>
              <a :href="mail(org.email)" class="muted link">{{ org.email || '—' }}</a>
            </div>
            <div>
              <strong>Slug</strong>
              <code>{{ org.slug }}</code>
            </div>
          </div>
        </div>
      </article>

      <!-- Небольшие «заполняющие» карточки — чисто визуально -->
      <article class="card plain" @mousemove="onTilt" @mouseleave="resetTilt">
        <div class="card-inner">
          <h3>Документы & интеграции</h3>
          <p class="muted">Список и статусы интеграций, документы, реквизиты — когда появятся в API, просто отрисуй здесь.</p>
        </div>
      </article>
    </section>

    <!-- Лоадер-скелет -->
    <section v-else-if="loading" class="grid">
      <article class="card profile">
        <div class="card-inner skeleton"></div>
      </article>
      <article class="card plain">
        <div class="card-inner skeleton"></div>
      </article>
    </section>
  </div>
</template>

<style scoped>
/* ===== THEME ===== */
.scene{
  --bg:#f6f7fb; --panel:#ffffff; --ink:#0f141a; --muted:#6b7280;
  --primary:#19c46d; --primary-ink:#0ea95b;
  --line:#e6e8ee; --ring:rgba(25,196,109,.24);
  min-height: calc(100vh - 64px);
  background:
    radial-gradient(1200px 600px at 70% -100px, rgba(25,196,109,.10), transparent 60%),
    var(--bg);
  color: var(--ink);
}
.scene.dark{
  --bg:#0f1118; --panel:#151b22; --ink:#eaf0f6; --muted:#94a3b8;
  --primary:#2bdf83; --primary-ink:#17b469;
  --line:#222a36; --ring:rgba(43,223,131,.18);
  background:
    radial-gradient(1300px 700px at 70% -120px, rgba(43,223,131,.10), transparent 60%),
    var(--bg);
}

/* ===== HERO ===== */
.hero{
  display:grid; grid-template-columns: 1.1fr .9fr;
  gap: 18px; align-items: center; padding: 20px 22px 6px;
}
@media (max-width: 980px){ .hero{ grid-template-columns:1fr; } }

.hero-left .title{ margin: 8px 0 4px;font-size: 32px; line-height:1.1; }
.subtitle{ display:flex; align-items:center; gap:10px; }
.pill{ display:inline-flex; align-items:center; height:24px; padding:0 10px; border-radius:999px;
  background: rgba(25,196,109,.15); color: var(--primary); border:1px solid rgba(25,196,109,.25); font-weight:800; font-size:12px; }
.muted{ color: var(--muted); }
.btn{ height:38px; padding:0 12px; border-radius:12px; border:1px solid var(--line); background:transparent; color:var(--ink); font-weight:800; cursor:pointer; }

/* ===== CUBE ===== */
.cube-wrap{ position:relative; width: clamp(260px, 42vw, 420px); aspect-ratio:1/1; margin-left:auto; perspective:900px; filter: drop-shadow(0 40px 80px rgba(0,0,0,.25)); }
.cube{ position:absolute; inset:0; transform-style:preserve-3d; animation: idle 8s ease-in-out infinite alternate; }
@keyframes idle{ 0%{transform: rotateX(-8deg) rotateY(20deg);} 100%{transform: rotateX(4deg) rotateY(-15deg);} }
.face{
  position:absolute; inset:0; display:flex; align-items:center; justify-content:center;
  font-weight:900; letter-spacing:2px; color:#fff; text-shadow:0 2px 18px rgba(0,0,0,.35);
  border-radius:18px; background:
    linear-gradient(145deg, rgba(255,255,255,.08), rgba(255,255,255,.02)),
    linear-gradient(145deg, var(--primary), var(--primary-ink));
  box-shadow: inset 0 0 0 1px rgba(255,255,255,.12);
}
.f1{ transform: translateZ(90px); } .f2{ transform: rotateY(90deg) translateZ(90px); }
.f3{ transform: rotateY(180deg) translateZ(90px); } .f4{ transform: rotateY(-90deg) translateZ(90px); }
.f5{ transform: rotateX(90deg) translateZ(90px); } .f6{ transform: rotateX(-90deg) translateZ(90px); }
.halo{ position:absolute; inset:auto 0 -16px 0; height:24px; filter: blur(8px);
  background: radial-gradient(closest-side, rgba(25,196,109,.50), transparent 70%); }

/* ===== GRID ===== */
.grid{
  display:grid; grid-template-columns: 1.2fr .8fr;
  gap: 18px; padding: 10px 22px 24px;
}
@media (max-width: 980px){ .grid{ grid-template-columns: 1fr; } }

/* ===== CARDS ===== */
.card{ perspective:900px; }
.card .card-inner{
  background: linear-gradient(180deg, rgba(255,255,255,.05), rgba(255,255,255,0)), var(--panel);
  border: 1px solid var(--line);
  border-radius: 18px; padding: 16px;
  transform-style: preserve-3d; transition: transform .22s ease, box-shadow .22s ease;
  box-shadow: 0 18px 38px rgba(0,0,0,.12);
}

/* Profile */
.profile .head{ display:flex; gap:14px; align-items:center; margin-bottom:8px; }
.avatar{
  width:64px; height:64px; border-radius:16px; border:1px solid var(--line); display:grid; place-items:center;
  background: linear-gradient(180deg, rgba(25,196,109,.18), rgba(25,196,109,.08));
  font-weight:900; font-size:20px; color:#fff; text-shadow:0 1px 12px rgba(0,0,0,.25);
}
.avatar img{ width:100%; height:100%; object-fit:cover; border-radius:16px; }
.info .name{ font-size:20px; font-weight:900; margin-bottom:4px; }
.tags{ display:flex; gap:8px; flex-wrap:wrap; }
.tag{ display:inline-flex; align-items:center; height:24px; padding:0 10px; border-radius:999px; background: rgba(25,196,109,.15); color: var(--primary); border:1px solid rgba(25,196,109,.25); font-weight:800; font-size:12px; }
.tag.ghost{ background: transparent; color: var(--muted); border-color: var(--line); }

.desc{ margin: 8px 0 10px; color: var(--muted); }
.details{
  display:grid; grid-template-columns: repeat(2, minmax(0,1fr));
  gap: 10px; margin-top: 8px;
}
.details .link{ text-decoration:none; }
.details strong{ display:block; font-size:12px; color: var(--muted); }
.details span, .details a{ font-size:14px; }

/* simple filler */
.plain h3{ margin:0 0 6px; }
.plain .muted{ font-size:14px; }

/* skeleton */
.skeleton{
  min-height: 180px;
  background: linear-gradient(90deg, rgba(0,0,0,.06), rgba(0,0,0,.02), rgba(0,0,0,.06));
  background-size: 200% 100%;
  animation: shimmer 1.2s infinite;
}
@keyframes shimmer{
  0%{ background-position: 200% 0; }
  100%{ background-position: -200% 0; }
}

/* misc */
.error{ color:#ef4444; margin: 8px 22px; }
</style>
