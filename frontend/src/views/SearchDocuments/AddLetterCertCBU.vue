<script>
export default {
  name: 'AddLetterCertCBU',
  data(){
    return{
      form:{
        system: 'CERT-CBU',  // фиксировано
        number: '',
        date: '',
        subject: '',         // тема письма / инцидента
        incident_type: '',   // тип инцидента (фишинг, малварь, DDoS, утечка…)
        severity: 'medium',  // low | medium | high | critical
        status: 'new',       // new | in_progress | resolved | rejected
        performer: '',
        affected: '',        // затронутые системы/подразделения
        deadline: '',        // дедлайн реакции/отчета
        indicators: '',      // IOC/ссылки/хэши
        description: '',
        files: [],
      },
      uploading:false
    }
  },
  methods:{
    onFiles(e){ this.form.files = Array.from(e.target.files || []) },
    async submit(){
      this.uploading = true
      try{
        // const fd = new FormData()
        // Object.entries(this.form).forEach(([k,v]) => k==='files'
        //   ? v.forEach(f=>fd.append('files',f)) : fd.append(k,v))
        // await axios.post('/api/docs/create/cert-cbu', fd)
        await new Promise(r=>setTimeout(r,700))
        alert('Письмо CERT-CBU добавлено (демо)')
        this.form = {
          system:'CERT-CBU', number:'', date:'', subject:'', incident_type:'',
          severity:'medium', status:'new', performer:'', affected:'',
          deadline:'', indicators:'', description:'', files:[]
        }
      }finally{ this.uploading=false }
    }
  }
}
</script>

<template>
  <form class="form" @submit.prevent="submit">
    <div class="grid">
      <div class="col">
        <label>Система</label>
        <input type="text" value="CERT-CBU" disabled />
      </div>
      <div class="col">
        <label>Номер</label>
        <input v-model.trim="form.number" type="text" required />
      </div>
      <div class="col">
        <label>Дата</label>
        <input v-model="form.date" type="date" required />
      </div>
    </div>

    <div class="row">
      <label>Тема</label>
      <input v-model.trim="form.subject" type="text" required />
    </div>

    <div class="grid">
      <div class="col">
        <label>Тип инцидента</label>
        <input v-model.trim="form.incident_type" type="text" placeholder="Фишинг / ВПО / DDoS / Утечка ..." />
      </div>
      <div class="col">
        <label>Критичность</label>
        <select v-model="form.severity">
          <option value="low">Низкая</option>
          <option value="medium">Средняя</option>
          <option value="high">Высокая</option>
          <option value="critical">Критическая</option>
        </select>
      </div>
      <div class="col">
        <label>Статус</label>
        <select v-model="form.status">
          <option value="new">Новый</option>
          <option value="in_progress">В работе</option>
          <option value="resolved">Закрыт</option>
          <option value="rejected">Отклонён</option>
        </select>
      </div>
    </div>

    <div class="grid">
      <div class="col">
        <label>Исполнитель</label>
        <input v-model.trim="form.performer" type="text" />
      </div>
      <div class="col">
        <label>Затронутые системы/подразделения</label>
        <input v-model.trim="form.affected" type="text" />
      </div>
      <div class="col">
        <label>Дедлайн</label>
        <input v-model="form.deadline" type="date" />
      </div>
    </div>

    <div class="row">
      <label>Индикаторы компрометации (IOC)</label>
      <textarea v-model.trim="form.indicators" rows="3" placeholder="URL, IP, домены, хеши…"/>
    </div>

    <div class="row">
      <label>Описание / Требуемые действия</label>
      <textarea v-model.trim="form.description" rows="5" />
    </div>

    <div class="row">
      <label>Файлы</label>
      <input type="file" multiple @change="onFiles" />
      <div class="files" v-if="form.files.length">
        <span v-for="(f,i) in form.files" :key="i" class="chip">{{ f.name }}</span>
      </div>
    </div>

    <div class="actions">
      <button type="submit" class="btn primary" :disabled="uploading">
        {{ uploading ? 'Сохранение…' : 'Сохранить' }}
      </button>
    </div>
  </form>
</template>

<style scoped>
.form{ display:flex; flex-direction:column; gap:12px; }
.grid{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px; }
.row,.col{ display:flex; flex-direction:column; gap:6px; }
label{ font-size:12px; opacity:.7; }
input,select,textarea{ border:1px solid #e5e7eb; border-radius:10px; padding:8px 10px; min-height:36px; }
textarea{ resize:vertical; }
.files{ display:flex; gap:6px; flex-wrap:wrap; margin-top:6px; }
.chip{ background:#fff7ed; border:1px solid #fdba74; color:#9a3412; border-radius:9999px; padding:4px 8px; font-size:12px; }
.actions{ display:flex; justify-content:flex-end; }
.btn{ padding:8px 14px; border-radius:10px; border:1px solid transparent; cursor:pointer; font-weight:700; }
.btn.primary{ background:#2563eb; color:#fff; }
</style>
