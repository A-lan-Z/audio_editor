import { useEffect, useState } from 'react'

import {
  getTranscript,
  getTranscriptionStatus,
  startTranscription,
  type TranscriptionStatusResponse,
} from '@/services/projects'

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
  const [status, setStatus] = useState<
    TranscriptionStatusResponse['status'] | null
  >(null)
  const [progress, setProgress] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!projectId || !taskId) return

    let canceled = false
    let intervalId: number | null = null
    setTranscriptReady(false)
    setIsWaiting(true)
    setStatus('queued')
    setProgress(null)

    async function poll(): Promise<void> {
      try {
        const statusResponse = await getTranscriptionStatus(projectId)
        if (canceled) return
        setStatus(statusResponse.status)
        setProgress(
          typeof statusResponse.progress === 'number'
            ? statusResponse.progress
            : null
        )
        if (statusResponse.status === 'failed') {
          setError(statusResponse.error ?? 'Transcription failed')
          setIsWaiting(false)
          if (intervalId !== null) window.clearInterval(intervalId)
          return
        }
        if (statusResponse.status === 'completed') {
          await getTranscript(projectId)
          if (canceled) return
          setTranscriptReady(true)
          setIsWaiting(false)
          if (intervalId !== null) window.clearInterval(intervalId)
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Unknown error'
        if (canceled) return
        setError(message)
        setIsWaiting(false)
        if (intervalId !== null) window.clearInterval(intervalId)
      }
    }

    intervalId = window.setInterval(() => {
      void poll()
    }, 2000)
    void poll()

    return () => {
      canceled = true
      if (intervalId !== null) window.clearInterval(intervalId)
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
          {status === 'queued' ? 'Queued…' : 'Processing…'}
        </div>
      )}
      {typeof progress === 'number' && (
        <div style={{ marginTop: 8, fontSize: 12, opacity: 0.8 }}>
          Progress: {Math.round(progress * 100)}%
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
