import { cn } from '@/lib/utils'

interface ScoreRingProps {
  value: number
  className?: string
  size?: number
  strokeWidth?: number
}

export function ScoreRing({
  value,
  className,
  size = 56,
  strokeWidth = 4,
}: ScoreRingProps) {
  const pct = Math.min(100, Math.max(0, value))
  const r = (size - strokeWidth) / 2
  const c = 2 * Math.PI * r
  const offset = c - (pct / 100) * c

  return (
    <div
      className={cn('relative shrink-0', className)}
      style={{ width: size, height: size }}
      aria-label={`Match score ${Math.round(pct)} percent`}
    >
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          className="stroke-muted"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          className="stroke-primary transition-[stroke-dashoffset] duration-500 ease-out"
          strokeWidth={strokeWidth}
          strokeDasharray={c}
          strokeDashoffset={offset}
          strokeLinecap="round"
        />
      </svg>
      <span className="absolute inset-0 flex items-center justify-center text-xs font-semibold text-foreground">
        {Math.round(pct)}
      </span>
    </div>
  )
}
