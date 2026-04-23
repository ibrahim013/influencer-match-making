import { Badge } from '@/components/ui/badge'
import { inferPlatforms } from '@/lib/infer-platforms'
import { cn } from '@/lib/utils'

export function PlatformBadges({
  niche,
  className,
}: {
  niche: string
  className?: string
}) {
  const platforms = inferPlatforms(niche)
  return (
    <div className={cn('flex flex-wrap gap-1', className)}>
      {platforms.map((p) => (
        <Badge key={p} variant="secondary" className="text-[10px] font-normal">
          {p}
        </Badge>
      ))}
    </div>
  )
}
