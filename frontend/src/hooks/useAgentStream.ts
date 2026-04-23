import { useCallback, useEffect, useRef, useState } from 'react'

import { getApiBase } from '@/lib/api-base'
import type { AgentStreamState, StreamEvent } from '@/types/campaign'

function parseEvent(data: string): StreamEvent | null {
  try {
    return JSON.parse(data) as StreamEvent
  } catch {
    return null
  }
}

export function useAgentStream(threadId: string | null) {
  const [state, setState] = useState<AgentStreamState>({
    snapshot: null,
    done: false,
    error: null,
    connected: false,
  })
  const esRef = useRef<EventSource | null>(null)

  const close = useCallback(() => {
    esRef.current?.close()
    esRef.current = null
  }, [])

  useEffect(() => {
    if (!threadId) {
      close()
      const resetId = requestAnimationFrame(() => {
        setState({
          snapshot: null,
          done: false,
          error: null,
          connected: false,
        })
      })
      return () => cancelAnimationFrame(resetId)
    }

    const base = getApiBase()
    const url = `${base}/campaign/${encodeURIComponent(threadId)}/stream`
    const es = new EventSource(url)
    esRef.current = es

    const initId = requestAnimationFrame(() => {
      setState({
        snapshot: null,
        done: false,
        error: null,
        connected: false,
      })
    })

    es.onopen = () => {
      setState((s) => ({ ...s, connected: true }))
    }

    es.onmessage = (ev) => {
      const msg = parseEvent(ev.data)
      if (!msg) return
      if (msg.type === 'error') {
        setState((s) => ({ ...s, error: msg.detail, done: true }))
        es.close()
        return
      }
      if (msg.type === 'done') {
        setState((s) => ({ ...s, done: true }))
        es.close()
        return
      }
      if (msg.type === 'state_snapshot') {
        setState((s) => ({ ...s, snapshot: msg, error: null }))
      }
    }

    es.onerror = () => {
      if (es.readyState === EventSource.CLOSED) {
        return
      }
      setState((s) => ({
        ...s,
        error: s.error ?? 'Stream connection error',
        connected: false,
      }))
      es.close()
    }

    return () => {
      cancelAnimationFrame(initId)
      es.close()
      esRef.current = null
    }
  }, [threadId, close])

  return { ...state, closeStream: close }
}
