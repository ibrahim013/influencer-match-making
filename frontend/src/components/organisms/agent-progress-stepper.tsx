import { motion } from 'framer-motion'
import { Check } from 'lucide-react'

import {
  deriveActiveStep,
  STEP_LABELS,
  STEP_ORDER,
  type ProgressStepId,
} from '@/lib/agent-progress'
import type { StateSnapshotEvent } from '@/types/campaign'
import { cn } from '@/lib/utils'

export function AgentProgressStepper({
  snapshot,
  done,
}: {
  snapshot: StateSnapshotEvent | null
  done: boolean
}) {
  const active = deriveActiveStep(snapshot)
  const activeIndex = STEP_ORDER.indexOf(active)

  const stepComplete = (_id: ProgressStepId, index: number): boolean => {
    if (done && snapshot?.values.outreach_draft && !snapshot.values.refusal_reason) {
      return true
    }
    return index < activeIndex
  }

  const stepCurrent = (id: ProgressStepId, index: number): boolean => {
    return id === active && !stepComplete(id, index)
  }

  return (
    <nav
      aria-label="Agent progress"
      className="mb-6 rounded-xl border border-border/80 bg-card px-3 py-3 shadow-sm sm:px-4"
    >
      <ol className="flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-center sm:gap-1">
        {STEP_ORDER.map((id, index) => {
          const complete = stepComplete(id, index)
          const current = stepCurrent(id, index)
          const isLast = index === STEP_ORDER.length - 1

          return (
            <li key={id} className="flex items-center gap-1 sm:contents">
              <div className="flex min-w-0 items-center gap-2 sm:shrink-0">
                <motion.span
                  layout
                  className={cn(
                    'flex size-7 shrink-0 items-center justify-center rounded-full border text-xs font-medium',
                    complete &&
                      'border-primary/40 bg-primary/10 text-primary',
                    current &&
                      'border-primary bg-primary text-primary-foreground shadow-sm',
                    !complete &&
                      !current &&
                      'border-muted bg-muted/50 text-muted-foreground',
                  )}
                  animate={
                    current
                      ? { scale: [1, 1.04, 1] }
                      : { scale: 1 }
                  }
                  transition={{
                    repeat: current ? Infinity : 0,
                    duration: 2.2,
                    ease: 'easeInOut',
                  }}
                >
                  {complete ? <Check className="size-3.5" /> : index + 1}
                </motion.span>
                <span
                  className={cn(
                    'truncate text-xs font-medium sm:max-w-[7.5rem]',
                    current && 'text-foreground',
                    complete && 'text-primary',
                    !current && !complete && 'text-muted-foreground',
                  )}
                >
                  {STEP_LABELS[id]}
                </span>
              </div>
              {!isLast && (
                <span
                  className="mx-1 hidden text-muted-foreground sm:inline"
                  aria-hidden
                >
                  →
                </span>
              )}
            </li>
          )
        })}
      </ol>
    </nav>
  )
}
