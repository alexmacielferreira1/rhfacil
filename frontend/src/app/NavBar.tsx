import { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'

import { logout } from '../features/auth/auth-api'

function hasSessionCookie() {
  return document.cookie.split('; ').some((entry) => entry.startsWith('saas_csrf='))
}

export function NavBar() {
  const navigate = useNavigate()
  const [signedIn, setSignedIn] = useState(hasSessionCookie)

  async function signOut() {
    try {
      await logout()
    } finally {
      setSignedIn(false)
      navigate('/login')
    }
  }

  return (
    <header className="topnav">
      <span className="topnav-brand">Gestão de Funcionários</span>
      <nav aria-label="Navegação principal">
        <NavLink to="/">Início</NavLink>
        <NavLink to="/people/employees">Colaboradores</NavLink>
      </nav>
      {signedIn ? (
        <button type="button" className="secondary" onClick={() => void signOut()}>Sair</button>
      ) : (
        <NavLink to="/login" className="topnav-login">Entrar</NavLink>
      )}
    </header>
  )
}
