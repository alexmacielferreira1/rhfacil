import { apiSend } from '../../lib/api-client'

export type LoginInput = {
  organization: string
  email: string
  password: string
}

export function login(payload: LoginInput) {
  return apiSend<{ status: string }>('/api/v1/auth/login', 'POST', payload)
}

export function logout() {
  return apiSend<{ status: string }>('/api/v1/auth/logout', 'POST', {})
}
