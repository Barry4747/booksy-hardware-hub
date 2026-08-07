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
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}
.badge-available {
  background-color: rgba(46, 204, 113, 0.15);
  color: #2ecc71;
  border: 1px solid rgba(46, 204, 113, 0.3);
}
.badge-in-use {
  background-color: rgba(149, 165, 166, 0.15);
  color: #bdc3c7;
  border: 1px solid rgba(149, 165, 166, 0.3);
}
.badge-repair {
  background-color: rgba(231, 76, 60, 0.15);
  color: #e74c3c;
  border: 1px solid rgba(231, 76, 60, 0.3);
}
</style>
