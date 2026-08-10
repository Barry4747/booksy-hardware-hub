<template>
  <div class="desktop-layout">
    <AppNavbar />
    <main class="desktop-main">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import AppNavbar from '../components/shared/AppNavbar.vue'
</script>

<style scoped>
.desktop-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: row;
}

.desktop-main {
  flex: 1;
  padding: 2.5rem 3rem;
  width: 100%;
}
</style>
