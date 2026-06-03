import axios from "axios"

const api = axios.create({
  baseURL: "http://127.0.0.1:8080/api",
  headers: { "Content-Type": "application/json" },
})

// Ҳар requestга token
api.interceptors.request.use(config => {
  // zustand persist "qline-auth" da saqlaydi
  const auth = JSON.parse(localStorage.getItem("qline-auth") || "{}")
  const token = auth?.state?.token || localStorage.getItem("access_token")
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})


// 401 → token refresh
api.interceptors.response.use(
  res => res,
  async err => {
    const orig = err.config
    if (err.response?.status === 401 && !orig._retry) {
      orig._retry = true
      try {
        const auth = JSON.parse(localStorage.getItem("qline-auth") || "{}")
        const refresh = auth?.state?.token
          ? localStorage.getItem("refresh_token")
          : localStorage.getItem("refresh_token")
        const { data } = await axios.post(
          "http://127.0.0.1:8080/api/auth/token/refresh/",
          { refresh }
        )
        localStorage.setItem("access_token", data.access)
        orig.headers.Authorization = `Bearer ${data.access}`
        return api(orig)
      } catch {
        localStorage.clear()
        window.location.href = "/login"
      }
    }
    return Promise.reject(err)
  }
)
export default api