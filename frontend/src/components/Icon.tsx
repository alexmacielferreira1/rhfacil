import type { CSSProperties } from 'react'

type Props = { name: string; size?: number; stroke?: number; className?: string; style?: CSSProperties }

const paths: Record<string, React.ReactNode> = {
  home: <><path d="m3 10 9-7 9 7"/><path d="M5 9v11h14V9"/><path d="M9 20v-6h6v6"/></>,
  map: <><path d="M9 18 3 21V6l6-3 6 3 6-3v15l-6 3-6-3Z"/><path d="M9 3v15M15 6v15"/></>,
  shield: <><path d="M12 3 20 6v6c0 5-3.4 8.3-8 10-4.6-1.7-8-5-8-10V6l8-3Z"/><path d="m8.5 12 2.2 2.2 4.8-5"/></>,
  bell: <><path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9"/><path d="M10 21h4"/></>,
  user: <><circle cx="12" cy="8" r="4"/><path d="M4 21c.8-4.2 3.4-6 8-6s7.2 1.8 8 6"/></>,
  alert: <><path d="m12 3 9 17H3L12 3Z"/><path d="M12 9v5M12 17h.01"/></>,
  location: <><path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/></>,
  shelter: <><path d="m3 11 9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M9 20v-5h6v5"/><path d="M7 12h10"/></>,
  checklist: <><rect x="5" y="3" width="14" height="18" rx="2"/><path d="M9 8h6M9 12h6M9 16h4"/></>,
  cloud: <><path d="M7 18h10a4 4 0 0 0 .7-7.9A6 6 0 0 0 6.2 8.8 4.6 4.6 0 0 0 7 18Z"/><path d="M9 21h.01M13 21h.01M17 21h.01"/></>,
  rain: <><path d="M7 16h10a4 4 0 0 0 .7-7.9A6 6 0 0 0 6.2 6.8 4.6 4.6 0 0 0 7 16Z"/><path d="m8 19-1 2m5-2-1 2m5-2-1 2"/></>,
  chart: <><path d="M4 19V5M4 19h16"/><path d="m7 15 3-4 3 2 5-7"/></>,
  settings: <><path d="M12 15.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Z"/><path d="m19.4 15 .1.1-1.7 3-1.4-.6a8 8 0 0 1-2 .9l-.2 1.5h-3.4l-.2-1.5a8 8 0 0 1-2-.9l-1.4.6-1.7-3 .1-.1a7 7 0 0 1-.8-2l-1.5-.2V9.4l1.5-.2a7 7 0 0 1 .8-2l-.1-.1 1.7-3 1.4.6a8 8 0 0 1 2-.9L10.8 2h3.4l.2 1.5a8 8 0 0 1 2 .9l1.4-.6 1.7 3-.1.1a7 7 0 0 1 .8 2l1.5.2v3.4l-1.5.2a7 7 0 0 1-.8 2Z"/></>,
  info: <><circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/></>,
  route: <><circle cx="6" cy="18" r="2"/><circle cx="18" cy="6" r="2"/><path d="M8 18c7 0 1-8 8-12"/></>,
  phone: <><path d="M7 4h3l1 4-2 1c1 2 2 3 4 4l1-2 4 1v3c0 1-1 2-2 2-7 0-12-5-12-12 0-1 1-2 2-2Z"/></>,
}

export function Icon({ name, size = 20, stroke = 1.8, className = '', style }: Props) {
  return <svg className={`icon ${className}`} style={style} width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name] ?? paths.info}</svg>
}
