<script setup lang="ts">
import { useToastStore } from '../../stores/toast'

const toastStore = useToastStore()
</script>

<template>
  <div class="toast-container">
    <TransitionGroup name="toast-list">
      <div 
        v-for="toast in toastStore.toasts" 
        :key="toast.id" 
        class="toast"
        :class="[`toast-${toast.type}`]"
      >
        <span class="toast-message">{{ toast.message }}</span>
        <button @click="toastStore.remove(toast.id)" class="close-btn">&times;</button>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-container {
  position: fixed;
  top: 24px;
  right: 24px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 12px;
  pointer-events: none;
}

.toast {
  pointer-events: auto;
  min-width: 280px;
  max-width: 400px;
  padding: 14px 18px;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  font-weight: 500;
  color: #111827;
  background-color: #ffffff;
  border: 1px solid #e5e7eb;
  border-left: 4px solid transparent;
}

.toast-message {
  font-size: 0.95rem;
  line-height: 1.4;
}

.toast-success {
  border-left-color: #10b981;
}
.toast-error {
  border-left-color: #ef4444;
}
.toast-info {
  border-left-color: #3b82f6;
}

.close-btn {
  background: none;
  border: none;
  color: #9ca3af;
  font-size: 1.5rem;
  cursor: pointer;
  opacity: 0.6;
  padding: 0 0 0 12px;
  transition: opacity 0.2s ease, color 0.2s ease;
  display: flex;
  align-items: center;
}
.close-btn:hover {
  opacity: 1;
  color: #374151;
}

/* Transitions */
.toast-list-enter-active,
.toast-list-leave-active {
  transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
.toast-list-enter-from {
  opacity: 0;
  transform: translateX(50px) scale(0.9);
}
.toast-list-leave-to {
  opacity: 0;
  transform: translateY(-30px) scale(0.9);
}
</style>
