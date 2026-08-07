<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}
</script>

<template>
  <nav class="navbar" v-if="authStore.user">
    <div class="nav-links">
      <router-link to="/" class="nav-link">Hardware List</router-link>
      <router-link to="/rentals" class="nav-link">My Rentals</router-link>
      <router-link v-if="authStore.isAdmin" to="/admin" class="nav-link admin-link">Admin Panel</router-link>
    </div>
    <div class="nav-actions">
      <span class="user-email">{{ authStore.user.email }}</span>
      <button @click="handleLogout" class="logout-btn">Logout</button>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: rgba(25, 25, 25, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  position: sticky;
  top: 0;
  z-index: 100;
}
.nav-links {
  display: flex;
  gap: 1.5rem;
}
.nav-link {
  color: #b0b0b0;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease, transform 0.2s ease;
}
.nav-link:hover, .nav-link.router-link-active {
  color: #fff;
  transform: translateY(-1px);
}
.admin-link {
  color: #ff9e3b;
}
.admin-link:hover, .admin-link.router-link-active {
  color: #ffb86c;
}
.nav-actions {
  display: flex;
  align-items: center;
  gap: 1.2rem;
}
.user-email {
  font-size: 0.9rem;
  color: #a0a0a0;
  font-weight: 500;
}
.logout-btn {
  background-color: transparent;
  color: #ff5555;
  border: 1px solid rgba(255, 85, 85, 0.5);
  padding: 0.4rem 1.2rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
}
.logout-btn:hover {
  background-color: #ff5555;
  color: white;
  border-color: #ff5555;
  box-shadow: 0 4px 12px rgba(255, 85, 85, 0.3);
}
</style>
