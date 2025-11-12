<script>
export default {
  name: 'AddLetterOther',
  data(){
    return{
      form:{
        system: 'NQQ',          // NQQ | MBQ | OTHER
        number: '',
        name: '',
        date: '',
        performer: '',
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
        // await axios.post('/api/docs/create/other', fd)
        await new Promise(r=>setTimeout(r,500))
        alert('Письмо добавлено (Другие)')
        this.form = { system:'NQQ', number:'', name:'', date:'', performer:'', description:'', files:[] }
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
        <select v-model="form.system">
          <option value="NQQ">NQQ</option>
          <option value="MBQ">MBQ</option>
          <option value="OTHER">Другая</option>
        </select>
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
      <label>Имя / Тема</label>
      <input v-model.trim="form.name" type="text" required />
    </div>

    <div class="row">
      <label>Исполнитель</label>
      <input v-model.trim="form.performer" type="text" />
    </div>

    <div class="row">
      <label>Описание</label>
      <textarea v-model.trim="form.description" rows="4" />
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
.chip{ background:#eef2ff; border:1px solid #c7d2fe; color:#3730a3; border-radius:9999px; padding:4px 8px; font-size:12px; }
.actions{ display:flex; justify-content:flex-end; }
.btn{ padding:8px 14px; border-radius:10px; border:1px solid transparent; cursor:pointer; font-weight:700; }
.btn.primary{ background:#2563eb; color:#fff; }
</style>
