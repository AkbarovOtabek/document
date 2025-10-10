<template>
  <div class="app" :class="{'dark': isDark}">
    <!-- Глобальный топбар -->
    <header class="topbar">
      <div class="brand">
        <span class="dot"></span>
        <strong>DocFlow</strong>
      </div>

      <div class="top-actions">
        <button class="btn ghost" @click="toggleTheme">
          {{ isDark ? '☀︎ Light' : '☾ Dark' }}
        </button>
      </div>
    </header>

    <NavBar v-if="!$route.meta.hideNav" :isDark="isDark"/>
    <RouterView v-slot="{ Component }">
      <component :is="Component" :is-dark="isDark" />
    </RouterView>
  </div>
</template>

<script>
import NavBar from './components/NavBar.vue';
export default {
  name: 'App',
  components: { NavBar },
  data() {
    return { isDark: false }
  },
  methods: {
    toggleTheme() {
      this.isDark = !this.isDark
    },
  },
}
</script>

<style>
html, body, #app { height: 100%; }
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg, #fff);
}
.topbar{
  position: sticky; 
  top: 0; 
  z-index: 40;
  height: 64px;
  display:flex; 
  align-items:center; 
  justify-content:space-between;
  padding: 0 22px;
  background: #ffffffcc; 
  backdrop-filter: blur(8px) saturate(160%);
  border-bottom: 1px solid rgba(0,0,0,.06);
}
.brand{ 
  display:flex; 
  align-items:center; 
  gap:10px; 
  font-size:18px; 
  font-weight:800; 
}
.brand .dot{ 
  width:10px; 
  height:10px; 
  border-radius:50%; 
  background:#19c46d; 
  box-shadow:0 0 16px #19c46d; 
}
.top-actions{ 
  display:flex; 
  gap:10px; 
}
.btn{
  height: 38px; 
  padding: 0 14px;
  border-radius: 10px; 
  border: 1px solid rgba(0,0,0,.08);
  background: #fff; color: #0f141a; 
  font-weight: 700; 
  cursor: pointer; 
  transition:.2s ease;
}
.btn:hover{ 
  transform: translateY(-1px); 
  box-shadow: 0 10px 24px rgba(0,0,0,.08); }
.btn.ghost{ 
  background: transparent; 
}

.app.dark {
background: var(--clr);
}

.app.dark .topbar{
  background: var(--clr-top-bar);
  color: #fff;
}
.app.dark .btn{
  color: #fff;
  border-color: #fff;
}
</style>
