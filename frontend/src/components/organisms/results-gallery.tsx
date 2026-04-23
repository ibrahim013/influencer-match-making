import { CreatorCard } from '@/components/molecules/creator-card'
import { Skeleton } from '@/components/ui/skeleton'
import type { CandidateListItem } from '@/types/campaign'

function CardSkeleton() {
  return (
    <div className="rounded-xl border border-border/80 bg-card p-4 shadow-sm">
      <div className="flex gap-3">
        <Skeleton className="size-[52px] rounded-full" />
        <div className="flex-1 space-y-2">
          <Skeleton className="h-4 w-28" />
          <Skeleton className="h-3 w-full" />
          <div className="flex gap-1">
            <Skeleton className="h-5 w-14 rounded-md" />
            <Skeleton className="h-5 w-16 rounded-md" />
          </div>
        </div>
        <Skeleton className="size-14 rounded-full" />
      </div>
      <div className="mt-4 space-y-2">
        <Skeleton className="h-3 w-20" />
        <div className="flex flex-wrap gap-1">
          <Skeleton className="h-5 w-24 rounded-md" />
          <Skeleton className="h-5 w-28 rounded-md" />
        </div>
      </div>
      <Skeleton className="mt-4 h-9 w-full rounded-lg" />
    </div>
  )
}

export function ResultsGallery({
  candidates,
  loading,
  sentIds,
  onReview,
}: {
  candidates: CandidateListItem[]
  loading: boolean
  sentIds: Set<string>
  onReview: (c: CandidateListItem) => void
}) {
  if (loading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <CardSkeleton key={i} />
        ))}
      </div>
    )
  }

  if (candidates.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-border bg-muted/30 px-6 py-16 text-center text-sm text-muted-foreground">
        No creators yet. Run the agent with a brief to populate matches from the engine.
      </div>
    )
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {candidates.map((c, i) => (
        <CreatorCard
          key={c.creator_id}
          candidate={c}
          index={i}
          sent={sentIds.has(c.creator_id)}
          onReview={() => onReview(c)}
        />
      ))}
    </div>
  )
}
