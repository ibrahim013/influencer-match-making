import { motion } from 'framer-motion'

import { cn } from '@/lib/utils'

export function AgentLogLine({
  line,
  index,
}: {
  line: string
  index: number
}) {
  return (
    <motion.li
      layout
      initial={{ opacity: 0, x: -6 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.02, duration: 0.2 }}
      className={cn(
        'rounded-md border border-border/60 bg-muted/40 px-2 py-1.5 font-mono text-[11px] leading-snug text-muted-foreground',
      )}
    >
      {line}
    </motion.li>
  )
}
