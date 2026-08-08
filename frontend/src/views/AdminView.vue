<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getAll, create, update, remove } from '../services/hardware'
import { runAudit } from '../services/audit'
import { getAllUsers, deleteUser, createUser as apiCreateUser } from '../services/users'
import api from '../services/api'
import { useToastStore } from '../stores/toast'
import { useAuthStore } from '../stores/auth'
import type { Hardware, HardwareCreate, AuditReport, User } from '../types'
import StatusBadge from '../components/shared/StatusBadge.vue'

const toastStore = useToastStore()
const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()

// UI State
const activeTab = ref<'hardware' | 'users' | 'audit'>('hardware')

// Hardware Management
const hardwareItems = ref<Hardware[]>([])
const loadingHardware = ref(false)
const showHardwareForm = ref(false)
const isEditing = ref(false)
const editingId = ref<number | null>(null)

const hwForm = ref<HardwareCreate>({
  name: '',
  brand: '',
  status: 'Available',
  purchase_date: null,
  notes: null
})

async function fetchHardware() {
  loadingHardware.value = true
  try {
    // Get a larger limit for the admin panel to view all items easily
    hardwareItems.value = await getAll({ limit: 100 })
  } catch (error: any) {
    toastStore.add('Failed to fetch hardware', 'error')
  } finally {
    loadingHardware.value = false
  }
}

function openAddForm() {
  isEditing.value = false
  editingId.value = null
  hwForm.value = { name: '', brand: '', status: 'Available', purchase_date: null, notes: null }
  showHardwareForm.value = true
}

function openEditForm(hw: Hardware) {
  isEditing.value = true
  editingId.value = hw.id
  hwForm.value = { 
    name: hw.name, 
    brand: hw.brand, 
    status: hw.status, 
    purchase_date: hw.purchase_date, 
    notes: hw.notes 
  }
  showHardwareForm.value = true
}

function cancelForm() {
  showHardwareForm.value = false
}

async function submitHardwareForm() {
  try {
    const payload = {
      ...hwForm.value,
      purchase_date: hwForm.value.purchase_date || null,
      notes: hwForm.value.notes || null
    }
    if (isEditing.value && editingId.value) {
      await update(editingId.value, payload)
      toastStore.add('Hardware updated successfully', 'success')
    } else {
      await create(payload)
      toastStore.add('Hardware created successfully', 'success')
    }
    showHardwareForm.value = false
    await fetchHardware()
  } catch (error: any) {
    toastStore.add(error.response?.data?.detail || 'Failed to save hardware', 'error')
  }
}

async function removeHardware(id: number) {
  if (!confirm('Are you sure you want to delete this hardware? This action cannot be undone.')) return
  try {
    await remove(id)
    toastStore.add('Hardware deleted', 'success')
    await fetchHardware()
  } catch (error: any) {
    toastStore.add(error.response?.data?.detail || 'Failed to delete hardware', 'error')
  }
}

async function toggleRepair(hw: Hardware) {
  const newStatus = hw.status === 'Repair' ? 'Available' : 'Repair'
  try {
    await update(hw.id, { status: newStatus })
    toastStore.add(`Status changed to ${newStatus}`, 'success')
    await fetchHardware()
  } catch (error: any) {
    toastStore.add(error.response?.data?.detail || 'Failed to change status', 'error')
  }
}

// User Management
const userForm = ref({
  email: '',
  password: '',
  is_admin: false
})
const isSubmittingUser = ref(false)
const usersList = ref<User[]>([])
const loadingUsers = ref(false)

async function fetchUsers() {
  loadingUsers.value = true
  try {
    usersList.value = await getAllUsers()
  } catch (error: any) {
    toastStore.add('Failed to fetch users', 'error')
  } finally {
    loadingUsers.value = false
  }
}

async function createUser() {
  isSubmittingUser.value = true
  try {
    await apiCreateUser(userForm.value)
    toastStore.add('User created successfully', 'success')
    userForm.value = { email: '', password: '', is_admin: false }
    await fetchUsers()
  } catch (error: any) {
    toastStore.add(error.response?.data?.detail || 'Failed to create user', 'error')
  } finally {
    isSubmittingUser.value = false
  }
}

async function handleDeleteUser(id: number) {
  if (!confirm('Are you sure you want to delete this user?')) return
  try {
    const result = await deleteUser(id)
    if (result.force_closed_rentals > 0) {
      toastStore.add(`User deleted. ${result.force_closed_rentals} active rentals were force-closed and hardware returned.`, 'warning')
    } else {
      toastStore.add('User deleted successfully.', 'success')
    }
    
    if (id === authStore.user?.id) {
      toastStore.add('You deleted your own account. Logging out...', 'warning')
      authStore.user = null
      router.push('/login')
      return
    }

    await fetchUsers()
  } catch (error: any) {
    toastStore.add(error.response?.data?.detail || 'Failed to delete user', 'error')
  }
}

// Audit Section
const auditReport = ref<AuditReport | null>(null)
const isRunningAudit = ref(false)

async function handleRunAudit() {
  isRunningAudit.value = true
  auditReport.value = null
  try {
    auditReport.value = await runAudit()
    toastStore.add('Audit completed', 'success')
  } catch (error: any) {
    toastStore.add(error.response?.data?.detail || 'Failed to run audit', 'error')
  } finally {
    isRunningAudit.value = false
  }
}

function formatDate(dateStr: string | null) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString()
}

onMounted(() => {
  fetchHardware()
  fetchUsers()
  
  if (route.query.tab === 'audit') {
    activeTab.value = 'audit'
    if (route.query.run === 'true') {
      handleRunAudit()
    }
    // Clean up query params so it doesn't run again on refresh
    router.replace({ query: {} })
  }
})
</script>

<template>
  <div class="admin-container">
    <div class="header-section">
      <div class="header-content">
        <h1 class="page-title">Hardware Management</h1>
        <button v-if="activeTab === 'hardware'" class="primary-btn" @click="openAddForm">
          <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          Add New Device
        </button>
      </div>
      
      <div class="tabs">
        <button 
          :class="['tab-btn', { active: activeTab === 'hardware' }]" 
          @click="activeTab = 'hardware'"
        >
          Hardware
        </button>
        <button 
          :class="['tab-btn', { active: activeTab === 'users' }]" 
          @click="activeTab = 'users'"
        >
          Users
        </button>
        <button 
          :class="['tab-btn', { active: activeTab === 'audit' }]" 
          @click="activeTab = 'audit'"
        >
          AI Audit
        </button>
      </div>
    </div>

    <!-- HARDWARE MANAGEMENT -->
    <div v-if="activeTab === 'hardware'" class="tab-content">
      <!-- Hardware Form Modal / Inline -->
      <div v-if="showHardwareForm" class="form-card">
        <h3>{{ isEditing ? 'Edit Hardware' : 'New Hardware' }}</h3>
        <form @submit.prevent="submitHardwareForm" class="admin-form">
          <div class="form-row">
            <div class="form-group">
              <label>Name</label>
              <input type="text" v-model="hwForm.name" required />
            </div>
            <div class="form-group">
              <label>Brand</label>
              <input type="text" v-model="hwForm.brand" required />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Purchase Date</label>
              <input type="date" v-model="hwForm.purchase_date" />
            </div>
            <div class="form-group">
              <label>Status</label>
              <select v-model="hwForm.status">
                <option value="Available">Available</option>
                <option value="In Use">In Use</option>
                <option value="Repair">Repair</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label>Notes</label>
            <input type="text" v-model="hwForm.notes" placeholder="Optional details..." />
          </div>
          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="cancelForm">Cancel</button>
            <button type="submit" class="submit-btn">{{ isEditing ? 'Save Changes' : 'Create' }}</button>
          </div>
        </form>
      </div>

      <!-- Hardware Table -->
      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>Device Name</th>
              <th class="th-center">Brand</th>
              <th class="th-center">Serial Number</th>
              <th class="th-center">Date Added</th>
              <th class="th-center">Status</th>
              <th class="action-column">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loadingHardware">
              <td colspan="6" class="empty-state">Loading hardware...</td>
            </tr>
            <tr v-else-if="hardwareItems.length === 0">
              <td colspan="6" class="empty-state">No hardware found.</td>
            </tr>
            <tr v-else v-for="item in hardwareItems" :key="item.id" class="table-row">
              <td class="font-medium">{{ item.name }}</td>
              <td class="text-secondary col-center">{{ item.brand }}</td>
              <td class="text-secondary col-center">#{{ item.id }}</td>
              <td class="text-secondary col-center">{{ formatDate(item.purchase_date) }}</td>
              <td class="col-center"><StatusBadge :status="item.status" /></td>
              <td class="action-column">
                <button class="action-btn edit" @click="openEditForm(item)" title="Edit">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="icon">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                  </svg>
                </button>
                <button class="action-btn toggle-repair" @click="toggleRepair(item)" title="Toggle Repair">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="icon">
                    <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path>
                  </svg>
                </button>
                <button class="action-btn delete" @click="removeHardware(item.id)" title="Delete">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="icon">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    <line x1="10" y1="11" x2="10" y2="17"></line>
                    <line x1="14" y1="11" x2="14" y2="17"></line>
                  </svg>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- USER MANAGEMENT -->
    <div v-if="activeTab === 'users'" class="tab-content">
      <div class="form-card">
        <h3>Create New User</h3>
        <form @submit.prevent="createUser" class="admin-form">
          <div class="form-group">
            <label>Email Address</label>
            <input type="email" v-model="userForm.email" required placeholder="user@example.com" />
          </div>
          <div class="form-group">
            <label>Password</label>
            <input type="password" v-model="userForm.password" required placeholder="••••••••" />
          </div>
          <div class="form-group checkbox-group">
            <label>
              <input type="checkbox" v-model="userForm.is_admin" />
              Give Administrator Privileges
            </label>
          </div>
          <div class="form-actions">
            <button type="submit" class="submit-btn" :disabled="isSubmittingUser">
              {{ isSubmittingUser ? 'Creating...' : 'Create User' }}
            </button>
          </div>
        </form>
      </div>

      <!-- Users Table -->
      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Email</th>
              <th class="th-center">Admin</th>
              <th class="th-center">Joined</th>
              <th class="action-column">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loadingUsers">
              <td colspan="5" class="empty-state">Loading users...</td>
            </tr>
            <tr v-else-if="usersList.length === 0">
              <td colspan="5" class="empty-state">No users found.</td>
            </tr>
            <tr v-else v-for="u in usersList" :key="u.id" class="table-row">
              <td class="text-secondary font-medium">#{{ u.id }}</td>
              <td class="font-medium">{{ u.email }}</td>
              <td class="col-center">
                <span v-if="u.is_admin" class="issue-badge" style="background-color: #111827; color: white;">ADMIN</span>
                <span v-else class="text-secondary">User</span>
              </td>
              <td class="text-secondary col-center">{{ formatDate(u.created_at) }}</td>
              <td class="action-column">
                <button class="action-btn delete" @click="handleDeleteUser(u.id)" title="Delete User">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="icon">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    <line x1="10" y1="11" x2="10" y2="17"></line>
                    <line x1="14" y1="11" x2="14" y2="17"></line>
                  </svg>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- AI AUDIT SECTION -->
    <div v-if="activeTab === 'audit'" class="tab-content">
      <div class="audit-header">
        <button class="primary-btn" @click="handleRunAudit" :disabled="isRunningAudit">
          <svg v-if="isRunningAudit" class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10" stroke-opacity="0.25"></circle>
            <path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round"></path>
          </svg>
          {{ isRunningAudit ? 'Analyzing...' : 'Run Audit' }}
        </button>
      </div>

      <div v-if="auditReport" class="audit-results">
        <div class="audit-summary-card">
          <h3>Audit Summary</h3>
          <p>{{ auditReport.summary }}</p>
        </div>

        <h3 class="issues-title">Detected Issues ({{ auditReport.issues.length }})</h3>
        
        <div v-if="auditReport.issues.length === 0" class="no-issues">
          <span class="icon">✅</span> No issues detected. Your inventory is perfect!
        </div>
        
        <div class="issues-list" v-else>
          <div 
            v-for="(issue, index) in auditReport.issues" 
            :key="index"
            :class="['issue-card', `severity-${issue.severity}`]"
          >
            <div class="issue-header">
              <span class="issue-badge">{{ issue.severity.toUpperCase() }}</span>
              <span class="issue-hardware">Hardware #{{ issue.hardware_id }}: {{ issue.hardware_name }}</span>
            </div>
            <div class="issue-body">
              <p class="issue-desc"><strong>Issue:</strong> {{ issue.issue }}</p>
              <p class="issue-rec"><strong>Recommendation:</strong> {{ issue.recommendation }}</p>
            </div>
          </div>
        </div>
      </div>
      
      <div v-else-if="!isRunningAudit" class="audit-placeholder">
        <div class="placeholder-icon">🤖</div>
        <p>Run the AI Audit to detect anomalies, missing data, and maintenance requirements across all inventory.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  width: 100%;
}

.header-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

/* Primary Add Button */
.primary-btn {
  background-color: #111827;
  color: #ffffff;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 9999px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.primary-btn:hover {
  background-color: #374151;
}

.btn-icon {
  width: 16px;
  height: 16px;
}

/* Tabs */
.tabs {
  display: flex;
  gap: 2rem;
  border-bottom: 1px solid #e5e7eb;
}

.tab-btn {
  background: transparent;
  color: #6b7280;
  border: none;
  padding: 0.5rem 0;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s ease;
  margin-bottom: -1px;
}

.tab-btn:hover {
  color: #111827;
}

.tab-btn.active {
  color: #111827;
  border-bottom: 2px solid #111827;
  font-weight: 600;
}

.tab-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Forms */
.form-card {
  background-color: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1.5rem 2rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.form-card h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
  color: #111827;
}

.admin-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #374151;
}

.form-group input, .form-group select {
  background-color: #f9fafb;
  border: 1px solid #d1d5db;
  color: #111827;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.95rem;
  outline: none;
  transition: all 0.2s ease;
}

.form-group input:focus, .form-group select:focus {
  border-color: #111827;
  background-color: #ffffff;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.95rem;
  color: #374151;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}

.cancel-btn {
  background: #f3f4f6;
  color: #4b5563;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn:hover {
  background: #e5e7eb;
}

.submit-btn {
  background-color: #111827;
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.submit-btn:hover {
  background-color: #374151;
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
  min-width: 110px;
}

.th-center, .col-center { text-align: center; }

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #9ca3af;
}

.action-btn {
  background: transparent;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  margin-left: 0.6rem;
  padding: 0;
  vertical-align: middle;
  transition: color 0.15s;
}
.icon {
  width: 17px;
  height: 17px;
  display: block;
}
.action-btn:hover { color: #374151; }
.action-btn.delete { color: #ef4444; opacity: 0.7; }
.action-btn.delete:hover { opacity: 1; }

/* Audit Section */
.audit-header {
  display: flex;
  justify-content: flex-end;
}

.spinner {
  width: 16px;
  height: 16px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.audit-placeholder {
  text-align: center;
  padding: 4rem 2rem;
  background-color: #f9fafb;
  border: 1px dashed #d1d5db;
  border-radius: 12px;
  color: #6b7280;
}

.placeholder-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.audit-summary-card {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
  margin-bottom: 2rem;
}
.audit-summary-card h3 {
  margin-top: 0;
  margin-bottom: 0.5rem;
  color: #111827;
}
.audit-summary-card p {
  margin: 0;
  color: #4b5563;
  line-height: 1.5;
}

.issues-title {
  margin-bottom: 1rem;
  font-size: 1.1rem;
  color: #111827;
}

.no-issues {
  background-color: #ffffff;
  color: #111827;
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 500;
}

.issues-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.issue-card {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 1.25rem;
  border: 1px solid #e5e7eb;
}

.issue-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.issue-badge {
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  background-color: #f3f4f6;
  color: #374151;
}

.issue-hardware {
  font-weight: 600;
  color: #111827;
}

.issue-body p {
  margin: 0.25rem 0;
  font-size: 0.95rem;
  color: #4b5563;
}
.issue-body strong {
  color: #111827;
}
</style>
