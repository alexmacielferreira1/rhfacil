import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { vi } from 'vitest'

import { EmployeesPage } from './EmployeesPage'
import * as employeesApi from './employees-api'

test('shows registered employees and their status', async () => {
  vi.spyOn(employeesApi, 'listEmployees').mockResolvedValue([{
    id: 'employee-1', full_name: 'Marina Souza', email: 'marina@example.com',
    job_title: 'Analista de Pessoas', department: 'RH', status: 'active',
    admission_date: '2026-01-10', termination_date: null,
    manager_id: null, manager_name: null, contract_type: null, level: null,
    cost_center: null, salary_amount: null,
    created_at: '2026-09-02T12:00:00Z', updated_at: '2026-09-02T12:00:00Z',
  }])

  render(
    <MemoryRouter>
      <QueryClientProvider client={new QueryClient()}>
        <EmployeesPage />
      </QueryClientProvider>
    </MemoryRouter>,
  )

  expect(await screen.findByRole('heading', { name: 'Colaboradores' })).toBeVisible()
  expect(await screen.findByRole('heading', { name: 'Marina Souza' })).toBeVisible()
  expect(screen.getByText('Analista de Pessoas · RH')).toBeVisible()
  expect(screen.getByText('Ativo')).toBeVisible()
})
