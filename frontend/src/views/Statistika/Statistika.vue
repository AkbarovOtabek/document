<script>
import axios from "axios"
import { API_BASE_URL } from "@/API"

import {
  Chart,
  BarController,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from "chart.js"

Chart.register(BarController, BarElement, CategoryScale, LinearScale, Tooltip, Legend)

export default {
  name: "Statistika",

  data() {
    return {
      loading: false,

      lettersByMonth: [],
      employeesCount: null,
      orgReplies: [],

      chartInstance: null,
      monthLabels: ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"],
    }
  },

  async mounted() {
    await this.loadAll()
  },

  computed: {
    // всего писем за год
    totalLettersYear() {
      if (!this.lettersByMonth || !this.lettersByMonth.length) return 0
      return this.lettersByMonth.reduce(
        (sum, m) => sum + (m.count || 0),
        0
      )
    },

    // агрегированная статистика по ответам организаций
    repliesSummary() {
      if (!this.orgReplies || !this.orgReplies.length) {
        return null
      }

      return this.orgReplies.reduce(
        (acc, o) => {
          acc.totalRequired += o.total_required || 0
          acc.onTime += o.on_time || 0
          acc.late += o.late || 0
          acc.noReply += o.no_reply || 0
          return acc
        },
        { totalRequired: 0, onTime: 0, late: 0, noReply: 0 }
      )
    },

    // общий процент ответов вовремя
    overallOnTimeRatio() {
      const s = this.repliesSummary
      if (!s || !s.totalRequired) return null
      return s.onTime / s.totalRequired
    },

    currentYear() {
      return new Date().getFullYear()
    },
  },

  methods: {
    async loadAll() {
      this.loading = true
      await Promise.all([
        this.loadLettersByMonth(),
        this.loadEmployeesCount(),
        this.loadOrgReplies(),
      ])
      this.renderChart()
      this.loading = false
    },

  async loadLettersByMonth() {
  try {
    const year = new Date().getFullYear()

    const { data } = await axios.get(
      `${API_BASE_URL}api/statistics/cert/letters-by-month/`,
      { params: { year } }
    )

    const raw = data.results || data || []
    console.log("letters-by-month raw =", raw)

    // ожидаем с бэка что-то типа [{month: 1, count: 2}, ...]
    const map = {}
    raw.forEach(item => {
      const m = Number(item.month)
      if (!Number.isNaN(m)) {
        map[m] = item.count || 0
      }
    })

    // нормализуем: всегда 12 месяцев
    this.lettersByMonth = Array.from({ length: 12 }, (_, idx) => {
      const monthNumber = idx + 1
      return {
        month: this.monthLabels[idx],
        count: map[monthNumber] || 0,
      }
    })

    console.log("lettersByMonth normalized =", this.lettersByMonth)
  } catch (e) {
    console.error("Ошибка загрузки писем по месяцам", e)
    this.lettersByMonth = []
  }
},


    async loadEmployeesCount() {
      try {
        const { data } = await axios.get(
          `${API_BASE_URL}api/statistics/cert/employees-count/`
        )

        this.employeesCount = data.total_employees ?? data.count ?? null
      } catch (e) {
        console.error("Ошибка загрузки сотрудников", e)
      }
    },

    async loadOrgReplies() {
      try {
        const year = new Date().getFullYear()

        const { data } = await axios.get(
          `${API_BASE_URL}api/statistics/cert/org-replies/`,
          {
            params: {
              date_from: `${year}-01-01`,
              date_to: `${year}-12-31`,
            },
          }
        )

        this.orgReplies = data.results || data || []
      } catch (e) {
        console.error("Ошибка загрузки ответов организаций", e)
      }
    },

    renderChart() {
  if (!this.$refs.chart) return;

  if (this.chartInstance) {
    this.chartInstance.destroy();
  }

  const labels = this.lettersByMonth.map(m => m.month);
  const values = this.lettersByMonth.map(m => m.count);

  const ctx = this.$refs.chart.getContext("2d");

  this.chartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Письма за месяц",
          data: values,
          borderRadius: 8,
          backgroundColor: "rgba(0, 140, 255, 0.9)",  // ЯРКИЙ цвет
          borderColor: "rgba(0, 180, 255, 1)",
          borderWidth: 2,
          hoverBackgroundColor: "rgba(0, 180, 255, 1)",
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: {
            color: "#ffffff",   // ← БЕЛЫЙ текст легенды
            font: { size: 12 }
          }
        },
        tooltip: {
          titleColor: "#fff",
          bodyColor: "#fff",
          backgroundColor: "rgba(0,0,0,0.7)",
        },
      },
      scales: {
        x: {
          ticks: {
            color: "#bcdcff",    // ← светлый голубой
            font: { size: 12 },
          },
          grid: { display: false }
        },
        y: {
          ticks: {
            color: "#bcdcff",
            font: { size: 12 },
          },
          grid: {
            color: "rgba(255,255,255,0.08)" // светлая сетка
          }
        },
      }
    }
  });
}

  },
}
</script>

<template>
  <div class="stat-page">
    <div class="stat-header">
      <div class="stat-title-block">
        <h1>Statistika CERT-CBU</h1>
        <p>Обзор писем, сотрудников и активности организаций за {{ currentYear }} год</p>
      </div>
      <div class="year-pill">
        {{ currentYear }}
      </div>
    </div>

    <div v-if="loading" class="loader-panel">
      <div class="loader-dot" />
      <span>Загрузка статистики…</span>
    </div>

    <div v-else class="stat-grid">
      <!-- Верхние метрики -->
      <section class="top-metrics">
        <div class="metric-card">
          <div class="metric-label">Писем за год</div>
          <div class="metric-value">
            {{ totalLettersYear }}
          </div>
          <div class="metric-sub">Все письма CERT-CBU за {{ currentYear }} год</div>
        </div>

        <div class="metric-card">
          <div class="metric-label">Сотрудников CERT-CBU</div>
          <div class="metric-value">
            {{ employeesCount !== null ? employeesCount : "—" }}
          </div>
          <div class="metric-sub">От директора до делопроизводителя</div>
        </div>

        <div class="metric-card">
          <div class="metric-label">Ответы вовремя</div>
          <div class="metric-value">
            {{
              overallOnTimeRatio !== null
                ? (overallOnTimeRatio * 100).toFixed(1) + "%"
                : "—"
            }}
          </div>
          <div class="metric-sub">
            Доля писем, на которые организации ответили в срок
          </div>
        </div>
      </section>

      <!-- Ряд с графиком и короткой сводкой -->
      <section class="middle-row">
        <div class="chart-card">
          <div class="card-head">
            <div>
              <div class="card-title">Динамика писем по месяцам</div>
              <div class="card-sub">Количество исходящих писем CERT-CBU</div>
            </div>
            <div class="pill small-pill">
              {{ totalLettersYear }} писем
            </div>
          </div>

          <div class="chart-wrapper">
            <canvas ref="chart"></canvas>
          </div>
        </div>

        <div class="summary-card">
          <div class="card-head">
            <div class="card-title">Сводка по ответам организаций</div>
            <div class="card-sub">Только письма, где ответы требуются</div>
          </div>

          <div v-if="repliesSummary" class="summary-stats">
            <div class="summary-row">
              <span>Всего писем с обязательным ответом</span>
              <span>{{ repliesSummary.totalRequired }}</span>
            </div>
            <div class="summary-row green">
              <span>Ответы вовремя</span>
              <span>{{ repliesSummary.onTime }}</span>
            </div>
            <div class="summary-row yellow">
              <span>С опозданием</span>
              <span>{{ repliesSummary.late }}</span>
            </div>
            <div class="summary-row grey">
              <span>Нет ответа</span>
              <span>{{ repliesSummary.noReply }}</span>
            </div>
          </div>

          <div v-else class="summary-empty">
            Статистика по ответам организаций пока отсутствует.
          </div>
        </div>
      </section>

      <!-- Таблица организаций -->
      <section class="table-card">
        <div class="card-head">
          <div class="card-title">Активность организаций</div>
          <div class="card-sub">
            Как часто организации отвечают вовремя на письма CERT-CBU
          </div>
        </div>

        <div v-if="orgReplies && orgReplies.length" class="table-wrapper">
          <table class="org-table">
            <thead>
              <tr>
                <th>Организация</th>
                <th>Всего</th>
                <th>В срок</th>
                <th>С опозданием</th>
                <th>Нет ответа</th>
                <th>% вовремя</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="org in orgReplies" :key="org.organization_id">
                <td class="org-name-cell">
                  {{ org.organization_name || ("Организация #" + org.organization_id) }}
                </td>
                <td>{{ org.total_required }}</td>
                <td class="green">{{ org.on_time }}</td>
                <td class="red">{{ org.late }}</td>
                <td class="grey">{{ org.no_reply }}</td>
                <td>
                  {{
                    org.on_time_ratio !== undefined && org.on_time_ratio !== null
                      ? (org.on_time_ratio * 100).toFixed(1) + "%"
                      : "—"
                  }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else class="summary-empty">
          Нет данных по организациям за выбранный период.
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.stat-page {
  padding: 20px 24px;
  min-height: 100%;
  background: radial-gradient(circle at top left, #1e293b 0, #020617 55%, #000 100%);
  color: #e5e7eb;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

/* header */
.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.stat-title-block h1 {
  font-size: 26px;
  font-weight: 700;
  margin: 0 0 4px;
  color: #f9fafb;
}

.stat-title-block p {
  margin: 0;
  font-size: 13px;
  color: #9ca3af;
}

.year-pill {
  padding: 6px 14px;
  border-radius: 999px;
  background: linear-gradient(135deg, #4f46e5, #6366f1);
  font-size: 13px;
  font-weight: 600;
  box-shadow: 0 10px 30px rgba(79, 70, 229, 0.55);
}

/* loader */
.loader-panel {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(148, 163, 184, 0.35);
  font-size: 13px;
}

.loader-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #22c55e;
  box-shadow: 0 0 12px #22c55e;
}

/* layout grid */
.stat-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* top metrics */
.top-metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.metric-card {
  padding: 14px 16px;
  border-radius: 18px;
  background: radial-gradient(circle at top left, #0f172a, #020617);
  border: 1px solid rgba(148, 163, 184, 0.35);
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.7);
}

.metric-label {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  color: #9ca3af;
}

.metric-value {
  margin-top: 8px;
  font-size: 30px;
  font-weight: 700;
  color: #f9fafb;
}

.metric-sub {
  margin-top: 4px;
  font-size: 12px;
  color: #9ca3af;
}

/* middle row */
.middle-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
}

/* cards */
.chart-card,
.summary-card,
.table-card {
  padding: 16px 18px;
  border-radius: 20px;
  background: radial-gradient(circle at top left, #020617, #020617 40%, #0b1220);
  border: 1px solid rgba(148, 163, 184, 0.35);
  box-shadow: 0 16px 40px rgba(15, 23, 42, 0.8);
}

.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #e5e7eb;
}

.card-sub {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 2px;
}

.pill,
.small-pill {
  border-radius: 999px;
  padding: 5px 12px;
  font-size: 12px;
  background: rgba(15, 23, 42, 0.9);
  border: 1px solid rgba(96, 165, 250, 0.7);
  color: #bfdbfe;
}

/* chart */
.chart-wrapper {
  margin-top: 6px;
  height: 220px;
}

/* summary card */
.summary-stats {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.summary-row span:last-child {
  font-weight: 600;
}

.summary-row.green {
  color: #bbf7d0;
}
.summary-row.yellow {
  color: #facc15;
}
.summary-row.grey {
  color: #9ca3af;
}

.summary-empty {
  margin-top: 10px;
  font-size: 13px;
  color: #9ca3af;
}

/* table */
.table-wrapper {
  margin-top: 6px;
  border-radius: 14px;
  border: 1px solid rgba(31, 41, 55, 0.9);
  overflow: hidden;
  background: rgba(15, 23, 42, 0.85);
}

.org-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.org-table thead {
  background: rgba(15, 23, 42, 0.95);
}

.org-table th,
.org-table td {
  padding: 8px 10px;
  border-bottom: 1px solid rgba(31, 41, 55, 0.9);
}

.org-table th {
  text-align: left;
  font-weight: 500;
  color: #9ca3af;
}

.org-table tbody tr:hover {
  background: rgba(30, 64, 175, 0.35);
}

.org-name-cell {
  font-weight: 500;
  color: #e5e7eb;
}

.green {
  color: #4ade80;
  font-weight: 600;
}
.red {
  color: #f97373;
  font-weight: 600;
}
.grey {
  color: #9ca3af;
  font-weight: 600;
}

/* responsive */
@media (max-width: 1024px) {
  .top-metrics {
    grid-template-columns: 1fr;
  }

  .middle-row {
    grid-template-columns: 1fr;
  }
}
.chart-wrapper {
  margin-top: 6px;
  height: 220px;
  position: relative;
}

.chart-canvas {
  width: 100% !important;
  height: 100% !important;
  display: block;
}
</style>
