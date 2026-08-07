import axios from 'axios'
import router from '../router'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  withCredentials: true
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // If the error is 401 Unauthorized and we haven't already retried this request
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        // Attempt to refresh the token
        // Use a new axios instance or generic axios to avoid interceptor loops
        await axios.post(
          `${import.meta.env.VITE_API_BASE_URL}/api/auth/refresh`,
          {},
          { withCredentials: true }
        )
        
        // If refresh succeeds, retry the original request
        return api(originalRequest)
      } catch (refreshError) {
        // If refresh fails, clear local user state and redirect to login
        // TODO: clear Pinia auth store when it's created
        router.push('/login')
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

export default api
