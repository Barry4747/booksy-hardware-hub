<template>
  <div class="mobile-layout">
    <MobileNavbar />
    <main class="mobile-main">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import MobileNavbar from '../components/shared/MobileNavbar.vue'
</script>

<style scoped>
.mobile-layout {
  width: 100%;
  max-width: 100%;
  overflow-x: hidden;
}

.mobile-main {
  padding-top: 56px; /* height of the fixed MobileNavbar */
  width: 100%;
  overflow-x: hidden;
  padding-left: 1rem;
  padding-right: 1rem;
  padding-bottom: 2rem;
}
</style>
