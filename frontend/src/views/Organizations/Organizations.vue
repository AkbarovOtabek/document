<script>
import axios from "axios";
import { API_BASE_URL } from "../../API.js";

const LIST_URL = `${API_BASE_URL}api/categories/list/`;
const CREATE_URL = `${API_BASE_URL}api/categories/create/`;

export default {
  name: "Organizations",
  props: { isDark: { type: Boolean, required: true } },
  data() {
    return {
      loading: false,
      error: "",
      categories: [],
      // hero cube
      rx: 0, ry: 0,

      // UI
      showCreate: false,

      // форма создания
      form: {
        name: "",
        description: "",
        badge: "",
      },
      showEdit: false,  
      saving: false,
      editSlug: null,
    editForm: { name: "", badge: "", description: "" },
    };
  },
  computed: {
    cubeStyle() {
      return { transform: `rotateX(${this.rx}deg) rotateY(${this.ry}deg)` };
    },
    canSubmit() {
      return this.form.name.trim() && this.form.badge.trim();
    },
  },
  mounted() {
    this.fetchCategories();
  },
  methods: {
    async fetchCategories() {
      try {
        this.loading = true; this.error = "";
        const { data } = await axios.get(LIST_URL);
        this.categories = Array.isArray(data) ? data : (data.results || []);
      } catch (e) {
        console.error(e);
        this.error = "Не удалось загрузить категории";
      } finally {
        this.loading = false;
      }
    },

    async createCategory() {
      if (!this.canSubmit || this.saving) return;
      try {
        this.saving = true; this.error = "";
        const payload = {
          name: this.form.name.trim(),
          description: this.form.description.trim(),
          badge: this.form.badge.trim(),
        };
        await axios.post(CREATE_URL, payload);
        this.form = { name: "", description: "", badge: "" };
        this.showCreate = false;
        this.fetchCategories();
      } catch (e) {
        console.error(e);
        this.error = "Не удалось создать категорию";
      } finally {
        this.saving = false;
      }
    },
   async updateCategory() {
  if (!this.editSlug) return;
  try {
    this.saving = true;
    await axios.patch(`${LIST_URL}${this.editSlug}/`, {
      name: this.editForm.name.trim(),
      badge: this.editForm.badge.trim(),
      description: this.editForm.description.trim(),
    });
    this.closeEdit();
    this.fetchCategories();
  } catch (e) {
    console.error(e);
    alert("Не удалось сохранить изменения");
  } finally {
    this.saving = false;
  }
},
    openEdit(c) {
      console.log('щзу')
  // у объекта c должен быть c.slug (бэкенд должен отдавать это поле)
  this.editSlug = c.slug;
  this.editForm = {
    name: c.name || "",
    badge: c.badge || "",
    description: c.description || "",
  };
  this.showEdit = true;
},
    closeEdit() {
  this.showEdit = false;
  this.editSlug = null;
},
openCategory(c) {
    // ожидаем, что у категории есть поле c.slug из API
    this.$router.push({ name: 'orgs-by-category', params: { slug: c.slug } })
  },
    // 3D эффекты карточек и куба
    onTilt(e) {
      const card = e.currentTarget.querySelector(".card-inner");
      const r = e.currentTarget.getBoundingClientRect();
      const x = ((e.clientX - r.left) / r.width) * 2 - 1;
      const y = ((e.clientY - r.top) / r.height) * 2 - 1;
      card.style.transform = `rotateX(${-y * 10}deg) rotateY(${x * 10}deg) translateZ(6px)`;
      card.style.boxShadow = `${-x * 16}px ${y * 18}px 48px rgba(0,0,0,.25)`;
    },
    resetTilt(e) {
      const card = e.currentTarget.querySelector(".card-inner");
      card.style.transform = "";
      card.style.boxShadow = "";
    },
    onCubeMove(e) {
      const r = e.currentTarget.getBoundingClientRect();
      const cx = r.left + r.width / 2;
      const cy = r.top + r.height / 2;
      const dx = (e.clientX - cx) / r.width;
      const dy = (e.clientY - cy) / r.height;
      this.ry = dx * 30; this.rx = -dy * 30;
    },
    resetCube() { this.rx = 0; this.ry = 0; },
  },
};
</script>

<template>
  <div class="scene" :class="{ dark: isDark }">
    <!-- HERO -->
    <section class="hero">
      <div class="hero-left">
        <h1>Категории <span class="hl">организаций</span><br>в одном месте</h1>
        <p class="lead">
          Управляй банками, платёжными организациями и системами через удобный интерфейс.
          Гибкие фильтры, мгновенный поиск, чистый API.
        </p>

        <div class="cta-row">
          <button class="btn primary big" @click="showCreate = true">Создать категорию</button>
          <button class="btn ghost big" @click="fetchCategories">
            Обновить список
          </button>
          <span class="chip" v-if="loading">Загрузка…</span>
          <span class="chip" v-else>{{ categories.length }} шт.</span>
        </div>
        <p v-if="error" class="error">{{ error }}</p>
      </div>

      <!-- 3D-куб -->
      <div class="hero-right">
        <div class="cube-wrap" @mousemove="onCubeMove" @mouseleave="resetCube">
          <div class="cube" :style="cubeStyle">
            <div class="face f1">BANK</div>
            <div class="face f2">PAY</div>
            <div class="face f3">SYS</div>
            <div class="face f4">DOC</div>
            <div class="face f5">ORG</div>
            <div class="face f6">API</div>
          </div>
          <div class="halo"></div>
        </div>
      </div>
    </section>

    <!-- СПИСОК КАРТОЧЕК -->
    <section class="cards">
      <article
        v-for="c in categories"
        :key="c.id"
        class="card"
        @mousemove="onTilt"
        @mouseleave="resetTilt"
      >
        <div class="card-inner">
          <div class="card-top">
            <span class="badge">{{ c.badge || 'Категория' }}</span>
            <div class="dots"><span></span><span></span><span></span></div>
          </div>

          <h3>{{ c.name }}</h3>
          <p class="muted">{{ c.description || 'Описание категории отсутствует.' }}</p>

          <div class="metrics">
            <div><strong>{{ c.objects_count ?? 0 }} </strong><span> объектов</span></div>
            <div><strong>{{ c.today_count ?? 0 }} </strong><span> за сегодня</span></div>
          </div>

          <div class="card-actions">
            <button class="btn subtle" @click="openCategory(c)">Открыть</button>
            <button class="btn ghost" @click="openEdit(c)">Настроить</button>
          </div>
        </div>
      </article>

      <div v-if="!loading && categories.length === 0" class="empty card">
        <p>Категорий пока нет.</p>
        <p class="muted">Создай первую с помощью кнопки «Создать категорию».</p>
      </div>
    </section>

    <!-- МОДАЛ СОЗДАНИЯ -->
    <transition name="fade">
      <div class="modal" v-if="showCreate" @click.self="showCreate=false">
        <div class="modal-card" @mousemove="onTilt" @mouseleave="resetTilt">
          <div class="modal-inner card-inner">
            <h3 class="modal-title">Новая категория</h3>
            <div class="row">
              <label>Название *</label>
              <input v-model="form.name" class="input" type="text" placeholder="Например: Банки" />
            </div>
            <div class="row">
              <label>Бейдж (короткая метка) *</label>
              <input v-model="form.badge" class="input" type="text" placeholder="Платежи / Банки / Системы" />
            </div>
            <div class="row">
              <label>Описание</label>
              <textarea v-model="form.description" class="input area" rows="4" placeholder="Короткое описание категории"></textarea>
            </div>

            <div class="row submit">
              <button class="btn primary" :disabled="!canSubmit || saving" @click="createCategory">
                {{ saving ? 'Сохраняем…' : 'Создать' }}
              </button>
              <button class="btn ghost" @click="showCreate=false">Отмена</button>
            </div>
          </div>
        </div>
      </div>
    </transition>
     <!-- МОДАЛ Обновления -->
    <transition name="fade">
  <div class="modal" v-if="showEdit" @click.self="closeEdit">
    <div class="modal-card" @mousemove="onTilt" @mouseleave="resetTilt">
      <div class="modal-inner card-inner">
        <h3 class="modal-title">Редактировать категорию</h3>

        <div class="row">
          <label>Название *</label>
          <input v-model="editForm.name" class="input" type="text" />
        </div>
        <div class="row">
          <label>Бейдж *</label>
          <input v-model="editForm.badge" class="input" type="text" />
        </div>
        <div class="row">
          <label>Описание</label>
          <textarea v-model="editForm.description" class="input area" rows="4"></textarea>
        </div>

        <div class="row submit">
          <button class="btn primary" :disabled="saving" @click="updateCategory">Сохранить</button>
          <button class="btn ghost" @click="closeEdit">Отмена</button>
        </div>
      </div>
    </div>
  </div>
</transition>
  </div>
</template>

<style scoped>
/* ====== ТЕМА ====== */
.scene{
  --bg:#f6f7fb; --panel:#fff; --ink:#0f141a; --muted:#6b7280;
  --primary:#19c46d; --primary-ink:#0ea95b; --ring:rgba(25,196,109,.25); --line:#e6e8ee;
  min-height: calc(100vh - 64px);
  background: radial-gradient(1200px 600px at 70% -100px, rgba(25,196,109,.18), transparent 60%), var(--bg);
  color: var(--ink); display:flex; flex-direction:column;
}
.scene.dark{
  --bg:#0f1118; --panel:#151b22; --ink:#eaf0f6; --muted:#94a3b8;
  --primary:#2bdf83; --primary-ink:#17b469; --ring:rgba(43,223,131,.22); --line:#222a36;
  background: radial-gradient(1300px 700px at 70% -120px, rgba(43,223,131,.14), transparent 60%), var(--bg);
}

/* ====== HERO ====== */
.hero{
  display:grid; 
  grid-template-columns:1.2fr 1fr; 
  gap:28px; 
  align-items:center; 
  padding:24px 22px 2px;
  min-height: 600px;
}
.hero-left h1{ font-size:40px; line-height:1.1; margin:0 0 10px; }
.hl{ color:var(--primary); text-shadow:0 0 24px rgba(25,196,109,.35); }
.lead{ color:var(--muted); margin:0 0 18px; max-width:68ch; }
.cta-row{ display:flex; gap:10px; align-items:center; flex-wrap:wrap; }

.btn{ height:40px; padding:0 14px; border-radius:12px; border:1px solid var(--line); background:var(--panel); color:var(--ink); font-weight:800; cursor:pointer; transition:.2s ease; }
.btn:hover{ transform: translateY(-1px); box-shadow:0 12px 28px rgba(0,0,0,.12); }
.btn.primary{ background:var(--primary); border-color:transparent; color:#fff; }
.btn.primary.big{ height:46px; padding:0 18px; }
.btn.ghost{ background:transparent; }
.btn.subtle{ background:transparent; border-color:var(--line); }
.chip{ border:1px solid var(--line); border-radius:999px; padding:6px 12px; color:var(--muted); font-weight:700; }

.error{ color:#ef4444; margin-top:8px; }

/* 3D CUBE */
.cube-wrap{ position:relative; width:clamp(260px,38vw,420px); aspect-ratio:1/1; margin:0 auto 0 0; perspective:900px; filter:drop-shadow(0 40px 80px rgba(0,0,0,.25)); }
.cube{ width:100%; height:100%; position:absolute; inset:0; transform-style:preserve-3d; animation: idle 8s ease-in-out infinite alternate; }
@keyframes idle{ 0%{transform: rotateX(-8deg) rotateY(20deg);} 100%{transform: rotateX(4deg) rotateY(-15deg);} }
.face{ position:absolute; inset:0; display:flex; align-items:center; justify-content:center; font-weight:900; letter-spacing:2px; color:#fff; text-shadow:0 2px 18px rgba(0,0,0,.4);
  border-radius:18px; background: linear-gradient(145deg, rgba(255,255,255,.09), rgba(255,255,255,.03)), linear-gradient(145deg, #2bdc83, #15a85a); box-shadow: inset 0 0 0 1px rgba(255,255,255,.12);}
.f1{ transform: translateZ(90px);} .f2{ transform: rotateY(90deg) translateZ(90px);} .f3{ transform: rotateY(180deg) translateZ(90px);}
.f4{ transform: rotateY(-90deg) translateZ(90px);} .f5{ transform: rotateX(90deg) translateZ(90px);} .f6{ transform: rotateX(-90deg) translateZ(90px);}
.halo{ position:absolute; inset:auto 0 -20px 0; margin:auto; height:26px; filter:blur(8px); background: radial-gradient(closest-side, rgba(25,196,109,.55), transparent 70%); }

/* ====== GRID ====== */
.cards{ width:100%; padding:22px; display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:18px; }
.card{ perspective:800px; }
.card-inner{ background: linear-gradient(180deg, rgba(255,255,255,.08), rgba(255,255,255,0)), var(--panel); border:1px solid var(--line);
  border-radius:16px; padding:16px; transform-style:preserve-3d; transition: transform .25s ease, box-shadow .25s ease; box-shadow:0 12px 30px rgba(0,0,0,.14); }
.card-top{ display:flex; align-items:center; justify-content:space-between; margin-bottom:8px; }
.badge{ display:inline-flex; align-items:center; height:24px; padding:0 10px; border-radius:999px; background: rgba(25,196,109,.15); color:#2bdf83; border:1px solid rgba(25,196,109,.25); font-weight:800; font-size:12px; letter-spacing:.3px; }
.dots span{ display:inline-block; width:6px; height:6px; border-radius:50%; background: var(--line); margin-left:4px; }
h3{ margin:6px 0; }
.muted{ color:var(--muted); }
.metrics{ display:grid; grid-template-columns:repeat(2,1fr); gap:10px; margin:12px 0; }
.metrics strong{ font-size:22px; }
.metrics span{ color:var(--muted); font-size:12px; }
.card-actions{ display:flex; gap:10px; }

/* ====== MODAL ====== */
.fade-enter-active,.fade-leave-active{ transition: opacity .18s ease, transform .18s ease; }
.fade-enter-from,.fade-leave-to{ opacity:0; transform: translateY(6px); }

.modal{ position:fixed; inset:0; background:rgba(0,0,0,.35); display:flex; align-items:center; justify-content:center; padding: 18px; z-index: 60; }
.modal-card{ perspective:900px; max-width:720px; width:min(720px, 94vw); }
.modal-inner{ background: linear-gradient(180deg, rgba(255,255,255,.08), rgba(255,255,255,0)), var(--panel); border:1px solid var(--line); border-radius:18px; padding:18px; }
.modal-title{ margin:0 0 8px; }

.row{ display:grid; gap:6px; margin-top:10px; }
label{ font-weight:800; font-size:12px; color:var(--muted); }
.input{ height:42px; border:1px solid var(--line); border-radius:12px; padding:0 12px; background:transparent; color:var(--ink); outline:none; }
.input.area{ height:auto; padding:10px 12px; resize:vertical; }
.input:focus{ border-color:var(--primary); box-shadow:0 0 0 4px var(--ring); }

@media (max-width: 980px){
  .hero{ grid-template-columns:1fr; }
  .cards{ grid-template-columns:1fr; }
}
</style>
