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
      <h1 class="title">Welcome Back</h1>
      <p class="subtitle">Please enter your details to sign in.</p>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="email">Email address</label>
          <input 
            id="email"
            type="email" 
            v-model="email" 
            placeholder="admin@example.com"
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
            placeholder="••••••••"
            :disabled="isSubmitting"
            required
          />
        </div>
        
        <button type="submit" class="submit-btn" :disabled="isSubmitting">
          {{ isSubmitting ? 'Signing in...' : 'Sign in' }}
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
  min-height: calc(100vh - 150px);
}

.login-card {
  background-color: rgba(30, 30, 30, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 3rem 2.5rem;
  width: 100%;
  max-width: 440px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
}

.title {
  font-size: 2rem;
  font-weight: 700;
  color: #fff;
  margin-bottom: 0.5rem;
  text-align: center;
  letter-spacing: -0.02em;
}

.subtitle {
  color: #a0a0a0;
  font-size: 0.95rem;
  text-align: center;
  margin-bottom: 2.5rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #d0d0d0;
}

input {
  background-color: rgba(18, 18, 18, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #fff;
  padding: 0.85rem 1rem;
  border-radius: 10px;
  font-size: 1rem;
  transition: all 0.2s ease;
  font-family: inherit;
}

input:focus {
  outline: none;
  border-color: #646cff;
  background-color: #1a1a1a;
  box-shadow: 0 0 0 3px rgba(100, 108, 255, 0.2);
}

input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.submit-btn {
  margin-top: 0.5rem;
  background: linear-gradient(135deg, #646cff 0%, #535bf2 100%);
  color: white;
  border: none;
  padding: 0.9rem;
  border-radius: 10px;
  font-size: 1.05rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(100, 108, 255, 0.3);
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(100, 108, 255, 0.4);
}

.submit-btn:active:not(:disabled) {
  transform: translateY(1px);
}

.submit-btn:disabled {
  background: #3a3a3a;
  box-shadow: none;
  cursor: not-allowed;
  opacity: 0.8;
}
</style>
