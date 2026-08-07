<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { getAll } from '../services/hardware'
import { rent } from '../services/rentals'
import { useToastStore } from '../stores/toast'
import type { Hardware } from '../types'
import StatusBadge from '../components/shared/StatusBadge.vue'

const toastStore = useToastStore()

const items = ref<Hardware[]>([])
const loading = ref(false)
const aiSearch = ref('')

// Pagination
const page = ref(1)
const limit = ref(10)
const totalCount = ref(0)
const hasNext = ref(false)

// Filters & Sorting
const statusFilter = ref<string>('')
const sortBy = ref<string>('created_at')
const sortOrder = ref<'asc' | 'desc'>('desc')

const statuses = ['Available', 'In Use', 'Repair']

async function fetchHardware() {
  loading.value = true
  try {
    const data = await getAll({
      page: page.value,
      limit: limit.value,
      status: statusFilter.value || undefined,
      sort_by: sortBy.value,
      sort_order: sortOrder.value
    })
    items.value = data
    totalCount.value = data.length
    hasNext.value = data.length === limit.value
  } catch (error: any) {
    toastStore.add('Failed to load hardware inventory', 'error')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchHardware()
})

watch([page, statusFilter, sortBy, sortOrder], () => {
  fetchHardware()
})

function toggleSort(field: string) {
  if (sortBy.value === field) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortBy.value = field
    sortOrder.value = 'asc'
  }
}

async function handleRent(id: number) {
  try {
    await rent(id)
    toastStore.add('Hardware rented successfully!', 'success')
    await fetchHardware()
  } catch (error: any) {
    toastStore.add(error.response?.data?.detail || 'Failed to rent hardware', 'error')
  }
}

function formatDate(dateStr: string | null) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString()
}
</script>

<template>
  <div class="dashboard-container">
    
    <!-- AI Search Section -->
    <div class="ai-search-section">
      <div class="search-wrapper">
        <span class="sparkle-icon">✨</span>
        <input 
          type="text" 
          v-model="aiSearch"
          placeholder="Ask AI (e.g., 'Show me all available Dell laptops...')"
          class="ai-search-input"
        />
        <button class="ai-search-btn" disabled>Search</button>
      </div>
    </div>

    <!-- Header & Controls -->
    <div class="controls-section">
      <h1 class="page-title">Hardware Inventory</h1>
      
      <div class="filters">
        <div class="filter-group">
          <label for="status-filter">Status:</label>
          <select id="status-filter" v-model="statusFilter" class="custom-select">
            <option value="">All</option>
            <option v-for="s in statuses" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Data Table -->
    <div class="table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th @click="toggleSort('name')" class="sortable">
              Device Name 
              <span v-if="sortBy === 'name'" class="sort-icon">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
            </th>
            <th @click="toggleSort('brand')" class="sortable">
              Brand 
              <span v-if="sortBy === 'brand'" class="sort-icon">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
            </th>
            <th @click="toggleSort('created_at')" class="sortable">
              Date Added 
              <span v-if="sortBy === 'created_at'" class="sort-icon">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
            </th>
            <th>Status</th>
            <th class="action-column">Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="5" class="empty-state">Loading inventory...</td>
          </tr>
          <tr v-else-if="items.length === 0">
            <td colspan="5" class="empty-state">No hardware found.</td>
          </tr>
          <tr v-else v-for="item in items" :key="item.id" class="table-row">
            <td class="font-medium">{{ item.name }}</td>
            <td class="text-secondary">{{ item.brand }}</td>
            <td class="text-secondary">{{ formatDate(item.created_at) }}</td>
            <td>
              <StatusBadge :status="item.status" />
            </td>
            <td class="action-column">
              <button 
                class="rent-btn" 
                :disabled="item.status !== 'Available'"
                @click="handleRent(item.id)"
              >
                Rent
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <!-- Pagination -->
      <div class="pagination-footer">
        <span class="total-count">Total: {{ totalCount }} items</span>
        <div class="pagination-controls">
          <button @click="page--" :disabled="page === 1" class="page-btn">Prev</button>
          <span class="page-info">Page {{ page }}</span>
          <button @click="page++" :disabled="!hasNext" class="page-btn">Next</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  padding-bottom: 3rem;
}

/* AI Search */
.ai-search-section {
  display: flex;
  justify-content: center;
  margin-bottom: 1rem;
}

.search-wrapper {
  display: flex;
  align-items: center;
  background-color: rgba(30, 30, 30, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 9999px;
  padding: 0.5rem 1rem;
  width: 100%;
  max-width: 650px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
}
.search-wrapper:focus-within {
  border-color: #646cff;
  box-shadow: 0 0 0 2px rgba(100, 108, 255, 0.2), 0 10px 25px rgba(0, 0, 0, 0.3);
}

.sparkle-icon {
  font-size: 1.2rem;
  margin-right: 0.75rem;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 0.7; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.1); }
  100% { opacity: 0.7; transform: scale(1); }
}

.ai-search-input {
  flex: 1;
  background: transparent;
  border: none;
  color: white;
  font-size: 1rem;
  outline: none;
  padding: 0.5rem 0;
}

.ai-search-input::placeholder {
  color: #777;
}

.ai-search-btn {
  background: linear-gradient(135deg, #646cff 0%, #535bf2 100%);
  color: white;
  border: none;
  padding: 0.5rem 1.2rem;
  border-radius: 9999px;
  font-weight: 600;
  cursor: pointer;
  margin-left: 0.5rem;
  opacity: 0.7;
}

/* Controls */
.controls-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  margin: 0;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.filter-group label {
  color: #a0a0a0;
  font-weight: 500;
  font-size: 0.9rem;
}
.custom-select {
  background-color: #1e1e1e;
  color: white;
  border: 1px solid #444;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  outline: none;
  font-family: inherit;
  font-size: 0.9rem;
}

/* Table */
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

.sortable {
  cursor: pointer;
  user-select: none;
  transition: color 0.2s;
}
.sortable:hover {
  color: #fff;
}
.sort-icon {
  margin-left: 0.25rem;
  color: #646cff;
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
}

.empty-state {
  text-align: center;
  padding: 3rem !important;
  color: #777;
  font-style: italic;
}

/* Rent Button */
.rent-btn {
  background-color: transparent;
  color: #2ecc71;
  border: 1px solid rgba(46, 204, 113, 0.5);
  padding: 0.4rem 1rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}
.rent-btn:hover:not(:disabled) {
  background-color: #2ecc71;
  color: #121212;
}
.rent-btn:disabled {
  color: #555;
  border-color: #444;
  cursor: not-allowed;
  opacity: 0.6;
}

/* Pagination Footer */
.pagination-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background-color: rgba(20, 20, 20, 0.5);
}
.total-count {
  font-size: 0.85rem;
  color: #777;
}
.pagination-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.page-btn {
  background-color: #2a2a2a;
  color: #e0e0e0;
  border: 1px solid #444;
  padding: 0.3rem 0.8rem;
  border-radius: 6px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}
.page-btn:hover:not(:disabled) {
  background-color: #3a3a3a;
  color: #fff;
}
.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.page-info {
  font-size: 0.9rem;
  font-weight: 500;
}
</style>
