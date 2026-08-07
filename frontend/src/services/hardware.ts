import api from './api'
import type { Hardware, HardwareCreate, HardwareUpdate, PaginatedResponse } from '../types'

export async function getAll(params: { page?: number, limit?: number, status?: string, sort_by?: string, sort_order?: string } = {}) {
  const { data } = await api.get<PaginatedResponse<Hardware>>('/api/hardware', { params })
  return data
}

export async function getById(id: number) {
  const { data } = await api.get<Hardware>(`/api/hardware/${id}`)
  return data
}

export async function create(hardwareData: HardwareCreate) {
  const { data } = await api.post<Hardware>('/api/hardware', hardwareData)
  return data
}

export async function update(id: number, hardwareData: HardwareUpdate) {
  const { data } = await api.put<Hardware>(`/api/hardware/${id}`, hardwareData)
  return data
}

export async function remove(id: number) {
  await api.delete(`/api/hardware/${id}`)
}
