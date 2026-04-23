import { cn } from '@/lib/utils'
import type { SafetyLevel } from '@/lib/safety-status'

const LABEL: Record<SafetyLevel, string> = {
  green: 'Passed',
  yellow: 'In review',
  red: 'Blocked',
}

export function SafetyIndicator({
  level,
  className,
}: {
  level: SafetyLevel
  className?: string
}) {
  const color =
    level === 'green'
      ? 'bg-emerald-500'
      : level === 'red'
        ? 'bg-destructive'
        : 'bg-amber-500'

  return (
    <div
      className={cn('flex items-center gap-2 text-sm', className)}
      role="status"
    >
      <span className={cn('size-2.5 rounded-full', color)} aria-hidden />
      <span className="font-medium text-foreground">Safety</span>
      <span className="text-muted-foreground">{LABEL[level]}</span>
    </div>
  )
}
