<script setup lang="ts">
import { RouterView } from 'vue-router'
import AppNavbar from './components/shared/AppNavbar.vue'
import AppToast from './components/shared/AppToast.vue'
</script>

<template>
  <div class="app-layout">
    <AppNavbar />
    <main class="main-content">
      <RouterView />
    </main>
    <AppToast />
  </div>
</template>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Inter', 'Roboto', 'Outfit', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f3f4f6;
  color: #111827;
  line-height: 1.6;
}

.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: row;
}

.main-content {
  flex: 1;
  padding: 2.5rem 3rem;
  width: 100%;
}
</style>
