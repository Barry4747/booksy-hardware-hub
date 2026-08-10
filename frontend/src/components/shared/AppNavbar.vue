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
  <nav class="sidebar" v-if="authStore.user">
    <div class="sidebar-header">
      <div class="logo-icon-wrapper">
        <svg class="logo-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
          <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
          <line x1="12" y1="22.08" x2="12" y2="12"></line>
        </svg>
      </div>
      <span class="logo-text">Hardware Manager</span>
    </div>
    
    <div class="nav-links">
      <router-link to="/" class="nav-link">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="8" y1="6" x2="21" y2="6"></line>
          <line x1="8" y1="12" x2="21" y2="12"></line>
          <line x1="8" y1="18" x2="21" y2="18"></line>
          <line x1="3" y1="6" x2="3.01" y2="6"></line>
          <line x1="3" y1="12" x2="3.01" y2="12"></line>
          <line x1="3" y1="18" x2="3.01" y2="18"></line>
        </svg>
        Hardware List
      </router-link>
      <router-link to="/rentals" class="nav-link">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <polyline points="12 6 12 12 16 14"></polyline>
        </svg>
        My Rentals
      </router-link>
      <router-link v-if="authStore.isAdmin" to="/admin" class="nav-link">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="3"></circle>
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
        </svg>
        Admin Panel
      </router-link>
    </div>
    
    <div class="sidebar-footer">
      <button @click="handleLogout" class="logout-btn">
        <svg class="logout-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
          <polyline points="16 17 21 12 16 7"></polyline>
          <line x1="21" y1="12" x2="9" y2="12"></line>
        </svg>
        Logout
      </button>
    </div>
  </nav>
</template>

<style scoped>
.sidebar {
  width: 260px;
  background-color: #ffffff;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  padding: 1.5rem 1rem;
  height: 100vh;
  position: sticky;
  top: 0;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 1rem;
  margin-bottom: 2rem;
}

.logo-icon-wrapper {
  background-color: #f3f4f6;
  padding: 0.5rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-icon {
  width: 20px;
  height: 20px;
  color: #111827;
}

.logo-text {
  font-weight: 700;
  font-size: 1rem;
  color: #111827;
}

.nav-links {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 0.85rem;
  color: #6b7280;
  text-decoration: none;
  font-weight: 600;
  border-radius: 12px;
  transition: all 0.2s ease;
  font-size: 0.85rem;
}

.nav-icon {
  width: 18px;
  height: 18px;
}

.nav-link:hover {
  background-color: #f3f4f6;
  color: #111827;
}

.nav-link.router-link-active {
  background-color: #f3f4f6;
  color: #111827;
  font-weight: 600;
}

.sidebar-footer {
  margin-top: auto;
  border-top: 1px solid #e5e7eb;
  padding-top: 1rem;
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  background: none;
  border: none;
  padding: 0.75rem 1rem;
  color: #ef4444;
  font-weight: 600;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s;
  font-size: 0.95rem;
}

.logout-icon {
  width: 18px;
  height: 18px;
}

.logout-btn:hover {
  background-color: #fef2f2;
}

@media (max-width: 768px) {
  .sidebar {
    width: 100%;
    height: auto;
    flex-direction: row;
    align-items: center;
    padding: 0.5rem;
    border-right: none;
    border-bottom: 1px solid #e5e7eb;
    z-index: 1000;
  }

  .sidebar-header {
    margin-bottom: 0;
    padding: 0.5rem;
  }

  .logo-text {
    display: none;
  }

  .nav-links {
    flex-direction: row;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    align-items: center;
  }

  .nav-link {
    min-height: 44px;
    min-width: 44px;
    white-space: nowrap;
  }

  .sidebar-footer {
    margin-top: 0;
    border-top: none;
    padding-top: 0;
    margin-left: auto;
  }

  .logout-btn {
    min-height: 44px;
    min-width: 44px;
    padding: 0.5rem;
  }
  
  .logout-btn text {
    display: none;
  }
}
</style>
