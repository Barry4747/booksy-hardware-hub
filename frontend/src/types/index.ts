export interface User {
  id: number
  email: string
  is_admin: boolean
  created_at: string
}

export interface UserCreate {
  email: string
  password: string
  is_admin?: boolean
}

export interface Hardware {
  id: number
  name: string
  brand: string
  purchase_date: string | null
  status: 'Available' | 'In Use' | 'Repair'
  notes: string | null
  serial_number: string | null
  created_at: string
}

export type HardwareCreate = Omit<Hardware, 'id' | 'created_at' | 'status'> & { status?: Hardware['status'] }
export type HardwareUpdate = Partial<HardwareCreate>

export interface Rental {
  id: number
  hardware_id: number
  user_id: number
  rented_at: string
  returned_at: string | null
  hardware: Hardware
}

export interface AuditIssue {
  hardware_id: number
  hardware_name: string
  severity: 'critical' | 'warning' | 'info'
  issue: string
  recommendation: string
}

export interface AuditReport {
  issues: AuditIssue[]
  summary: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total_count: number
  page: number
  limit: number
  has_next: boolean
}
