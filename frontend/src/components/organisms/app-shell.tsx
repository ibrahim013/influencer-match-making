import { Menu } from 'lucide-react'
import { useState } from 'react'
import { Outlet } from 'react-router-dom'

import { AppSidebar } from '@/components/organisms/app-sidebar'
import { Button } from '@/components/ui/button'
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet'
import { useIsMobile } from '@/hooks/use-is-mobile'

export function AppShell() {
  const isMobile = useIsMobile()
  const [navOpen, setNavOpen] = useState(false)

  return (
    <div className="flex min-h-svh w-full bg-background">
      {!isMobile && (
        <aside className="hidden w-56 shrink-0 lg:block">
          <AppSidebar />
        </aside>
      )}

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-30 flex h-14 items-center gap-3 border-b border-border/80 bg-background/95 px-4 backdrop-blur supports-backdrop-filter:bg-background/80 lg:hidden">
          <Sheet open={navOpen} onOpenChange={setNavOpen}>
            <SheetTrigger asChild>
              <Button type="button" variant="outline" size="icon-sm" aria-label="Open menu">
                <Menu className="size-4" />
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-64 p-0">
              <SheetHeader className="sr-only">
                <SheetTitle>Navigation</SheetTitle>
              </SheetHeader>
              <AppSidebar onNavigate={() => setNavOpen(false)} />
            </SheetContent>
          </Sheet>
          <span className="text-sm font-semibold text-foreground">Matchmaking</span>
        </header>

        <main className="min-h-0 flex-1 overflow-auto p-4 lg:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
