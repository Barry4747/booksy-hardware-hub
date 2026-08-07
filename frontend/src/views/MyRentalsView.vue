<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getMyRentals, returnRental } from '../services/rentals'
import { useToastStore } from '../stores/toast'
import type { Rental } from '../types'

const toastStore = useToastStore()

const rentals = ref<Rental[]>([])
const loading = ref(false)

async function fetchRentals() {
  loading.value = true
  try {
    rentals.value = await getMyRentals()
  } catch (error: any) {
    toastStore.add('Failed to load your rentals', 'error')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchRentals()
})

async function handleReturn(rentalId: number) {
  try {
    await returnRental(rentalId)
    toastStore.add('Hardware returned successfully!', 'success')
    await fetchRentals()
  } catch (error: any) {
    toastStore.add(error.response?.data?.detail || 'Failed to return hardware', 'error')
  }
}

function formatDate(dateStr: string | null) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString()
}
</script>

<template>
  <div class="rentals-container">
    <div class="header-section">
      <h1 class="page-title">My Rentals</h1>
      <p class="subtitle">Manage the hardware you currently have checked out.</p>
    </div>

    <div class="table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th>Device Name</th>
            <th>Brand</th>
            <th>Rented At</th>
            <th>Status</th>
            <th class="action-column">Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="5" class="empty-state">Loading your rentals...</td>
          </tr>
          <tr v-else-if="rentals.length === 0">
            <td colspan="5" class="empty-state">You haven't rented any hardware yet.</td>
          </tr>
          <tr v-else v-for="rental in rentals" :key="rental.id" class="table-row">
            <td class="font-medium">{{ rental.hardware.name }}</td>
            <td class="text-secondary">{{ rental.hardware.brand }}</td>
            <td class="text-secondary">{{ formatDate(rental.rented_at) }}</td>
            <td>
              <span v-if="rental.returned_at" class="badge-returned">Returned</span>
              <span v-else class="badge-active">Active</span>
            </td>
            <td class="action-column">
              <button 
                class="return-btn" 
                v-if="!rental.returned_at"
                @click="handleReturn(rental.id)"
              >
                Return
              </button>
              <span v-else class="returned-date">
                on {{ formatDate(rental.returned_at) }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.rentals-container {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.header-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.page-title {
  font-size: 1.35rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.subtitle {
  color: #6b7280;
  font-size: 0.95rem;
  margin: 0;
}

/* Table — Single Panel */
.table-wrapper {
  background-color: transparent;
  overflow: visible;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  background-color: #ffffff;
  border-radius: 12px;
  overflow: hidden;
  text-align: left;
}

.data-table th {
  padding: 1rem 1.5rem;
  font-size: 0.8rem;
  font-weight: 700;
  color: #111827;
  border-bottom: 1px solid #f3f4f6;
  white-space: nowrap;
}

.data-table td {
  padding: 1rem 1.5rem;
  font-size: 0.85rem;
  border-bottom: 1px solid #f3f4f6;
}

.table-row:last-child td { border-bottom: none; }
.table-row:hover td { background-color: #fafafa; }

.font-medium {
  color: #111827;
  font-weight: 500;
}
.text-secondary {
  color: #4b5563;
  font-size: 0.85rem;
}

.action-column {
  text-align: right;
  min-width: 120px;
}

.empty-state {
  text-align: center;
  padding: 3rem !important;
  color: #9ca3af;
}

.badge-active {
  background-color: #f3f4f6;
  color: #374151;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge-returned {
  background-color: #111827;
  color: #ffffff;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.return-btn {
  background-color: #111827;
  color: #ffffff;
  border: none;
  padding: 0.4rem 1.1rem;
  border-radius: 9999px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.return-btn:hover {
  background-color: #374151;
}

.returned-date {
  font-size: 0.85rem;
  color: #6b7280;
  font-style: italic;
}
</style>
