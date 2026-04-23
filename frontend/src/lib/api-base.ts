const STORAGE_KEY = 'matchmaking_api_base'

export function getApiBase(): string {
  if (typeof window !== 'undefined') {
    const fromLs = window.localStorage.getItem(STORAGE_KEY)
    if (fromLs?.trim()) {
      return fromLs.replace(/\/$/, '')
    }
  }
  const fromEnv = import.meta.env.VITE_API_BASE_URL as string | undefined
  return (fromEnv?.trim() ? fromEnv : 'http://localhost:8000').replace(/\/$/, '')
}

export function setApiBase(url: string | null): void {
  if (typeof window === 'undefined') return
  if (!url?.trim()) {
    window.localStorage.removeItem(STORAGE_KEY)
    return
  }
  window.localStorage.setItem(STORAGE_KEY, url.replace(/\/$/, ''))
}
