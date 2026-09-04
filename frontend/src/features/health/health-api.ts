import { apiGet } from '../../lib/api-client'

export type HealthStatus = { api: 'ok' | 'error'; database: 'ok' | 'error'; redis: 'ok' | 'error' }
type ApiHealth = { status: 'ok' | 'error' }
type ServicesHealth = { services: { database: 'ok' | 'error'; redis: 'ok' | 'error' } }

export async function getHealth(): Promise<HealthStatus> {
  const [api, services] = await Promise.all([
    apiGet<ApiHealth>('/api/v1/health'),
    apiGet<ServicesHealth>('/api/v1/health/services'),
  ])
  return { api: api.status, ...services.services }
}
