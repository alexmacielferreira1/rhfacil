import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { vi } from 'vitest'
import { HealthPage } from './HealthPage'
import * as healthApi from './health-api'

vi.spyOn(healthApi, 'getHealth').mockResolvedValue({ api: 'ok', database: 'ok', redis: 'ok' })

test('shows every foundation service as operational', async () => {
  render(<QueryClientProvider client={new QueryClient()}><HealthPage /></QueryClientProvider>)
  expect(await screen.findByText('API operacional')).toBeInTheDocument()
  expect(screen.getByText('PostgreSQL operacional')).toBeInTheDocument()
  expect(screen.getByText('Redis operacional')).toBeInTheDocument()
})
