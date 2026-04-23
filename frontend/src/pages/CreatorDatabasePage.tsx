import { Database } from 'lucide-react'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export function CreatorDatabasePage() {
  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Creator database</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Browse and manage creators once a dedicated API is wired to Pinecone or your warehouse.
        </p>
      </div>
      <Card className="border-dashed">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Database className="size-5 text-muted-foreground" />
            <CardTitle className="text-lg">Coming soon</CardTitle>
          </div>
          <CardDescription>
            This view will surface filters, saved lists, and enrichment from the matchmaking
            engine. For now, creators flow through each campaign run on the dashboard.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Tip: seed demo vectors with{' '}
            <code className="rounded bg-muted px-1 py-0.5 text-xs">
              backend/scripts/seed_pinecone.py
            </code>{' '}
            so the agent returns richer cards locally.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
