import type { ReactNode } from 'react'
import { Icon } from './Icon'
import type { PageKey } from '../data/mock'

type Props = { page: PageKey; onNavigate: (page: PageKey) => void; children: ReactNode; title?: string }

const items: { key: PageKey; label: string; icon: string }[] = [
  { key: 'inicio', label: 'Início', icon: 'home' },
  { key: 'mapa', label: 'Mapa de risco', icon: 'map' },
  { key: 'abrigos', label: 'Abrigos', icon: 'shelter' },
  { key: 'plano', label: 'Meu plano', icon: 'checklist' },
  { key: 'notificacoes', label: 'Notificações', icon: 'bell' },
  { key: 'clima', label: 'Clima e rios', icon: 'cloud' },
  { key: 'relatorios', label: 'Relatórios', icon: 'chart' },
]

export function Shell({ page, onNavigate, children, title = 'RS Seguro' }: Props) {
  return <div className="app-shell">
    <aside className="desktop-sidebar">
      <div className="brand"><div className="brand-mark"><Icon name="shield" size={22}/></div><div><strong>RS Seguro</strong><span>Proteção começa com informação</span></div></div>
      <div className="sidebar-demo">● CENÁRIO DEMONSTRATIVO · DADOS NÃO OFICIAIS</div>
      <nav>{items.map(item => <button key={item.key} className={page === item.key ? 'active' : ''} onClick={() => onNavigate(item.key)}><Icon name={item.icon}/><span>{item.label}</span></button>)}</nav>
      <div className="sidebar-bottom"><button onClick={() => onNavigate('configuracoes')}><Icon name="settings"/>Configurações</button><button onClick={() => onNavigate('perfil')}><Icon name="user"/>Meu perfil</button></div>
    </aside>
    <main className="main-area">
      <header className="topbar">
        <div className="mobile-brand"><div className="brand-mark"><Icon name="shield" size={19}/></div><strong>{title}</strong></div>
        <div className="location-select"><Icon name="location" size={17}/> Menino Deus, Porto Alegre <span>⌄</span></div>
        <div className="top-actions"><span className="demo-pill">Ambiente demonstrativo</span><button className="icon-button" onClick={() => onNavigate('notificacoes')}><Icon name="bell"/></button><button className="avatar" onClick={() => onNavigate('perfil')}>AM</button></div>
      </header>
      <div className="mobile-demo">● CENÁRIO DEMONSTRATIVO · DADOS NÃO OFICIAIS</div>
      <section className="content">{children}</section>
      <nav className="mobile-nav">{items.slice(0,5).map(item => <button key={item.key} className={page === item.key ? 'active' : ''} onClick={() => onNavigate(item.key)}><Icon name={item.icon} size={19}/><span>{item.label === 'Mapa de risco' ? 'Mapa' : item.label === 'Meu plano' ? 'Plano' : item.label}</span></button>)}</nav>
    </main>
  </div>
}
