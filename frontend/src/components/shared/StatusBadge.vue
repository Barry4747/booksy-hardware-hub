<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  status: 'Available' | 'In Use' | 'Repair'
}>()

const statusClass = computed(() => {
  switch (props.status) {
    case 'Available': return 'badge-available'
    case 'In Use': return 'badge-in-use'
    case 'Repair': return 'badge-repair'
    default: return ''
  }
})
</script>

<template>
  <span class="badge" :class="statusClass">
    {{ status }}
  </span>
</template>

<style scoped>
.badge {
  padding: 0.3rem 0.8rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.badge-available {
  background-color: #111827;
  color: #ffffff;
}
.badge-in-use {
  background-color: #f3f4f6;
  color: #6b7280;
}
.badge-repair {
  background-color: #ef4444;
  color: #ffffff;
}
</style>
