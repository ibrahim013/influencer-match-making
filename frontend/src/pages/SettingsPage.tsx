import { useState } from 'react'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { getApiBase, setApiBase } from '@/lib/api-base'

export function SettingsPage() {
  const [baseUrl, setBaseUrl] = useState(() => getApiBase())

  const save = () => {
    const trimmed = baseUrl.trim()
    setApiBase(trimmed || null)
    setBaseUrl(getApiBase())
  }

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Local preferences for this browser session.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">API base URL</CardTitle>
          <CardDescription>
            Overrides <code className="text-xs">VITE_API_BASE_URL</code> for REST and SSE calls.
            Stored in localStorage.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-2">
          <Label htmlFor="api-base">Base URL</Label>
          <Input
            id="api-base"
            type="url"
            placeholder="http://localhost:8000"
            value={baseUrl}
            onChange={(e) => setBaseUrl(e.target.value)}
          />
        </CardContent>
        <CardFooter className="justify-end gap-2">
          <Button type="button" variant="outline" onClick={() => setBaseUrl('http://localhost:8000')}>
            Reset default
          </Button>
          <Button type="button" onClick={save}>
            Save
          </Button>
        </CardFooter>
      </Card>
    </div>
  )
}
