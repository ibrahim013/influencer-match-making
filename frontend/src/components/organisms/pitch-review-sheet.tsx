import { Loader2 } from 'lucide-react'
import { useMemo } from 'react'

import { SafetyIndicator } from '@/components/atoms/safety-indicator'
import { Button } from '@/components/ui/button'
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet'
import { Textarea } from '@/components/ui/textarea'
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import { formatDraftForEditing, parseOutreachDraft } from '@/lib/outreach'
import { deriveSafetyStatus } from '@/lib/safety-status'
import type { CandidateListItem, StateSnapshotEvent } from '@/types/campaign'

interface PitchReviewSheetProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  candidate: CandidateListItem | null
  snapshot: StateSnapshotEvent | null
  streamDone: boolean
  onApprove: (creatorId: string) => void
  approvePending: boolean
}

export function PitchReviewSheet({
  open,
  onOpenChange,
  candidate,
  snapshot,
  streamDone,
  onApprove,
  approvePending,
}: PitchReviewSheetProps) {
  const rawDraft = snapshot?.values.outreach_draft ?? null
  const parsed = useMemo(() => parseOutreachDraft(rawDraft), [rawDraft])
  const draftDefaults = useMemo(
    () => (parsed ? formatDraftForEditing(parsed) : ''),
    [parsed],
  )

  const safety = deriveSafetyStatus(snapshot, streamDone)
  const waitingOnDraft =
    snapshot?.values.is_approved &&
    !parsed &&
    !streamDone &&
    (snapshot?.next?.length ?? 0) > 0

  if (!candidate) return null

  const audit = candidate._engagement_audit

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent
        side="right"
        className="flex w-full flex-col gap-0 overflow-y-auto sm:max-w-lg"
      >
        <SheetHeader className="border-b border-border/80 pb-4 text-left">
          <SheetTitle>Review pitch</SheetTitle>
          <SheetDescription>
            {parsed
              ? 'Edit copy locally if needed. Sending uses the server-generated draft from the graph.'
              : 'Approve to let the writer node generate outreach, then guardrails validate outbound copy.'}
          </SheetDescription>
        </SheetHeader>

        <div className="flex flex-1 flex-col gap-4 px-4 py-4">
          <div>
            <p className="text-sm font-medium text-foreground">{candidate.handle}</p>
            <p className="text-xs text-muted-foreground">{candidate.niche}</p>
          </div>

          {audit && (
            <div className="rounded-lg border border-border/80 bg-muted/30 px-3 py-2 text-xs text-muted-foreground">
              <p>
                <span className="font-medium text-foreground">Engagement: </span>
                {audit.engagement_quality_score}/10 · risk {audit.fake_follower_risk}
              </p>
              <p className="mt-1 line-clamp-3">{audit.brand_alignment_notes}</p>
            </div>
          )}

          <SafetyIndicator level={safety} />

          {waitingOnDraft && (
            <div className="flex items-center gap-2 rounded-lg border border-dashed border-primary/40 bg-primary/5 px-3 py-4 text-sm text-primary">
              <Loader2 className="size-4 shrink-0 animate-spin" />
              Generating pitch and running guardrails…
            </div>
          )}

          {parsed && (
            <div className="space-y-2">
              <label className="text-sm font-medium" htmlFor="pitch-body">
                Pitch
              </label>
              <Textarea
                id="pitch-body"
                key={rawDraft ?? 'draft'}
                defaultValue={draftDefaults}
                rows={14}
                className="font-mono text-xs leading-relaxed"
              />
            </div>
          )}
        </div>

        <SheetFooter className="mt-auto flex-col gap-2 border-t border-border/80 bg-muted/20 px-4 py-4 sm:flex-row sm:justify-end">
          <Tooltip>
            <TooltipTrigger asChild>
              <span className="w-full sm:w-auto sm:mr-auto">
                <Button type="button" variant="outline" className="w-full" disabled>
                  Regenerate
                </Button>
              </span>
            </TooltipTrigger>
            <TooltipContent side="top" className="max-w-xs text-xs">
              The API does not expose manual rewrite yet. Failed guardrails trigger up
              to three automatic writer retries—watch the agent terminal for progress.
            </TooltipContent>
          </Tooltip>
          {!parsed && snapshot?.next?.includes('writer_node') && (
            <Button
              type="button"
              onClick={() => onApprove(candidate.creator_id)}
              disabled={approvePending}
            >
              {approvePending ? (
                <>
                  <Loader2 className="size-4 animate-spin" />
                  Approving…
                </>
              ) : (
                'Approve & send'
              )}
            </Button>
          )}
        </SheetFooter>
      </SheetContent>
    </Sheet>
  )
}
