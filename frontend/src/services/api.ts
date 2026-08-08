import axios from 'axios'
import router from '../router'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
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

    // If the error is 401 Unauthorized and we haven't already retried this request
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

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
        // Attempt to refresh the token
        await axios.post(
          `${import.meta.env.VITE_API_BASE_URL}/api/auth/refresh`,
          {},
          { withCredentials: true }
        )
        
        isRefreshing = false
        notifySubscribers(true)
        
        // Retry the original request
        return api(originalRequest)
      } catch (refreshError) {
        isRefreshing = false
        notifySubscribers(false)
        
        // If refresh fails, clear local user state and redirect to login
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
