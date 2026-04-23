import { motion } from 'framer-motion'

import { CreatorAvatar } from '@/components/atoms/creator-avatar'
import { PlatformBadges } from '@/components/atoms/platform-badges'
import { ScoreRing } from '@/components/atoms/score-ring'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card'
import type { CandidateListItem } from '@/types/campaign'
import { cn } from '@/lib/utils'

function vibeScore(c: CandidateListItem): number {
  const sim = c.similarity_score
  if (typeof sim === 'number' && !Number.isNaN(sim)) {
    return Math.min(100, Math.max(0, sim * 100))
  }
  const q = c._engagement_audit?.engagement_quality_score
  if (typeof q === 'number') {
    return Math.min(100, Math.max(0, (q / 10) * 100))
  }
  return 55
}

function auditTags(c: CandidateListItem): string[] {
  const a = c._engagement_audit
  if (!a) {
    return ['Pending audit', 'Audience Alignment', 'Safe Content']
  }
  const authenticity =
    a.fake_follower_risk === 'low' ? 'High Authenticity' : 'Authenticity review'
  const safe =
    a.recommendation === 'proceed'
      ? 'Safe Content'
      : a.recommendation === 'exclude'
        ? 'Flagged'
        : 'Review carefully'
  return [authenticity, 'Audience Alignment', safe]
}

interface CreatorCardProps {
  candidate: CandidateListItem
  index: number
  sent: boolean
  onReview: () => void
}

export function CreatorCard({ candidate, index, sent, onReview }: CreatorCardProps) {
  const score = vibeScore(candidate)
  const tags = auditTags(candidate)

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05, duration: 0.25 }}
    >
      <Card
        className={cn(
          'h-full overflow-hidden border-border/80 transition-shadow hover:shadow-md',
          sent && 'opacity-80 ring-1 ring-primary/30',
        )}
      >
        <CardHeader className="flex flex-row items-start gap-3 pb-2">
          <CreatorAvatar handle={candidate.handle} size={52} />
          <div className="min-w-0 flex-1 space-y-1">
            <p className="truncate font-medium text-foreground">{candidate.handle}</p>
            <p className="line-clamp-2 text-xs text-muted-foreground">{candidate.niche}</p>
            <PlatformBadges niche={candidate.niche} />
          </div>
          <ScoreRing value={score} />
        </CardHeader>
        <CardContent className="pb-3">
          <p className="mb-2 text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
            Vibe match
          </p>
          <div className="flex flex-wrap gap-1">
            {tags.map((t) => (
              <Badge key={t} variant="outline" className="text-[10px] font-normal">
                {t}
              </Badge>
            ))}
          </div>
        </CardContent>
        <CardFooter className="border-t border-border/60 bg-muted/20 pt-3">
          <Button
            type="button"
            variant={sent ? 'secondary' : 'default'}
            className="w-full"
            onClick={onReview}
            disabled={sent}
          >
            {sent ? 'Sent' : 'Review pitch'}
          </Button>
        </CardFooter>
      </Card>
    </motion.div>
  )
}
