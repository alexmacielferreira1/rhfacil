import { FormEvent, useState } from 'react'

import { requestAccess } from './access-api'

export function RequestAccessPage({ organizationToken }: { organizationToken: string }) {
  const [message, setMessage] = useState('')

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const result = await requestAccess(organizationToken, {
      email: String(form.get('email') ?? ''),
      name: String(form.get('name') ?? ''),
      reason: String(form.get('reason') ?? ''),
    })
    setMessage(result.message)
  }

  return (
    <main className="shell narrow-shell">
      <p className="eyebrow">ACESSO SEGURO</p>
      <h1>Solicite entrada na equipe</h1>
      <p className="lead">O administrador analisará sua solicitação.</p>
      <form className="card form-card" onSubmit={submit}>
        <label>E-mail<input name="email" type="email" required /></label>
        <label>Nome<input name="name" maxLength={160} /></label>
        <label>Motivo<textarea name="reason" maxLength={1000} /></label>
        <button type="submit">Enviar solicitação</button>
        {message && <p role="status" className="success-message">{message}</p>}
      </form>
    </main>
  )
}
