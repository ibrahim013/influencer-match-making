export interface OutreachDraft {
  subject: string
  body: string
  cta: string
  referenced_metadata: string
}

export function parseOutreachDraft(raw: string | null | undefined): OutreachDraft | null {
  if (!raw?.trim()) return null
  try {
    const o = JSON.parse(raw) as OutreachDraft
    if (
      typeof o.subject === 'string' &&
      typeof o.body === 'string' &&
      typeof o.cta === 'string' &&
      typeof o.referenced_metadata === 'string'
    ) {
      return o
    }
    return null
  } catch {
    return null
  }
}

export function formatDraftForEditing(d: OutreachDraft): string {
  return `Subject: ${d.subject}\n\n${d.body}\n\nCTA: ${d.cta}\n\nReferenced: ${d.referenced_metadata}`
}
