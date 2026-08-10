import api from './api'
import type { User, UserCreate } from '../types'

export async function createUser(user: UserCreate) {
  const { data } = await api.post<User>('/api/users', user)
  return data
}

export async function getAllUsers() {
  const { data } = await api.get<User[]>('/api/users')
  return data
}

export async function deleteUser(id: number) {
  const { data } = await api.delete<{ message: string; force_closed_rentals: number }>(`/api/users/${id}`)
  return data
}
