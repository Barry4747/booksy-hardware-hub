<template>
  <component :is="layout">
    <slot />
  </component>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import DesktopLayout from './DesktopLayout.vue'
import MobileLayout from './MobileLayout.vue'

const isMobile = ref(window.innerWidth <= 768)

function onResize() {
  isMobile.value = window.innerWidth <= 768
}

onMounted(() => window.addEventListener('resize', onResize))
onUnmounted(() => window.removeEventListener('resize', onResize))

const layout = computed(() => isMobile.value ? MobileLayout : DesktopLayout)
</script>
