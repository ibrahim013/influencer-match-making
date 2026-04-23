const KEY = 'matchmaking_campaign_threads'

export interface StoredThread {
  threadId: string
  snippet: string
  createdAt: number
}

export function listStoredThreads(): StoredThread[] {
  if (typeof window === 'undefined') return []
  try {
    const raw = window.localStorage.getItem(KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw) as unknown
    if (!Array.isArray(parsed)) return []
    return parsed.filter(
      (x): x is StoredThread =>
        typeof x === 'object' &&
        x !== null &&
        typeof (x as StoredThread).threadId === 'string' &&
        typeof (x as StoredThread).snippet === 'string' &&
        typeof (x as StoredThread).createdAt === 'number',
    )
  } catch {
    return []
  }
}

export function upsertStoredThread(entry: StoredThread): void {
  if (typeof window === 'undefined') return
  const prev = listStoredThreads()
  const next = [entry, ...prev.filter((t) => t.threadId !== entry.threadId)].slice(0, 50)
  window.localStorage.setItem(KEY, JSON.stringify(next))
}
