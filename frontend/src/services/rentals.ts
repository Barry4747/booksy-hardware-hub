import api from './api'
import type { Rental } from '../types'

export async function rent(hardwareId: number) {
  const { data } = await api.post<Rental>('/api/rentals', { hardware_id: hardwareId })
  return data
}

export async function returnRental(rentalId: number) {
  const { data } = await api.post<Rental>(`/api/rentals/${rentalId}/return`)
  return data
}

export async function getMyRentals(userId?: number) {
  const params = userId ? { user_id: userId } : undefined
  const { data } = await api.get<Rental[]>('/api/rentals', { params })
  return data
}
