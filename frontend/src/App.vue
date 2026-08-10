<script setup lang="ts">
import { RouterView } from 'vue-router'
import AppLayout from './layouts/AppLayout.vue'
import AppToast from './components/shared/AppToast.vue'
</script>

<template>
  <AppLayout>
    <RouterView />
  </AppLayout>
  <AppToast />
</template>

<style>
*, *::before, *::after {
  box-sizing: border-box;
}

html, body, #app {
  width: 100%;
  max-width: 100%;
  overflow-x: hidden;
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
  margin: 0;
  padding: 0;
}
</style>
