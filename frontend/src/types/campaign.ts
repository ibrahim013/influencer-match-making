export interface EngagementAudit {
  creator_id: string
  engagement_quality_score: number
  fake_follower_risk: 'low' | 'medium' | 'high'
  brand_alignment_notes: string
  recommendation: 'proceed' | 'review_carefully' | 'exclude'
}

export interface CandidateListItem {
  creator_id: string
  handle: string
  niche: string
  follower_count: number
  avg_engagement_rate: number
  recent_post_topics: string
  audience_geo: string
  similarity_score?: number | null
  _engagement_audit?: EngagementAudit
}

export interface CampaignValues {
  brand_context: string
  candidate_list: CandidateListItem[]
  selected_candidate_id: string | null
  outreach_draft: string | null
  is_approved: boolean
  logs: string[]
  refusal_reason?: string | null
  retry_count?: number
}

export interface StateSnapshotEvent {
  type: 'state_snapshot'
  thread_id: string
  next: string[]
  values: CampaignValues
}

export interface DoneEvent {
  type: 'done'
  thread_id: string
}

export interface ErrorEvent {
  type: 'error'
  detail: string
}

export type StreamEvent = StateSnapshotEvent | DoneEvent | ErrorEvent

export interface AgentStreamState {
  snapshot: StateSnapshotEvent | null
  done: boolean
  error: string | null
  connected: boolean
}
