const API_TIMEOUT_MS = 8_000

export class ApiError extends Error {
  constructor(readonly status: number) {
    super('Não foi possível concluir a comunicação com o serviço.')
  }
}

export async function apiGet<T>(path: string): Promise<T> {
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), API_TIMEOUT_MS)
  try {
    const response = await fetch(path, {
      credentials: 'include',
      headers: { Accept: 'application/json' },
      signal: controller.signal,
    })
    if (!response.ok) throw new ApiError(response.status)
    return (await response.json()) as T
  } finally {
    window.clearTimeout(timeout)
  }
}

function readCookie(name: string) {
  const prefix = `${name}=`
  return document.cookie.split('; ').find((value) => value.startsWith(prefix))?.slice(prefix.length)
}

export async function apiSend<T>(
  path: string,
  method: 'POST' | 'PATCH',
  payload: object,
): Promise<T> {
  const headers: Record<string, string> = {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  }
  const csrf = readCookie('saas_csrf')
  if (csrf) headers['X-CSRF-Token'] = decodeURIComponent(csrf)
  const response = await fetch(path, {
    method,
    credentials: 'include',
    headers,
    body: JSON.stringify(payload),
  })
  if (!response.ok) throw new ApiError(response.status)
  return (await response.json()) as T
}

export async function apiUpload<T>(path: string, file: File): Promise<T> {
  const headers: Record<string, string> = { Accept: 'application/json' }
  const csrf = readCookie('saas_csrf')
  if (csrf) headers['X-CSRF-Token'] = decodeURIComponent(csrf)
  const body = new FormData()
  body.append('file', file)
  const response = await fetch(path, { method: 'POST', credentials: 'include', headers, body })
  if (!response.ok) throw new ApiError(response.status)
  return (await response.json()) as T
}
