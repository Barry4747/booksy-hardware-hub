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
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  font-weight: 500;
  color: white;
  background-color: #2c2c2c;
  border-left: 5px solid transparent;
}

.toast-message {
  font-size: 0.95rem;
  line-height: 1.4;
}

.toast-success {
  border-left-color: #2ecc71;
}
.toast-error {
  border-left-color: #e74c3c;
}
.toast-info {
  border-left-color: #3498db;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  opacity: 0.6;
  padding: 0 0 0 12px;
  transition: opacity 0.2s ease;
  display: flex;
  align-items: center;
}
.close-btn:hover {
  opacity: 1;
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
