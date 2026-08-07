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
  gap: 2rem;
  padding-bottom: 3rem;
}

.header-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  margin: 0;
  color: #fff;
}

.subtitle {
  color: #a0a0a0;
  font-size: 0.95rem;
  margin: 0;
}

/* Table styles */
.table-wrapper {
  background-color: #1e1e1e;
  border: 1px solid #333;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.data-table th {
  background-color: rgba(20, 20, 20, 0.8);
  padding: 1rem 1.5rem;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #a0a0a0;
  font-weight: 600;
  border-bottom: 1px solid #333;
}

.data-table td {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #2a2a2a;
}

.table-row {
  transition: background-color 0.2s ease;
}

.table-row:hover {
  background-color: rgba(255, 255, 255, 0.03);
}

.font-medium {
  font-weight: 500;
  color: #fff;
}

.text-secondary {
  color: #999;
}

.action-column {
  text-align: right;
  min-width: 120px;
}

.empty-state {
  text-align: center;
  padding: 3rem !important;
  color: #777;
  font-style: italic;
}

/* Badges */
.badge-active {
  background-color: rgba(46, 204, 113, 0.15);
  color: #2ecc71;
  padding: 0.3rem 0.6rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid rgba(46, 204, 113, 0.3);
}

.badge-returned {
  background-color: rgba(149, 165, 166, 0.15);
  color: #95a5a6;
  padding: 0.3rem 0.6rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid rgba(149, 165, 166, 0.3);
}

/* Return Button */
.return-btn {
  background-color: transparent;
  color: #e74c3c;
  border: 1px solid rgba(231, 76, 60, 0.5);
  padding: 0.4rem 1rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.return-btn:hover {
  background-color: #e74c3c;
  color: #121212;
}

.returned-date {
  font-size: 0.85rem;
  color: #777;
  font-style: italic;
}
</style>
