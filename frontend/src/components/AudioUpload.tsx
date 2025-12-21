import { useMemo, useState } from 'react'

import {
  createProject,
  uploadAudioWithProgress,
  type UploadResponse,
} from '@/services/projects'

const allowedExtensions = ['.wav', '.mp3']

type Props = {
  onProjectIdChange?: (projectId: string | null) => void
  onAudioReadyChange?: (ready: boolean) => void
}

function formatBytes(bytes: number): string {
  const units = ['B', 'KB', 'MB', 'GB']
  let value = bytes
  let index = 0
  while (value >= 1024 && index < units.length - 1) {
    value /= 1024
    index += 1
  }
  return `${value.toFixed(index === 0 ? 0 : 1)} ${units[index]}`
}

function isAllowedFile(file: File): boolean {
  const lower = file.name.toLowerCase()
  return allowedExtensions.some((ext) => lower.endsWith(ext))
}

export function AudioUpload({
  onProjectIdChange,
  onAudioReadyChange,
}: Props): JSX.Element {
  const [projectId, setProjectId] = useState<string | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [progress, setProgress] = useState<number>(0)
  const [status, setStatus] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<UploadResponse | null>(null)

  const selectedLabel = useMemo(() => {
    if (!selectedFile) return 'Drop a .wav or .mp3 here, or click to browse'
    return `${selectedFile.name} (${formatBytes(selectedFile.size)})`
  }, [selectedFile])

  async function onUpload(): Promise<void> {
    if (!selectedFile) return

    setError(null)
    setResult(null)
    setProgress(0)
    setStatus('Uploading…')
    onAudioReadyChange?.(false)
    setIsUploading(true)
    try {
      let id = projectId
      if (!id) {
        const created = await createProject()
        id = created.project_id
        setProjectId(id)
        onProjectIdChange?.(id)
      }
      const response = await uploadAudioWithProgress(id, selectedFile, (p) => {
        setProgress(p.percent)
        if (p.percent >= 100) {
          setStatus('Processing…')
        }
      })
      setResult(response)
      setStatus('Complete')
      onAudioReadyChange?.(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
      setStatus(null)
      onAudioReadyChange?.(false)
    } finally {
      setIsUploading(false)
    }
  }

  function setFile(file: File | null): void {
    setError(null)
    setResult(null)
    setProgress(0)
    setStatus(null)
    onAudioReadyChange?.(false)
    if (!file) {
      setSelectedFile(null)
      return
    }
    if (!isAllowedFile(file)) {
      setSelectedFile(null)
      setError('Unsupported file type. Please select a .wav or .mp3.')
      return
    }
    setSelectedFile(file)
  }

  return (
    <div style={{ maxWidth: 640, margin: '0 auto' }}>
      <h2>Upload audio</h2>
      <label
        htmlFor="audio-file"
        onDragOver={(event) => {
          event.preventDefault()
          setIsDragging(true)
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(event) => {
          event.preventDefault()
          setIsDragging(false)
          const file = event.dataTransfer.files?.[0] ?? null
          setFile(file)
        }}
        style={{
          display: 'block',
          padding: 24,
          borderRadius: 12,
          border: `2px dashed ${isDragging ? '#646cff' : '#ccc'}`,
          background: isDragging ? 'rgba(100,108,255,0.08)' : 'transparent',
          cursor: 'pointer',
          userSelect: 'none',
        }}
      >
        <div style={{ fontWeight: 600 }}>{selectedLabel}</div>
        {projectId && (
          <div style={{ marginTop: 8, fontSize: 12, opacity: 0.75 }}>
            Project: {projectId}
          </div>
        )}
      </label>
      <input
        id="audio-file"
        type="file"
        accept={allowedExtensions.join(',')}
        onChange={(event) => setFile(event.target.files?.[0] ?? null)}
        style={{ display: 'none' }}
      />

      <div style={{ marginTop: 16, display: 'flex', gap: 12 }}>
        <button onClick={onUpload} disabled={!selectedFile || isUploading}>
          {isUploading ? 'Uploading…' : 'Upload'}
        </button>
        <button
          onClick={() => {
            setSelectedFile(null)
            setError(null)
            setResult(null)
            onAudioReadyChange?.(false)
          }}
          disabled={isUploading}
        >
          Clear
        </button>
      </div>

      {isUploading && (
        <div style={{ marginTop: 16 }}>
          <div style={{ fontSize: 12, opacity: 0.8 }}>{status}</div>
          <div
            style={{
              marginTop: 8,
              height: 10,
              borderRadius: 999,
              background: '#e6e6e6',
              overflow: 'hidden',
            }}
          >
            <div
              style={{
                width: `${progress}%`,
                height: '100%',
                background: '#646cff',
                transition: 'width 120ms linear',
              }}
            />
          </div>
          <div style={{ marginTop: 6, fontSize: 12, opacity: 0.75 }}>
            {progress}%
          </div>
        </div>
      )}

      {error && (
        <div style={{ marginTop: 16, color: '#b00020', fontWeight: 600 }}>
          {error}
        </div>
      )}

      {result && (
        <div style={{ marginTop: 16 }}>
          <div style={{ fontWeight: 700 }}>Upload complete</div>
          <div style={{ fontSize: 12, opacity: 0.8 }}>
            Stored as {result.filename} ({formatBytes(result.size_bytes)})
          </div>
        </div>
      )}
    </div>
  )
}
