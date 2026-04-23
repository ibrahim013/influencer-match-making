import type { StateSnapshotEvent } from '@/types/campaign'

export type SafetyLevel = 'green' | 'yellow' | 'red'

export function deriveSafetyStatus(
  snapshot: StateSnapshotEvent | null,
  done: boolean,
): SafetyLevel {
  if (!snapshot) return 'yellow'

  const { values, next } = snapshot
  const refusal = values.refusal_reason
  const draft = values.outreach_draft
  const retries = values.retry_count ?? 0

  if (done && draft && !refusal) {
    return 'green'
  }

  if (refusal) {
    if (done && retries >= 3) {
      return 'red'
    }
    return 'yellow'
  }

  if (values.is_approved && next.length > 0) {
    return 'yellow'
  }

  if (draft && !done) {
    return 'yellow'
  }

  return 'yellow'
}
