import { FormEvent, useState } from 'react'

import { activateAccount } from './access-api'

export function ActivateAccountPage({ token }: { token: string }) {
  const [message, setMessage] = useState('')

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const password = String(form.get('password') ?? '')
    const confirmation = String(form.get('confirmation') ?? '')
    if (password !== confirmation) {
      setMessage('As senhas não coincidem.')
      return
    }
    await activateAccount(token, password)
    setMessage('Conta ativada. Você já pode entrar.')
  }

  return (
    <main className="shell narrow-shell">
      <p className="eyebrow">ATIVAÇÃO</p>
      <h1>Crie sua senha</h1>
      <form className="card form-card" onSubmit={submit}>
        <label>Senha<input name="password" type="password" minLength={12} required /></label>
        <label>Confirmar senha<input name="confirmation" type="password" minLength={12} required /></label>
        <button type="submit">Ativar conta</button>
        {message && <p role="status">{message}</p>}
      </form>
    </main>
  )
}
