import { getApiBase } from '@/lib/api-base'

export async function startCampaign(brandContext: string): Promise<{ thread_id: string }> {
  const res = await fetch(`${getApiBase()}/campaign/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ brand_context: brandContext }),
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `Start failed (${res.status})`)
  }
  return res.json() as Promise<{ thread_id: string }>
}

export async function approveCampaign(
  threadId: string,
  selectedCandidateId: string,
): Promise<{ status: string }> {
  const res = await fetch(
    `${getApiBase()}/campaign/${encodeURIComponent(threadId)}/approve`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ selected_candidate_id: selectedCandidateId }),
    },
  )
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `Approve failed (${res.status})`)
  }
  return res.json() as Promise<{ status: string }>
}
