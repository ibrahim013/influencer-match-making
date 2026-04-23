import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'

import { Button } from '@/components/ui/button'
import { listStoredThreads } from '@/lib/campaign-storage'

export function CampaignsPage() {
  const { data: threads = [] } = useQuery({
    queryKey: ['stored-threads'],
    queryFn: () => listStoredThreads(),
    staleTime: 30_000,
  })

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Campaigns</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Recent runs are stored in this browser until a list API exists.
        </p>
      </div>

      {threads.length === 0 ? (
        <div className="rounded-xl border border-dashed border-border bg-muted/30 px-6 py-14 text-center">
          <p className="text-sm text-muted-foreground">
            No saved threads yet. Start a campaign from the dashboard.
          </p>
          <Button className="mt-4" asChild>
            <Link to="/dashboard">Go to dashboard</Link>
          </Button>
        </div>
      ) : (
        <ul className="space-y-2">
          {threads.map((t) => (
            <li
              key={t.threadId}
              className="flex flex-col gap-2 rounded-xl border border-border/80 bg-card p-4 shadow-sm sm:flex-row sm:items-center sm:justify-between"
            >
              <div className="min-w-0">
                <p className="truncate text-sm font-medium text-foreground">{t.snippet}</p>
                <p className="text-xs text-muted-foreground">
                  {new Date(t.createdAt).toLocaleString()} ·{' '}
                  <code className="text-[11px]">{t.threadId.slice(0, 8)}…</code>
                </p>
              </div>
              <Button size="sm" variant="secondary" asChild>
                <Link to={`/dashboard?thread=${encodeURIComponent(t.threadId)}`}>
                  Open
                </Link>
              </Button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
