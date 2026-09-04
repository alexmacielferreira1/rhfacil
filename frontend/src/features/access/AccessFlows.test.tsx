import { fireEvent, render, screen } from '@testing-library/react'
import { vi } from 'vitest'

import { ActivateAccountPage } from './ActivateAccountPage'
import { ManageAccessRequestsPage } from './ManageAccessRequestsPage'
import { RequestAccessPage } from './RequestAccessPage'
import * as accessApi from './access-api'

test('submits a public access request with a generic confirmation', async () => {
  vi.spyOn(accessApi, 'requestAccess').mockResolvedValue({
    message: 'Solicitação recebida para análise.',
  })
  render(<RequestAccessPage organizationToken="public-token" />)

  fireEvent.change(screen.getByLabelText(/e-mail/i), {
    target: { value: 'person@example.com' },
  })
  fireEvent.click(screen.getByRole('button', { name: /enviar solicitação/i }))

  expect(await screen.findByText('Solicitação recebida para análise.')).toBeVisible()
})

test('activation requires matching secure passwords', async () => {
  render(<ActivateAccountPage token="invitation-token" />)

  fireEvent.change(screen.getByLabelText(/^senha$/i), {
    target: { value: 'a-long-secure-password' },
  })
  fireEvent.change(screen.getByLabelText(/confirmar senha/i), {
    target: { value: 'different-long-password' },
  })
  fireEvent.click(screen.getByRole('button', { name: /ativar conta/i }))

  expect(await screen.findByText(/senhas não coincidem/i)).toBeVisible()
})

test('admin can approve a pending access request', async () => {
  vi.spyOn(accessApi, 'listAccessRequests').mockResolvedValue([
    {
      id: '9ca6b682-c50b-4c21-9941-bb87557cd69c',
      email: 'candidate@example.com',
      name: 'Candidata',
      reason: null,
      status: 'pending',
      created_at: '2026-08-28T12:00:00Z',
    },
  ])
  vi.spyOn(accessApi, 'decideAccessRequest').mockResolvedValue({
    id: '9ca6b682-c50b-4c21-9941-bb87557cd69c',
    status: 'approved',
  })
  render(<ManageAccessRequestsPage />)

  expect(await screen.findByText('candidate@example.com')).toBeVisible()
  fireEvent.click(screen.getByRole('button', { name: /aprovar/i }))

  expect(await screen.findByText(/aprovada/i)).toBeVisible()
})
