import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useCallback, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'

import { AgentProgressStepper } from '@/components/organisms/agent-progress-stepper'
import { AgentTerminal } from '@/components/organisms/agent-terminal'
import { BrandInputCard } from '@/components/organisms/brand-input-card'
import { PitchReviewSheet } from '@/components/organisms/pitch-review-sheet'
import { ResultsGallery } from '@/components/organisms/results-gallery'
import { useAgentStream } from '@/hooks/useAgentStream'
import { upsertStoredThread } from '@/lib/campaign-storage'
import { approveCampaign, startCampaign } from '@/lib/campaigns-api'
import type { CandidateListItem } from '@/types/campaign'

export function DashboardPage() {
  const queryClient = useQueryClient()
  const [searchParams, setSearchParams] = useSearchParams()
  const threadId = searchParams.get('thread')

  const [sheetOpen, setSheetOpen] = useState(false)
  const [activeCreator, setActiveCreator] = useState<CandidateListItem | null>(null)
  const [optimisticSent, setOptimisticSent] = useState<Set<string>>(() => new Set())

  const { snapshot, done, error, closeStream } = useAgentStream(threadId)

  const candidates = snapshot?.values.candidate_list ?? []
  const logs = snapshot?.values.logs ?? []

  const startMutation = useMutation({
    mutationFn: startCampaign,
    onSuccess: (data, brandContext) => {
      closeStream()
      setOptimisticSent(new Set())
      const snippet = brandContext.slice(0, 120)
      upsertStoredThread({
        threadId: data.thread_id,
        snippet,
        createdAt: Date.now(),
      })
      setSearchParams({ thread: data.thread_id })
      void queryClient.invalidateQueries({ queryKey: ['stored-threads'] })
    },
  })

  const approveMutation = useMutation({
    mutationFn: ({
      tid,
      cid,
    }: {
      tid: string
      cid: string
    }) => approveCampaign(tid, cid),
    onSuccess: (_, { cid }) => {
      setOptimisticSent((prev) => new Set(prev).add(cid))
    },
    onError: (_, { cid }) => {
      setOptimisticSent((prev) => {
        const next = new Set(prev)
        next.delete(cid)
        return next
      })
    },
  })

  const handleStart = useCallback(
    (brandContext: string) => {
      startMutation.mutate(brandContext)
    },
    [startMutation],
  )

  const handleReview = useCallback((c: CandidateListItem) => {
    setActiveCreator(c)
    setSheetOpen(true)
  }, [])

  const handleApprove = useCallback(
    (creatorId: string) => {
      if (!threadId) return
      approveMutation.mutate({ tid: threadId, cid: creatorId })
    },
    [threadId, approveMutation],
  )

  const galleryLoading = useMemo(() => {
    if (startMutation.isPending) return true
    if (!threadId) return false
    if (!snapshot && !done && !error) return true
    return false
  }, [startMutation.isPending, threadId, snapshot, done, error])

  const thinking = useMemo(() => {
    if (startMutation.isPending) return true
    if (!threadId || error) return false
    const v = snapshot?.values
    if (v?.is_approved && !v.outreach_draft && !done) return true
    return false
  }, [startMutation.isPending, threadId, error, snapshot, done])

  return (
    <div className="mx-auto flex max-w-[1600px] min-h-0 flex-1 flex-col gap-6 lg:flex-row">
      <div className="min-w-0 flex-1 space-y-6 pb-24 lg:pb-6">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">
            Dashboard
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Run semantic search, audits, and human-in-the-loop approval against your live graph.
          </p>
        </div>

        {error && (
          <div
            className="rounded-lg border border-destructive/40 bg-destructive/10 px-4 py-3 text-sm text-destructive"
            role="alert"
          >
            {error}
          </div>
        )}

        <AgentProgressStepper snapshot={snapshot} done={done} />

        <BrandInputCard
          onSubmit={handleStart}
          disabled={startMutation.isPending}
        />

        <section>
          <h2 className="mb-3 text-sm font-semibold text-foreground">Results gallery</h2>
          <ResultsGallery
            candidates={candidates}
            loading={!!galleryLoading}
            sentIds={optimisticSent}
            onReview={handleReview}
          />
        </section>
      </div>

      <AgentTerminal logs={logs} thinking={thinking} />

      <PitchReviewSheet
        open={sheetOpen}
        onOpenChange={(o) => {
          setSheetOpen(o)
          if (!o) setActiveCreator(null)
        }}
        candidate={activeCreator}
        snapshot={snapshot}
        streamDone={done}
        onApprove={handleApprove}
        approvePending={approveMutation.isPending}
      />
    </div>
  )
}
