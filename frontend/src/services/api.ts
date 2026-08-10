import axios from 'axios'
import router from '../router'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  // withCredentials required for HttpOnly cookies on cross-origin requests
  withCredentials: true
})

let isRefreshing = false
let refreshSubscribers: ((success: boolean) => void)[] = []

function subscribeToRefresh(callback: (success: boolean) => void) {
  refreshSubscribers.push(callback)
}

function notifySubscribers(success: boolean) {
  refreshSubscribers.forEach(cb => cb(success))
  refreshSubscribers = []
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      // Concurrency lock — only one refresh fires regardless of concurrent 401s
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          subscribeToRefresh((success) => {
            if (success) {
              resolve(api(originalRequest))
            } else {
              reject(error)
            }
          })
        })
      }

      isRefreshing = true
      try {
        await axios.post(
          `${import.meta.env.VITE_API_BASE_URL}/api/auth/refresh`,
          {},
          { withCredentials: true }
        )
        
        isRefreshing = false
        notifySubscribers(true)
        return api(originalRequest)
      } catch (refreshError) {
        isRefreshing = false
        notifySubscribers(false)
        
        const { useAuthStore } = await import('../stores/auth')
        const authStore = useAuthStore()
        authStore.user = null
        router.push('/login')
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

export default api
