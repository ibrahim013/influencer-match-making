import { Loader2 } from 'lucide-react'
import { useState } from 'react'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'

function buildBrandContext(brandUrl: string, objective: string): string {
  const u = brandUrl.trim()
  const o = objective.trim()
  return [
    u ? `Brand URL:\n${u}` : null,
    o ? `Campaign objective:\n${o}` : null,
  ]
    .filter(Boolean)
    .join('\n\n')
}

export function BrandInputCard({
  onSubmit,
  disabled,
}: {
  onSubmit: (brandContext: string) => void
  disabled?: boolean
}) {
  const [brandUrl, setBrandUrl] = useState('')
  const [objective, setObjective] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const ctx = buildBrandContext(brandUrl, objective)
    if (ctx.length < 10) return
    onSubmit(ctx)
  }

  const tooShort = buildBrandContext(brandUrl, objective).length < 10

  return (
    <Card className="border-border/80 shadow-sm">
      <CardHeader>
        <CardTitle className="text-lg">Brand brief</CardTitle>
        <CardDescription>
          Paste your site and objective. We bundle them into one brief for the matchmaking agent.
        </CardDescription>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="brand-url">Brand URL</Label>
            <Input
              id="brand-url"
              type="url"
              placeholder="https://yourbrand.com"
              value={brandUrl}
              onChange={(e) => setBrandUrl(e.target.value)}
              disabled={disabled}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="objective">Campaign objective</Label>
            <Textarea
              id="objective"
              placeholder="e.g. US parents, organic snacks, Q4 awareness…"
              value={objective}
              onChange={(e) => setObjective(e.target.value)}
              disabled={disabled}
              rows={4}
              className="resize-y min-h-[100px]"
            />
          </div>
        </CardContent>
        <CardFooter className="justify-end gap-2 border-t border-border/60 bg-muted/20">
          <Button type="submit" disabled={disabled || tooShort}>
            {disabled ? (
              <>
                <Loader2 className="size-4 animate-spin" />
                Starting…
              </>
            ) : (
              'Run agent'
            )}
          </Button>
        </CardFooter>
      </form>
    </Card>
  )
}
