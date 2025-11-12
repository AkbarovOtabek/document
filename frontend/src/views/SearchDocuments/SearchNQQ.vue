<script>
export default {
  name: 'SearchNQQ',
  data(){
    return{
      form:{
        name:'', number:'', description:'',
        date_from:'', date_to:'', performer:''
      },
      results: [],
      loading:false,
    }
  },
  methods:{
    async onSearch(){
      this.loading = true
      try{
        // TODO: сюда добавим реальный запрос к API NQQ
        // пример: const { data } = await axios.get('/api/nqq/search', { params: this.form })
        // имитация:
        await new Promise(r=>setTimeout(r,400))
        this.results = [
          { id:1, number:'NQQ-001', name:'Письмо по ИБ', performer:'Иванов', date:'2025-05-05', description:'Текст…' },
        ]
      }finally{
        this.loading = false
      }
    },
    onReset(){
      this.form = { name:'', number:'', description:'', date_from:'', date_to:'', performer:'' }
      this.results = []
    }
  }
}
</script>

<template>
  <div class="wrap">
    <h3>NQQ</h3>

    <div class="filters">
      <div class="row">
        <div class="col">
          <label>Имя</label>
          <input v-model.trim="form.name" type="text" placeholder="Название/тема" />
        </div>
        <div class="col">
          <label>Номер</label>
          <input v-model.trim="form.number" type="text" placeholder="№ письма" />
        </div>
        <div class="col">
          <label>Исполнитель</label>
          <input v-model.trim="form.performer" type="text" placeholder="ФИО" />
        </div>
      </div>

      <div class="row">
        <div class="col">
          <label>Описание</label>
          <input v-model.trim="form.description" type="text" placeholder="Ключевые слова" />
        </div>
        <div class="col">
          <label>От даты</label>
          <input v-model="form.date_from" type="date" />
        </div>
        <div class="col">
          <label>До даты</label>
          <input v-model="form.date_to" type="date" />
        </div>
      </div>

      <div class="actions">
        <button class="btn ghost" @click="onReset">Сброс</button>
        <button class="btn primary" :disabled="loading" @click="onSearch">
          {{ loading ? 'Поиск…' : 'Искать' }}
        </button>
      </div>
    </div>

    <div class="results" v-if="results.length">
      <table>
        <thead>
          <tr>
            <th>Номер</th>
            <th>Имя</th>
            <th>Исполнитель</th>
            <th>Дата</th>
            <th>Описание</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in results" :key="r.id">
            <td>{{ r.number }}</td>
            <td>{{ r.name }}</td>
            <td>{{ r.performer }}</td>
            <td>{{ r.date }}</td>
            <td>{{ r.description }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="empty" v-else>Ничего не найдено</div>
  </div>
</template>

<style scoped>
h3{ margin:4px 0 10px; }
.filters{ display:flex; flex-direction:column; gap:10px; }
.row{ display:grid; grid-template-columns: 1fr 1fr 1fr; gap:10px; }
.col{ display:flex; flex-direction:column; gap:6px; }
label{ font-size:12px; opacity:.7; }
input{ height:36px; border:1px solid #e5e7eb; border-radius:10px; padding:6px 10px; }
.actions{ display:flex; justify-content:flex-end; gap:10px; }
.btn{ padding:8px 14px; border-radius:10px; border:1px solid transparent; cursor:pointer; font-weight:700; }
.btn.ghost{ background:#f3f4f6; }
.btn.primary{ background:#2563eb; color:#fff; }
.results{ margin-top:12px; overflow:auto; }
table{ width:100%; border-collapse:collapse; }
th, td{ padding:8px 10px; border-bottom:1px solid #eef2f7; font-size:14px; text-align:left; }
.empty{ margin-top:10px; font-size:13px; opacity:.6; }
</style>
