import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { vi } from 'vitest'

import { LoginPage } from './LoginPage'
import * as authApi from './auth-api'

test('submits credentials and confirms access', async () => {
  vi.spyOn(authApi, 'login').mockResolvedValue({ status: 'ok' })
  render(
    <QueryClientProvider client={new QueryClient()}>
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    </QueryClientProvider>,
  )

  fireEvent.change(screen.getByLabelText(/empresa/i), { target: { value: 'acme' } })
  fireEvent.change(screen.getByLabelText(/e-mail/i), { target: { value: 'pessoa@example.com' } })
  fireEvent.change(screen.getByLabelText(/senha/i), { target: { value: 'senha-segura-123' } })
  fireEvent.click(screen.getByRole('button', { name: /entrar/i }))

  expect(await screen.findByText('Acesso confirmado.')).toBeVisible()
})
