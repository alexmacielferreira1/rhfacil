import { useEffect, useState } from 'react'

import {
  type AccessRequest,
  decideAccessRequest,
  listAccessRequests,
} from './access-api'

export function ManageAccessRequestsPage() {
  const [requests, setRequests] = useState<AccessRequest[]>([])

  useEffect(() => {
    void listAccessRequests().then(setRequests)
  }, [])

  async function decide(id: string, decision: 'approved' | 'rejected') {
    const result = await decideAccessRequest(id, decision)
    setRequests((items) =>
      items.map((item) => (item.id === id ? { ...item, status: result.status } : item)),
    )
  }

  return (
    <main className="shell">
      <p className="eyebrow">ADMINISTRAÇÃO</p>
      <h1>Solicitações de acesso</h1>
      <div className="grid">
        {requests.map((item) => (
          <article className="card" key={item.id}>
            <h2>{item.name || 'Pessoa solicitante'}</h2>
            <p>{item.email}</p>
            {item.status === 'pending' ? (
              <div className="actions">
                <button onClick={() => void decide(item.id, 'approved')}>Aprovar</button>
                <button className="secondary" onClick={() => void decide(item.id, 'rejected')}>Rejeitar</button>
              </div>
            ) : (
              <p role="status">Solicitação {item.status === 'approved' ? 'aprovada' : 'rejeitada'}.</p>
            )}
          </article>
        ))}
      </div>
    </main>
  )
}
