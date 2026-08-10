<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getMyRentals, returnRental } from '../services/rentals'
import { useToastStore } from '../stores/toast'
import { useAuthStore } from '../stores/auth'
import type { Rental } from '../types'

const toastStore = useToastStore()
const authStore = useAuthStore()

const rentals = ref<Rental[]>([])
const loading = ref(false)
const showOnlyMine = ref(true)

async function fetchRentals() {
  loading.value = true
  try {
    const fetchUserId = (authStore.isAdmin && !showOnlyMine.value) ? undefined : authStore.user?.id
    rentals.value = await getMyRentals(fetchUserId)
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

import { computed } from 'vue'

const searchQuery = ref('')
const statusFilter = ref('')
const sortBy = ref('rented_at')
const sortOrder = ref<'asc'|'desc'>('desc')

const filteredRentals = computed(() => {
  let items = [...rentals.value]
  if (statusFilter.value) {
    if (statusFilter.value === 'Active') {
      items = items.filter(r => !r.returned_at)
    } else if (statusFilter.value === 'Returned') {
      items = items.filter(r => !!r.returned_at)
    }
  }
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    items = items.filter(r => 
      (r.hardware?.name && r.hardware.name.toLowerCase().includes(q)) || 
      (r.hardware?.brand && r.hardware.brand.toLowerCase().includes(q))
    )
  }
  
  items.sort((a, b) => {
    let aVal = a[sortBy.value as keyof Rental]
    let bVal = b[sortBy.value as keyof Rental]
    
    // special handling for nested hardware name
    if (sortBy.value === 'hardware_name') {
        aVal = a.hardware?.name
        bVal = b.hardware?.name
    }
    
    if (aVal == null) aVal = ''
    if (bVal == null) bVal = ''
    if (aVal < bVal) return sortOrder.value === 'asc' ? -1 : 1
    if (aVal > bVal) return sortOrder.value === 'asc' ? 1 : -1
    return 0
  })
  
  return items
})

function toggleSort(field: string) {
  if (sortBy.value === field) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortBy.value = field
    sortOrder.value = 'asc'
  }
}
</script>

<template>
  <div class="rentals-container">
    <div class="header-section">
      <div class="header-title-row">
        <h1 class="page-title">{{ authStore.isAdmin && !showOnlyMine ? 'All Rentals' : 'My Rentals' }}</h1>
        <div v-if="authStore.isAdmin" class="admin-toggle">
          <label class="toggle-label">
            <input type="checkbox" v-model="showOnlyMine" @change="fetchRentals" />
            Show only my rentals
          </label>
        </div>
      </div>
      <p class="subtitle">Manage the hardware currently checked out.</p>
    </div>
    <!-- Filters Bar -->
    <div class="filter-bar">
      <div class="search-wrapper">
        <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <input type="text" v-model="searchQuery" placeholder="Search by name or brand..." class="search-input" />
      </div>
      <div class="filter-wrapper">
        <label class="filter-label">Status:</label>
        <select v-model="statusFilter" class="custom-select">
          <option value="">All Statuses</option>
          <option value="Active">Active</option>
          <option value="Returned">Returned</option>
        </select>
      </div>
    </div>

    <div class="table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th @click="toggleSort('hardware_name')" class="sortable" style="width: 25%">
              Device Name<span v-if="sortBy === 'hardware_name'" class="sort-icon">{{ sortOrder === 'asc' ? ' ↑' : ' ↓' }}</span>
            </th>
            <th style="width: 15%">Brand</th>
            <th v-if="authStore.isAdmin && !showOnlyMine" @click="toggleSort('user_id')" class="sortable" style="width: 15%">
              User ID<span v-if="sortBy === 'user_id'" class="sort-icon">{{ sortOrder === 'asc' ? ' ↑' : ' ↓' }}</span>
            </th>
            <th @click="toggleSort('rented_at')" class="sortable" style="width: 20%">
              Rented At<span v-if="sortBy === 'rented_at'" class="sort-icon">{{ sortOrder === 'asc' ? ' ↑' : ' ↓' }}</span>
            </th>
            <th @click="toggleSort('status')" class="sortable" style="width: 10%">
              Status<span v-if="sortBy === 'status'" class="sort-icon">{{ sortOrder === 'asc' ? ' ↑' : ' ↓' }}</span>
            </th>
            <th class="action-column" style="width: 15%">Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td :colspan="authStore.isAdmin && !showOnlyMine ? 6 : 5" class="empty-state">Loading rentals...</td>
          </tr>
          <tr v-else-if="filteredRentals.length === 0">
            <td :colspan="authStore.isAdmin && !showOnlyMine ? 6 : 5" class="empty-state">No rentals found.</td>
          </tr>
          <tr v-else v-for="rental in filteredRentals" :key="rental.id" class="table-row">
            <td class="font-medium">{{ rental.hardware.name }}</td>
            <td class="text-secondary">{{ rental.hardware.brand }}</td>
            <td class="text-secondary" v-if="authStore.isAdmin && !showOnlyMine">User #{{ rental.user_id }}</td>
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

.header-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.admin-toggle {
  display: flex;
  align-items: center;
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  font-weight: 500;
  color: #374151;
  cursor: pointer;
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
  table-layout: fixed;
}

.data-table th {
  padding: 1rem 1.5rem;
  font-size: 0.8rem;
  font-weight: 700;
  color: #111827;
  border-bottom: 1px solid #f3f4f6;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.data-table td {
  padding: 1rem 1.5rem;
  font-size: 0.85rem;
  border-bottom: 1px solid #f3f4f6;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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
  padding: 3rem;
  color: #6b7280;
  font-size: 0.95rem;
}

/* Filter Bar */
.filter-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  background-color: #ffffff;
  padding: 1rem;
  border-radius: 12px;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

.search-wrapper {
  position: relative;
  flex: 1;
  min-width: 250px;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  color: #9ca3af;
}

.search-input {
  width: 100%;
  padding: 0.6rem 1rem 0.6rem 2.25rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.9rem;
  color: #111827;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.search-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.filter-wrapper {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-label {
  font-size: 0.85rem;
  font-weight: 500;
  color: #4b5563;
}

.custom-select {
  padding: 0.4rem 1.5rem 0.4rem 0.75rem;
  font-size: 0.85rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background-color: #ffffff;
  color: #111827;
  outline: none;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%236b7280'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.5rem center;
  background-size: 1rem;
}

.custom-select:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59,130,246,0.1);
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

@media (max-width: 768px) {
  .table-wrapper {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    width: 100%;
    min-width: 0;
  }

  table {
    min-width: 560px;
  }

  .return-btn {
    min-height: 44px;
    min-width: 44px;
  }

  .header-title-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
}
</style>
