import { apiGet, apiSend } from '../../lib/api-client'

export type AccessRequest = {
  id: string
  email: string
  name: string | null
  reason: string | null
  status: string
  created_at: string
}

export function requestAccess(
  organizationToken: string,
  payload: { email: string; name?: string; reason?: string },
) {
  return apiSend<{ message: string }>(
    `/api/v1/access/request/${encodeURIComponent(organizationToken)}`,
    'POST',
    payload,
  )
}

export function activateAccount(token: string, password: string) {
  return apiSend<{ status: string }>('/api/v1/auth/accept-invitation', 'POST', {
    token,
    password,
  })
}

export function listAccessRequests() {
  return apiGet<AccessRequest[]>('/api/v1/access/requests')
}

export function decideAccessRequest(id: string, decision: 'approved' | 'rejected') {
  return apiSend<{ id: string; status: string }>(
    `/api/v1/access/requests/${id}`,
    'PATCH',
    { decision, role: 'member' },
  )
}
