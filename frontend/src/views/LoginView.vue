<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'

const router = useRouter()
const authStore = useAuthStore()
const toastStore = useToastStore()

const email = ref('')
const password = ref('')
const isSubmitting = ref(false)

onMounted(() => {
  if (authStore.user) {
    router.push('/')
  }
})

async function handleLogin() {
  if (!email.value || !password.value) {
    toastStore.add('Please enter both email and password', 'error')
    return
  }
  
  isSubmitting.value = true
  try {
    await authStore.login(email.value, password.value)
    toastStore.add('Login successful', 'success')
    router.push('/')
  } catch (error: any) {
    toastStore.add(
      error.response?.data?.detail || 'Login failed. Please check your credentials.', 
      'error'
    )
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="login-container">
    <div class="login-card">
      <div class="logo-wrapper">
        <svg class="logo-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
          <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
          <line x1="12" y1="22.08" x2="12" y2="12"></line>
        </svg>
      </div>

      <div class="header-text">
        <h1 class="title">Welcome back</h1>
        <p class="subtitle">Sign in to your account</p>
      </div>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="email">Email (company domain only)</label>
          <input 
            id="email"
            type="email" 
            v-model="email" 
            placeholder="name@booksy.com"
            :disabled="isSubmitting"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="password">Password</label>
          <input 
            id="password"
            type="password" 
            v-model="password" 
            placeholder="Enter your password"
            :disabled="isSubmitting"
            required
          />
        </div>
        
        <button type="submit" class="submit-btn" :disabled="isSubmitting">
          {{ isSubmitting ? 'Signing in...' : 'Login' }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
}

.login-card {
  background-color: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 2rem 2.5rem 2.5rem;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.logo-wrapper {
  background-color: #e5e7eb;
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 2rem;
}

.logo-icon {
  width: 24px;
  height: 24px;
  color: #111827;
}

.header-text {
  text-align: center;
  margin-bottom: 2rem;
}

.title {
  font-size: 1.15rem;
  font-weight: 700;
  color: #111827;
  margin: 0 0 0.25rem 0;
}

.subtitle {
  color: #6b7280;
  font-size: 0.9rem;
  margin: 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

label {
  font-size: 0.8rem;
  font-weight: 700;
  color: #111827;
}

input {
  background-color: #f3f4f6;
  border: none;
  color: #111827;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  font-size: 0.9rem;
  transition: all 0.2s ease;
  font-family: inherit;
}

input::placeholder {
  color: #9ca3af;
}

input:focus {
  outline: none;
  background-color: #e5e7eb;
}

input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.submit-btn {
  margin-top: 0.5rem;
  background-color: #0f172a;
  color: #ffffff;
  border: none;
  padding: 0.75rem;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.submit-btn:hover:not(:disabled) {
  background-color: #1e293b;
}

.submit-btn:disabled {
  background-color: #475569;
  cursor: not-allowed;
  opacity: 0.8;
}
</style>
