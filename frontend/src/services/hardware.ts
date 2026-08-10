import api from './api'
import type { Hardware, HardwareCreate, HardwareUpdate, PaginatedResponse } from '../types'

export async function getAll(params: { page?: number, limit?: number, status?: string, sort_by?: string, sort_order?: string } = {}) {
  const page = params.page || 1
  const limit = params.limit || 10
  const skip = (page - 1) * limit
  const query = {
    skip,
    limit: limit + 1,
    status: params.status,
    sort_by: params.sort_by,
    sort_desc: params.sort_order === 'desc'
  }
  const { data } = await api.get<Hardware[]>('/api/hardware', { params: query })
  return {
    items: data.slice(0, limit),
    hasNext: data.length > limit
  }
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
