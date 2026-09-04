import type { OrgNode } from '../../mock/people-data'

function initials(name: string) {
  return name.split(' ').map((p) => p[0]).slice(0, 2).join('')
}

function OrgBranch({ node }: { node: OrgNode }) {
  return (
    <li className="org-node">
      <div className="org-card">
        <span className="avatar">{initials(node.nome)}</span>
        <div>
          <strong>{node.nome}</strong>
          <span className="lead" style={{ fontSize: '.8rem' }}>{node.cargo}</span>
          {node.equipe !== undefined && <span className="org-team-count">{node.equipe} colaboradores</span>}
        </div>
      </div>
      {node.filhos && node.filhos.length > 0 && (
        <ul>
          {node.filhos.map((child) => (
            <OrgBranch key={child.nome} node={child} />
          ))}
        </ul>
      )}
    </li>
  )
}

export function OrgChart({ root }: { root: OrgNode }) {
  return (
    <div className="org-chart">
      <ul>
        <OrgBranch node={root} />
      </ul>
    </div>
  )
}
