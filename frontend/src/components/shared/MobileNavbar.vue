<template>
  <div class="mobile-navbar-container">
    <nav class="mobile-navbar" v-if="authStore.user">
      <div class="logo-icon-wrapper">
        <svg class="logo-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
          <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
          <line x1="12" y1="22.08" x2="12" y2="12"></line>
        </svg>
        <span class="logo-text">Hardware</span>
      </div>

      <div class="hamburger" :class="{ open: isOpen }" @click="toggleMenu">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </nav>

    <!-- Overlay menu -->
    <div 
      class="mobile-menu-overlay" 
      :class="{ open: isOpen }"
      @click.self="toggleMenu"
    >
      <div class="mobile-menu-content">
        <router-link to="/" class="nav-link" @click="isOpen = false">
          Hardware List
        </router-link>
        
        <router-link to="/rentals" class="nav-link" @click="isOpen = false">
          My Rentals
        </router-link>
        
        <router-link v-if="authStore.isAdmin" to="/admin" class="nav-link" @click="isOpen = false">
          Admin Panel
        </router-link>

        <div class="menu-divider"></div>

        <button @click="handleLogout" class="logout-btn">
          Logout
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const isOpen = ref(false)

function toggleMenu() {
  isOpen.value = !isOpen.value
}

async function handleLogout() {
  isOpen.value = false
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.mobile-navbar-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 56px;
  z-index: 1000;
}

.mobile-navbar {
  height: 100%;
  width: 100%;
  background-color: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  position: relative;
  z-index: 1001; /* Above the overlay */
}

.logo-icon-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.logo-icon {
  width: 24px;
  height: 24px;
  color: #111827;
}

.logo-text {
  font-weight: 700;
  font-size: 1rem;
  color: #111827;
}

.hamburger {
  display: flex;
  flex-direction: column;
  gap: 5px;
  cursor: pointer;
  padding: 8px;
}

.hamburger span {
  display: block;
  width: 24px;
  height: 2px;
  background: #111827;
  transition: transform 0.2s, opacity 0.2s;
}

/* When open, animate to X */
.hamburger.open span:nth-child(1) {
  transform: translateY(7px) rotate(45deg);
}
.hamburger.open span:nth-child(2) {
  opacity: 0;
}
.hamburger.open span:nth-child(3) {
  transform: translateY(-7px) rotate(-45deg);
}

.mobile-menu-overlay {
  position: fixed;
  top: 56px;
  left: 0;
  width: 100%;
  height: calc(100vh - 56px);
  background-color: rgba(0, 0, 0, 0.5); /* Dimmed background */
  z-index: 1000;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s ease;
}

.mobile-menu-overlay.open {
  opacity: 1;
  pointer-events: auto;
}

.mobile-menu-content {
  width: 100%;
  background-color: #ffffff;
  display: flex;
  flex-direction: column;
  padding: 8px 0;
  transform: translateY(-100%);
  transition: transform 0.3s ease;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.mobile-menu-overlay.open .mobile-menu-content {
  transform: translateY(0);
}

.nav-link {
  display: flex;
  align-items: center;
  min-height: 56px;
  padding: 0 24px;
  color: #111827;
  text-decoration: none;
  font-weight: 600;
  font-size: 1.1rem;
  transition: background-color 0.2s;
}

.nav-link:active {
  background-color: #f3f4f6;
}

.menu-divider {
  height: 1px;
  background-color: #e5e7eb;
  margin: 8px 0;
}

.logout-btn {
  display: flex;
  align-items: center;
  min-height: 56px;
  padding: 0 24px;
  color: #ef4444;
  background: none;
  border: none;
  font-weight: 600;
  font-size: 1.1rem;
  width: 100%;
  text-align: left;
  cursor: pointer;
}

.logout-btn:active {
  background-color: #fef2f2;
}
</style>
