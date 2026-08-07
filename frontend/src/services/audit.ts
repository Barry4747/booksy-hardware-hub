import api from './api'
import type { AuditReport } from '../types'

export async function runAudit() {
  const { data } = await api.post<AuditReport>('/api/audit')
  return data
}
