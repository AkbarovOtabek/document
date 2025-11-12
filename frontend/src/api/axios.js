import axios from "axios";

export const API_BASE_URL = "http://127.0.0.1:8000/";

const api = axios.create({
  baseURL: API_BASE_URL,
  // credentials НЕ нужны при JWT
  withCredentials: false,
});

// Достаём токен из localStorage и ставим в Authorization
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Обновление access при 401 (если есть refresh)
let isRefreshing = false;
let pending = [];

function onRefreshed(newAccess) {
  pending.forEach(cb => cb(newAccess));
  pending = [];
}

api.interceptors.response.use(
  (r) => r,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      const refresh = localStorage.getItem("refresh");
      if (!refresh) return Promise.reject(error);

      original._retry = true;

      if (isRefreshing) {
        // очередь запросов, пока рефрешимся
        return new Promise((resolve) => {
          pending.push((newAccess) => {
            original.headers.Authorization = `Bearer ${newAccess}`;
            resolve(api(original));
          });
        });
      }

      isRefreshing = true;
      try {
        const { data } = await axios.post(`${API_BASE_URL}api/token/refresh/`, { refresh });
        const newAccess = data.access;
        localStorage.setItem("access", newAccess);
        isRefreshing = false;
        onRefreshed(newAccess);

        original.headers.Authorization = `Bearer ${newAccess}`;
        return api(original);
      } catch (e) {
        isRefreshing = false;
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        return Promise.reject(e);
      }
    }
    return Promise.reject(error);
  }
);

export default api;
