<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getAll, create, update, remove } from '../services/hardware'
import { runAudit } from '../services/audit'
import api from '../services/api'
import { useToastStore } from '../stores/toast'
import type { Hardware, HardwareCreate, AuditReport } from '../types'
import StatusBadge from '../components/shared/StatusBadge.vue'

const toastStore = useToastStore()

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

async function createUser() {
  isSubmittingUser.value = true
  try {
    await api.post('/api/users', userForm.value)
    toastStore.add('User created successfully', 'success')
    userForm.value = { email: '', password: '', is_admin: false }
  } catch (error: any) {
    toastStore.add(error.response?.data?.detail || 'Failed to create user', 'error')
  } finally {
    isSubmittingUser.value = false
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
})
</script>

<template>
  <div class="admin-container">
    <div class="header-section">
      <h1 class="page-title">Admin Dashboard</h1>
      <p class="subtitle">Manage hardware, users, and run AI audits.</p>
    </div>

    <!-- Tabs -->
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

    <!-- HARDWARE MANAGEMENT -->
    <div v-if="activeTab === 'hardware'" class="tab-content">
      <div class="section-header">
        <h2>Hardware Inventory</h2>
        <button class="primary-btn" @click="openAddForm">+ Add Hardware</button>
      </div>

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
              <th>ID</th>
              <th>Name</th>
              <th>Brand</th>
              <th>Status</th>
              <th>Purchase Date</th>
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
              <td class="text-secondary">#{{ item.id }}</td>
              <td class="font-medium">{{ item.name }}</td>
              <td>{{ item.brand }}</td>
              <td><StatusBadge :status="item.status" /></td>
              <td class="text-secondary">{{ formatDate(item.purchase_date) }}</td>
              <td class="action-column">
                <button class="action-btn toggle-repair" @click="toggleRepair(item)" title="Toggle Repair">
                  🔧
                </button>
                <button class="action-btn edit" @click="openEditForm(item)" title="Edit">
                  ✎
                </button>
                <button class="action-btn delete" @click="removeHardware(item.id)" title="Delete">
                  ✖
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- USER MANAGEMENT -->
    <div v-if="activeTab === 'users'" class="tab-content">
      <div class="section-header">
        <h2>Create New User</h2>
      </div>
      
      <div class="form-card">
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
    </div>

    <!-- AI AUDIT SECTION -->
    <div v-if="activeTab === 'audit'" class="tab-content">
      <div class="section-header">
        <h2>System Audit</h2>
        <button class="primary-btn audit-btn" @click="handleRunAudit" :disabled="isRunningAudit">
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

/* Tabs */
.tabs {
  display: flex;
  gap: 1rem;
  border-bottom: 1px solid #333;
  padding-bottom: 0;
}

.tab-btn {
  background: transparent;
  color: #a0a0a0;
  border: none;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  border-bottom: 3px solid transparent;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  color: #e0e0e0;
}

.tab-btn.active {
  color: #646cff;
  border-bottom: 3px solid #646cff;
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

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
}

/* Buttons */
.primary-btn {
  background: linear-gradient(135deg, #646cff 0%, #535bf2 100%);
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 10px rgba(100, 108, 255, 0.3);
}

.primary-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 15px rgba(100, 108, 255, 0.4);
}

.audit-btn {
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 99%, #fecfef 100%);
  color: #121212;
  box-shadow: 0 4px 15px rgba(255, 154, 158, 0.4);
}
.audit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

/* Forms */
.form-card {
  background-color: rgba(30, 30, 30, 0.6);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 1.5rem 2rem;
  margin-bottom: 1rem;
}

.form-card h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
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
  color: #d0d0d0;
}

.form-group input, .form-group select {
  background-color: rgba(18, 18, 18, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #fff;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.95rem;
  outline: none;
  transition: all 0.2s ease;
  font-family: inherit;
}

.form-group input:focus, .form-group select:focus {
  border-color: #646cff;
  box-shadow: 0 0 0 2px rgba(100, 108, 255, 0.2);
}

.checkbox-group label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.95rem;
}
.checkbox-group input {
  width: 1.2rem;
  height: 1.2rem;
  cursor: pointer;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}

.cancel-btn {
  background: transparent;
  color: #a0a0a0;
  border: 1px solid #444;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.cancel-btn:hover {
  background: #333;
  color: #fff;
}

.submit-btn {
  background-color: #646cff;
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
  background-color: #747bff;
}
.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
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
  min-width: 130px;
}

.empty-state {
  text-align: center;
  padding: 3rem !important;
  color: #777;
  font-style: italic;
}

.action-btn {
  background: transparent;
  border: none;
  color: #999;
  font-size: 1.1rem;
  cursor: pointer;
  margin-left: 0.5rem;
  transition: all 0.2s;
  padding: 0.3rem;
  border-radius: 4px;
}
.action-btn:hover {
  background: rgba(255,255,255,0.1);
}
.action-btn.toggle-repair:hover { color: #f39c12; }
.action-btn.edit:hover { color: #3498db; }
.action-btn.delete:hover { color: #e74c3c; }


/* Audit Section */
.audit-placeholder {
  text-align: center;
  padding: 4rem 2rem;
  background-color: rgba(30, 30, 30, 0.4);
  border: 1px dashed #444;
  border-radius: 12px;
  color: #888;
}

.placeholder-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.audit-summary-card {
  background-color: rgba(30, 30, 30, 0.6);
  border-left: 4px solid #646cff;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}
.audit-summary-card h3 {
  margin-top: 0;
  margin-bottom: 0.5rem;
  color: #e0e0e0;
}
.audit-summary-card p {
  margin: 0;
  color: #b0b0b0;
  line-height: 1.5;
}

.issues-title {
  margin-bottom: 1rem;
  font-size: 1.1rem;
  color: #e0e0e0;
}

.no-issues {
  background-color: rgba(46, 204, 113, 0.1);
  color: #2ecc71;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid rgba(46, 204, 113, 0.2);
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
  background-color: rgba(30, 30, 30, 0.6);
  border-radius: 8px;
  padding: 1.25rem;
  border-left: 4px solid #444;
}

.severity-critical { border-left-color: #e74c3c; }
.severity-warning { border-left-color: #f1c40f; }
.severity-info { border-left-color: #3498db; }

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
}
.severity-critical .issue-badge { background-color: rgba(231, 76, 60, 0.2); color: #e74c3c; }
.severity-warning .issue-badge { background-color: rgba(241, 196, 15, 0.2); color: #f1c40f; }
.severity-info .issue-badge { background-color: rgba(52, 152, 219, 0.2); color: #3498db; }

.issue-hardware {
  font-weight: 600;
  color: #fff;
}

.issue-body p {
  margin: 0.25rem 0;
  font-size: 0.95rem;
  color: #ccc;
}
.issue-body strong {
  color: #e0e0e0;
}
.issue-rec {
  color: #2ecc71 !important;
}
</style>
