import { useQuery } from '@tanstack/react-query'
import { getHealth } from './health-api'

const labels = { api: 'API', database: 'PostgreSQL', redis: 'Redis' } as const

export function HealthPage() {
  const health = useQuery({ queryKey: ['health'], queryFn: getHealth, retry: false })
  return (
    <main className="shell">
      <p className="eyebrow">BASE SAAS V1</p>
      <h1>Fundação pronta para o próximo produto.</h1>
      <p className="lead">Serviços essenciais, isolados e verificáveis.</p>
      {health.isPending && <p role="status">Verificando serviços…</p>}
      {health.isError && <p role="alert">Não foi possível verificar os serviços.</p>}
      {health.data && (
        <section className="grid" aria-label="Estado dos serviços">
          {(Object.keys(labels) as Array<keyof typeof labels>).map((key) => (
            <article className={`card ${health.data[key]}`} key={key}>
              <span aria-hidden="true">●</span>
              <strong>{labels[key]}</strong>
              <p>{labels[key]} {health.data[key] === 'ok' ? 'operacional' : 'indisponível'}</p>
            </article>
          ))}
        </section>
      )}
    </main>
  )
}
