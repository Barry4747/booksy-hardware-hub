import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import AdminView from '../views/AdminView.vue'
import MyRentalsView from '../views/MyRentalsView.vue'

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    requiresAdmin?: boolean
  }
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      name: 'dashboard',
      component: DashboardView,
      meta: { requiresAuth: true }
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminView,
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/rentals',
      name: 'rentals',
      component: MyRentalsView,
      meta: { requiresAuth: true }
    }
  ]
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // 1. Call authStore.fetchMe() if user is null and route requires auth
  if (to.meta.requiresAuth && !authStore.user) {
    await authStore.fetchMe()
  }

  // 2. If user is not logged in and route requires auth -> redirect to /login
  if (to.meta.requiresAuth && !authStore.user) {
    return next('/login')
  }

  // 3. If user is not admin and route requires admin -> redirect to /
  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    return next('/')
  }

  // 4. If user is logged in and tries to access /login -> redirect to /
  if (authStore.user && to.path === '/login') {
    return next('/')
  }

  next()
})

export default router
