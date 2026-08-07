import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import api from '../services/api'
import type { User } from '../types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const isLoading = ref<boolean>(false)

  const isAdmin = computed(() => user.value?.is_admin ?? false)

  async function login(email: string, password: string) {
    isLoading.value = true
    try {
      const response = await api.post<User>('/api/auth/login', { email, password })
      user.value = response.data
    } finally {
      isLoading.value = false
    }
  }

  async function logout() {
    isLoading.value = true
    try {
      await api.post('/api/auth/logout')
      user.value = null
    } finally {
      isLoading.value = false
    }
  }

  async function fetchMe() {
    isLoading.value = true
    try {
      const response = await api.get<User>('/api/auth/me')
      user.value = response.data
    } catch (error) {
      user.value = null
    } finally {
      isLoading.value = false
    }
  }

  return {
    user,
    isLoading,
    isAdmin,
    login,
    logout,
    fetchMe
  }
})
