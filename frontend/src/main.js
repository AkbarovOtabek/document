import './assets/main.css'
import axios from "axios";

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'


axios.interceptors.request.use((config) => {
  const token = localStorage.getItem("access");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

const app = createApp(App)

app.use(router)

app.mount('#app')

