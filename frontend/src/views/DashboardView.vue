<script setup lang="ts">
import { ref, onMounted, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { getAll } from '../services/hardware'
import { rent } from '../services/rentals'
import { useToastStore } from '../stores/toast'
import type { Hardware } from '../types'
import StatusBadge from '../components/shared/StatusBadge.vue'

const toastStore = useToastStore()
const router = useRouter()
const authStore = useAuthStore()

const items = ref<Hardware[]>([])
const loading = ref(false)

const page = ref(1)
const limit = ref(10)
const totalCount = ref(0)
const hasNext = ref(false)

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

// rentingIds tracks in-flight requests to prevent double-click race conditions
const rentingIds = reactive(new Set<number>())

async function handleRent(id: number) {
  if (rentingIds.has(id)) return
  rentingIds.add(id)
  try {
    await rent(id)
    toastStore.add('Hardware rented successfully!', 'success')
    await fetchHardware()
  } catch (error: any) {
    toastStore.add(error.response?.data?.detail || 'Failed to rent hardware', 'error')
  } finally {
    rentingIds.delete(id)
  }
}

function formatDate(dateStr: string | null) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString()
}

function goToAudit() {
  router.push('/admin?tab=audit&run=true')
}
</script>

<template>
  <div class="dashboard-container">

    <div class="header-row">
      <h1 class="page-title">Hardware List</h1>
      <button 
        v-if="authStore.user?.is_admin" 
        class="audit-action-btn"
        @click="goToAudit"
      >
        <svg class="sparkle-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
        </svg>
        AI Audit
      </button>
    </div>

    <!-- Data Table -->
    <div class="table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th @click="toggleSort('name')" class="sortable">
              Device Name<span v-if="sortBy === 'name'" class="sort-icon">{{ sortOrder === 'asc' ? ' ↑' : ' ↓' }}</span>
            </th>
            <th @click="toggleSort('brand')" class="sortable th-center">
              Brand<span v-if="sortBy === 'brand'" class="sort-icon">{{ sortOrder === 'asc' ? ' ↑' : ' ↓' }}</span>
            </th>
            <th @click="toggleSort('created_at')" class="sortable th-center">
              Date Added<span v-if="sortBy === 'created_at'" class="sort-icon">{{ sortOrder === 'asc' ? ' ↑' : ' ↓' }}</span>
            </th>
            <th class="th-center">Status</th>
            <th class="th-center">Action</th>
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
            <td class="col-name">{{ item.name }}</td>
            <td class="col-accent col-center">{{ item.brand }}</td>
            <td class="col-accent col-center">{{ formatDate(item.created_at) }}</td>
            <td class="col-center"><StatusBadge :status="item.status" /></td>
            <td class="col-center">
              <button
                class="rent-btn"
                :class="{ 'rent-btn--inactive': item.status !== 'Available' || rentingIds.has(item.id) }"
                :disabled="item.status !== 'Available' || rentingIds.has(item.id)"
                @click="handleRent(item.id)"
              >
                {{ rentingIds.has(item.id) ? 'Renting...' : 'Rent' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div class="pagination-footer">
      <span class="total-count">Total: {{ totalCount }} items</span>
      <div class="pagination-controls">
        <button @click="page--" :disabled="page === 1" class="page-btn">Prev</button>
        <span class="page-info">Page {{ page }}</span>
        <button @click="page++" :disabled="!hasNext" class="page-btn">Next</button>
      </div>
    </div>

    <!-- Status Filter (minimal, below table) -->
    <div class="filters-row">
      <label class="filter-label">Filter:</label>
      <select id="status-filter" v-model="statusFilter" class="custom-select">
        <option value="">All Statuses</option>
        <option v-for="s in statuses" :key="s" :value="s">{{ s }}</option>
      </select>
    </div>

  </div>
</template>

<style scoped>
.dashboard-container {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 1.35rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.audit-action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #8b5cf6;
  color: #ffffff;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.audit-action-btn:hover {
  background-color: #7c3aed;
}

.sparkle-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

/* Table — Single Panel */
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
.sortable { cursor: pointer; user-select: none; }
.sortable:hover { color: #374151; }
.sort-icon { font-size: 0.75rem; }

.table-row td {
  padding: 1rem 1.5rem;
  font-size: 0.85rem;
  border-bottom: 1px solid #f3f4f6;
}
.table-row:last-child td { border-bottom: none; }
.table-row:hover td { background-color: #fafafa; }

.col-name { color: #111827; font-weight: 500; }
.col-accent { color: #4b5563; font-size: 0.85rem; }

.th-center, .col-center { text-align: center; }
.th-right { text-align: right; }
.td-right { text-align: right; }

/* Rent button */
.rent-btn {
  background-color: #111827;
  color: #ffffff;
  border: none;
  padding: 0.5rem 1.25rem;
  border-radius: 9999px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.15s;
}
.rent-btn:hover:not(:disabled) { background-color: #374151; }
.rent-btn--inactive,
.rent-btn:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #9ca3af;
}

/* Pagination */
.pagination-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 0.5rem;
  border-top: 1px solid #e5e7eb;
}
.total-count { font-size: 0.85rem; color: #6b7280; }
.pagination-controls { display: flex; align-items: center; gap: 0.75rem; }
.page-btn {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
  padding: 0.3rem 0.8rem;
  border-radius: 6px;
  font-size: 0.85rem;
  cursor: pointer;
}
.page-btn:hover:not(:disabled) { background: #e5e7eb; }
.page-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.page-info { font-size: 0.9rem; color: #374151; }

/* Filter */
.filters-row { display: flex; align-items: center; gap: 0.75rem; }
.filter-label { font-size: 0.875rem; color: #6b7280; }
.custom-select {
  background-color: #f9fafb;
  border: 1px solid #d1d5db;
  color: #374151;
  padding: 0.4rem 0.75rem;
  border-radius: 6px;
  font-size: 0.875rem;
  outline: none;
  font-family: inherit;
  cursor: pointer;
}

@media (max-width: 768px) {
  .header-row {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .audit-action-btn {
    min-height: 44px;
    width: 100%;
    justify-content: center;
  }

  .table-wrapper {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    width: 100%;
  }

  table {
    min-width: 560px;
  }

  .data-table th, .data-table td {
    white-space: nowrap;
  }

  .rent-btn {
    min-height: 44px;
    min-width: 44px;
  }

  .pagination-footer {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }

  .pagination-controls {
    flex-direction: column;
    width: 100%;
  }

  .page-btn {
    width: 100%;
    min-height: 44px;
  }

  .filters-row {
    flex-direction: column;
    align-items: stretch;
  }

  .custom-select {
    width: 100%;
    min-height: 44px;
  }
}
</style>
