import { AnimatePresence, motion } from 'framer-motion'
import { ChevronDown, ChevronUp, PanelRight, Sparkles } from 'lucide-react'
import { useState } from 'react'

import { AgentLogLine } from '@/components/molecules/agent-log-line'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet'
import { useIsMobile } from '@/hooks/use-is-mobile'
import { cn } from '@/lib/utils'

interface AgentTerminalProps {
  logs: string[]
  thinking?: boolean
}

export function AgentTerminal({ logs, thinking }: AgentTerminalProps) {
  const isMobile = useIsMobile()
  const [desktopOpen, setDesktopOpen] = useState(true)
  const [mobileOpen, setMobileOpen] = useState(false)

  const logContent = (
    <ScrollArea className={cn(isMobile ? 'h-[50vh]' : 'h-[calc(100vh-8rem)]')}>
      <ul className="space-y-1.5 pr-3 pb-4">
        <AnimatePresence initial={false}>
          {logs.map((line, i) => (
            <AgentLogLine key={`${i}-${line.slice(0, 24)}`} line={line} index={i} />
          ))}
        </AnimatePresence>
        {thinking && (
          <motion.li
            key="thinking"
            initial={{ opacity: 0 }}
            animate={{ opacity: [0.4, 1, 0.4] }}
            transition={{ repeat: Infinity, duration: 1.6 }}
            className="flex items-center gap-2 rounded-md border border-dashed border-primary/40 bg-primary/5 px-2 py-2 text-xs text-primary"
          >
            <Sparkles className="size-3.5 shrink-0" />
            Agent thinking…
          </motion.li>
        )}
      </ul>
    </ScrollArea>
  )

  const header = (
    <div className="flex items-center justify-between gap-2 border-b border-border/80 px-3 py-2">
      <div className="flex items-center gap-2">
        <Sparkles className="size-4 text-primary" />
        <span className="text-sm font-semibold">Agent terminal</span>
      </div>
      {!isMobile && (
        <Button
          type="button"
          variant="ghost"
          size="icon-sm"
          onClick={() => setDesktopOpen((o) => !o)}
          aria-expanded={desktopOpen}
          aria-label={desktopOpen ? 'Collapse agent panel' : 'Expand agent panel'}
        >
          {desktopOpen ? <ChevronDown /> : <PanelRight />}
        </Button>
      )}
    </div>
  )

  if (isMobile) {
    return (
      <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
        <SheetTrigger asChild>
          <Button
            type="button"
            variant="secondary"
            className="fixed bottom-4 right-4 z-40 shadow-lg"
            size="sm"
          >
            <Sparkles className="size-4" />
            Agent logs
          </Button>
        </SheetTrigger>
        <SheetContent side="bottom" className="h-[60vh] gap-0 p-0">
          <SheetHeader className="border-b border-border/80 p-3 text-left">
            <SheetTitle className="flex items-center gap-2">
              <Sparkles className="size-4 text-primary" />
              Live agent logs
            </SheetTitle>
          </SheetHeader>
          <div className="p-3">{logContent}</div>
        </SheetContent>
      </Sheet>
    )
  }

  return (
    <aside
      className={cn(
        'shrink-0 border-l border-border/80 bg-sidebar transition-[width] duration-200 ease-out',
        desktopOpen ? 'w-[min(22rem,100%)]' : 'w-12',
      )}
    >
      {desktopOpen ? (
        <div className="flex h-full min-h-0 flex-col">
          {header}
          <div className="min-h-0 flex-1 px-2 pt-2">{logContent}</div>
        </div>
      ) : (
        <div className="flex h-full flex-col items-center py-3">
          <Button
            type="button"
            variant="ghost"
            size="icon-sm"
            onClick={() => setDesktopOpen(true)}
            aria-label="Expand agent panel"
          >
            <ChevronUp />
          </Button>
        </div>
      )}
    </aside>
  )
}
