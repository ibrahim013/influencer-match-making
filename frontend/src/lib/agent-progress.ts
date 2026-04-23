import type { StateSnapshotEvent } from '@/types/campaign'

export type ProgressStepId =
  | 'brand_analysis'
  | 'market_search'
  | 'quality_audit'
  | 'human_review'

export const STEP_LABELS: Record<ProgressStepId, string> = {
  brand_analysis: 'Brand Analysis',
  market_search: 'Market Search',
  quality_audit: 'Quality Audit',
  human_review: 'Human Review',
}

export const STEP_ORDER: ProgressStepId[] = [
  'brand_analysis',
  'market_search',
  'quality_audit',
  'human_review',
]

export function deriveActiveStep(snapshot: StateSnapshotEvent | null): ProgressStepId {
  if (!snapshot) return 'brand_analysis'

  const { values, next } = snapshot
  const logs = values.logs ?? []
  const candidates = values.candidate_list ?? []
  const hasAudit =
    candidates.length > 0 &&
    candidates.some((c) => c._engagement_audit !== undefined)

  const waitingHuman = next.includes('writer_node')
  const postApprove = values.is_approved

  if (waitingHuman || postApprove) {
    return 'human_review'
  }
  if (hasAudit) {
    return 'quality_audit'
  }
  if (
    candidates.length > 0 ||
    logs.some((l) => l.includes('Researcher:')) ||
    logs.some((l) => l.includes('Pinecone'))
  ) {
    return 'market_search'
  }
  return 'brand_analysis'
}
