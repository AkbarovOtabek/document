<template>
  <transition name="fade">
    <div class="modal" @click.self="$emit('close')">
      <transition name="zoom">
        <div class="card card--elevated" role="dialog" aria-modal="true">
          <header class="card__head">
            <div class="card__title-wrap">
              <span class="dot"></span>
              <h3 class="card__title">Добавить структуру</h3>
              <p class="card__subtitle">Создайте узел и при необходимости назначьте руководителя</p>
            </div>
            <button class="icon-btn" @click="$emit('close')" aria-label="Закрыть">
              <svg viewBox="0 0 24 24" width="18" height="18">
                <path
                  d="M6 6l12 12M18 6L6 18"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                />
              </svg>
            </button>
          </header>

          <section class="card__body">
            <div class="grid2">
              <!-- Тип -->
              <div class="field">
                <label class="label">Тип</label>
                <div class="control">
                  <select v-model="form.type" class="input input--select">
                    <option value="center">Центр</option>
                    <option value="management">Управление</option>
                    <option value="department">Отдел</option>
                  </select>
                </div>
              </div>

              <!-- Центр / Управление -->
              <div class="field" v-if="form.type === 'management'">
                <label class="label">Центр</label>
                <div class="control">
                  <select v-model.number="form.center" class="input input--select">
                    <option :value="c.id" v-for="c in centers" :key="c.id">{{ c.name }}</option>
                  </select>
                </div>
              </div>

              <div class="field" v-if="form.type === 'department'">
                <label class="label">Управление</label>
                <div class="control">
                  <select v-model.number="form.management" class="input input--select">
                    <option v-for="m in centersFlatManagements" :key="m.id" :value="m.id">
                      {{ m.name }} · {{ centerName(m.center) }}
                    </option>
                  </select>
                </div>
              </div>

              <!-- Название -->
              <div class="field field--full">
                <label class="label">Название</label>
                <input
                  v-model.trim="form.name"
                  class="input"
                  placeholder="Например: Управление ИБ"
                />
              </div>
            </div>

            <!-- РУКОВОДИТЕЛЬ -->
            <div class="divider"></div>

            <label class="switch">
              <input type="checkbox" v-model="form.addDirector" />
              <span class="switch__track"><span class="switch__thumb"></span></span>
              <span class="switch__label">Назначить руководителя</span>
            </label>

            <div v-if="form.addDirector" class="subsection">
              <div class="grid2">
                <div class="field">
                  <label class="label">Пользователь</label>
                  <div class="control">
                    <select v-model.number="form.dirUserId" class="input input--select">
                      <option :value="u.id" v-for="u in users" :key="u.id">
                        {{ userLabel(u) }}
                      </option>
                    </select>
                  </div>
                </div>

                <div class="field">
                  <label class="label">Должность</label>
                  <input :value="directorPositionHuman" class="input input--ghost" disabled />
                </div>
              </div>
              <p class="help">
                Пользователь получит назначение «{{ directorPositionHuman }}» и будет привязан к
                созданной структуре.
              </p>
            </div>
          </section>

          <footer class="card__foot">
            <button class="btn ghost" @click="$emit('close')">Отмена</button>
            <button class="btn primary" :disabled="saving" @click="save">
              <span v-if="saving" class="spinner"></span>
              {{ saving ? "Сохраняю…" : "Добавить" }}
            </button>
          </footer>
        </div>
      </transition>
    </div>
  </transition>
</template>

<script>
import axios from "axios";
import { API_BASE_URL } from "../../API";

export default {
  name: "AddStructureModal",
  props: {
    centers: { type: Array, default: () => [] },
    managements: { type: Array, default: () => [] },
  },
  emits: ["close", "saved"],
  data() {
    return {
      saving: false,
      users: [],
      form: {
        type: "management",
        center: null,
        management: null,
        name: "",
        addDirector: true,
        dirUserId: null,
      },
    };
  },
  computed: {
    centersFlatManagements() {
      return this.managements || [];
    },
    directorPosition() {
      return this.form.type === "center"
        ? "director"
        : this.form.type === "management"
        ? "deputy_director"
        : "head_of_department";
    },
    directorPositionHuman() {
      return this.form.type === "center"
        ? "Директор центра"
        : this.form.type === "management"
        ? "Начальник управления"
        : "Начальник отдела";
    },
  },
  mounted() {
    this.loadUsers();
    this._esc = (e) => e.key === "Escape" && this.$emit("close");
    window.addEventListener("keydown", this._esc);
  },
  beforeUnmount() {
    window.removeEventListener("keydown", this._esc);
  },
  methods: {
    async loadUsers() {
      try {
        const { data } = await axios.get(`${API_BASE_URL}api/staff/users/`, {
          params: { page_size: 500 },
        });
        this.users = Array.isArray(data?.results) ? data.results : Array.isArray(data) ? data : [];
      } catch (e) {
        console.warn("Не удалось загрузить пользователей:", e?.message);
      }
    },
    userLabel(u) {
      const fio = u.fio || u.full_name || u.username || u.email || `user#${u.id}`;
      return u.position ? `${fio} — ${u.position}` : fio;
    },
    centerName(id) {
      const c = this.centers.find((x) => x.id === (x.id?.id ?? id) || x.id === id);
      return c?.name || "—";
    },
    async save() {
      try {
        this.saving = true;

        let created = { center: null, management: null, department: null };

        if (this.form.type === "center") {
          const { data } = await axios.post(`${API_BASE_URL}api/staff/centers/`, {
            name: this.form.name,
          });
          created.center = data?.id;
        } else if (this.form.type === "management") {
          const centerId = this.form.center || this.centers[0]?.id;
          const { data } = await axios.post(`${API_BASE_URL}api/staff/management/`, {
            name: this.form.name,
            center: centerId,
          });
          created.center = centerId;
          created.management = data?.id;
        } else {
          if (!this.form.management) throw new Error("Укажите управление");
          const { data } = await axios.post(`${API_BASE_URL}api/staff/departments/`, {
            name: this.form.name,
            management: this.form.management,
          });
          created.department = data?.id;
        }

        if (this.form.addDirector) {
          if (!this.form.dirUserId) throw new Error("Выберите пользователя.");
          const payload = {
            position: this.directorPosition,
            center: created.center || undefined,
            management:
              this.form.type === "management"
                ? created.management
                : this.form.type === "department"
                ? this.form.management
                : undefined,
            department: this.form.type === "department" ? created.department : undefined,
          };
          await axios.patch(`${API_BASE_URL}api/staff/users/${this.form.dirUserId}/`, payload);
        }

        this.$emit("saved");
      } catch (e) {
        const msg = e?.response?.data?.detail || e?.message || "Неизвестная ошибка";
        alert("Ошибка: " + msg);
      } finally {
        this.saving = false;
      }
    },
  },
};
</script>
<style scoped>
/* Бэкдроп остаётся тёмным c блюром */
.modal {
  position: fixed;
  inset: 0;
  background: rgba(10, 12, 18, 0.55);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  display: grid;
  place-items: center;
  padding: 20px;
  z-index: 9999;
}

/* КАРТОЧКА — ярко-белая, полупрозрачность минимальная */
.card {
  width: 620px;
  max-width: 100%;
  background: rgba(255, 255, 255, 0.92) !important; /* белая */
  color: #0f141a !important;
  border: 1px solid rgba(255, 255, 255, 0.9) !important;
  border-radius: 20px;
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.28);
  overflow: hidden;
}

/* Шапка/подвал тоже белые */
.card__head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}
.card__foot {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
}
.card__head,
.card__foot {
  background: rgba(255, 255, 255, 0.96) !important;
  border-color: rgba(15, 20, 26, 0.06) !important;
  padding: 16px 20px;
}
.card__title {
  font-weight: 900;
  font-size: 18px;
  margin: 0;
}

/* Контент */
.card__body {
  padding: 18px 20px 10px;
  display: grid;
  gap: 14px;
}

/* Поля ввода — реально белые */
.input,
select {
  width: 100%;
  height: 38px;
  border-radius: 12px;
  border: 1px solid rgba(15, 20, 26, 0.12) !important;
  background: #ffffff !important; /* ← белый фон */
  color: #0f141a !important;
  padding: 0 12px;
  transition: box-shadow 0.15s ease, border-color 0.15s ease;
}
.input:focus,
select:focus {
  outline: none;
  border-color: #22c55e !important;
  box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.2);
}

/* Подсказки/лейблы */
.label {
  font-size: 12px;
  font-weight: 700;
  color: #5e6b7c;
}
.switch {
  display: flex;
  align-items: center;
  gap: 10px;
}
.switch input {
  accent-color: #22c55e;
}
.subsection {
  background: rgba(247, 249, 252, 0.9) !important; /* белёсый бокс */
  border: 1px dashed rgba(15, 20, 26, 0.12);
  border-radius: 12px;
  padding: 12px;
  display: grid;
  gap: 10px;
}

/* Кнопки */
.btn {
  height: 38px;
  padding: 0 16px;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
  border: 1px solid rgba(15, 20, 26, 0.12);
  background: #ffffff !important; /* белая */
  color: #0f141a;
  transition: transform 0.06s ease, box-shadow 0.2s ease, background 0.2s;
}
.btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 22px rgba(0, 0, 0, 0.08);
}
.btn.primary {
  background: #22c55e !important;
  border-color: #22c55e !important;
  color: #063a21 !important;
}
.btn.primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* Иконка закрытия */
.icon-btn {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  border: 1px solid rgba(15, 20, 26, 0.12);
  background: #ffffff !important;
  color: #0f141a;
  display: grid;
  place-items: center;
  font-size: 18px;
  line-height: 1;
}
.icon-btn:hover {
  box-shadow: 0 10px 22px rgba(0, 0, 0, 0.08);
}

/* Сетка */
.grid2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
@media (max-width: 600px) {
  .grid2 {
    grid-template-columns: 1fr;
  }
}
</style>
