import { useEffect, useState } from 'react'

import { getTranscript, startTranscription } from '@/services/projects'

type Props = {
  projectId: string | null
  hasAudio: boolean
  onTaskStarted?: (taskId: string) => void
}

export function TranscriptionTrigger({
  projectId,
  hasAudio,
  onTaskStarted,
}: Props): JSX.Element {
  const [isStarting, setIsStarting] = useState(false)
  const [isWaiting, setIsWaiting] = useState(false)
  const [taskId, setTaskId] = useState<string | null>(null)
  const [transcriptReady, setTranscriptReady] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!projectId || !taskId) return

    let canceled = false
    setTranscriptReady(false)
    setIsWaiting(true)

    async function poll(): Promise<void> {
      try {
        await getTranscript(projectId)
        if (canceled) return
        setTranscriptReady(true)
        setIsWaiting(false)
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Unknown error'
        if (canceled) return
        if (message.toLowerCase().includes('transcript not found')) {
          return
        }
        setError(message)
        setIsWaiting(false)
      }
    }

    const id = window.setInterval(() => {
      void poll()
    }, 2000)
    void poll()

    return () => {
      canceled = true
      window.clearInterval(id)
    }
  }, [projectId, taskId])

  async function onStart(): Promise<void> {
    if (!projectId) return

    setError(null)
    setIsStarting(true)
    try {
      const result = await startTranscription(projectId)
      setTaskId(result.task_id)
      onTaskStarted?.(result.task_id)
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to start transcription'
      )
      setTaskId(null)
    } finally {
      setIsStarting(false)
    }
  }

  const disabled = !projectId || !hasAudio || isStarting

  return (
    <div style={{ maxWidth: 640, margin: '24px auto 0' }}>
      <h2>Transcribe</h2>
      <button onClick={onStart} disabled={disabled}>
        {isStarting ? 'Starting…' : 'Generate Transcript'}
      </button>
      {!hasAudio && (
        <div style={{ marginTop: 8, fontSize: 12, opacity: 0.75 }}>
          Upload audio to enable transcription.
        </div>
      )}
      {taskId && (
        <div style={{ marginTop: 12, fontSize: 12 }}>
          Started transcription task: <code>{taskId}</code>
        </div>
      )}
      {isWaiting && (
        <div style={{ marginTop: 12, fontSize: 12, opacity: 0.8 }}>
          Processing…
        </div>
      )}
      {transcriptReady && (
        <div style={{ marginTop: 12, color: '#1b5e20', fontWeight: 700 }}>
          Transcript ready
        </div>
      )}
      {error && (
        <div style={{ marginTop: 12, color: '#b00020', fontWeight: 600 }}>
          {error}
        </div>
      )}
    </div>
  )
}
