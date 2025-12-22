export type CreateProjectResponse = {
  project_id: string
  created_at: string
  updated_at: string
  audio_path: string | null
  metadata: Record<string, unknown>
}

export type UploadResponse = {
  project_id: string
  filename: string
  content_type: string | null
  size_bytes: number
  status: string
}

export async function createProject(
  metadata: Record<string, unknown> = {}
): Promise<CreateProjectResponse> {
  const response = await fetch('/api/projects', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ metadata }),
  })

  if (!response.ok) {
    throw new Error(`Failed to create project (${response.status})`)
  }

  return (await response.json()) as CreateProjectResponse
}

export async function uploadAudio(
  projectId: string,
  file: File
): Promise<UploadResponse> {
  const form = new FormData()
  form.append('file', file, file.name)

  const response = await fetch(`/api/projects/${projectId}/upload`, {
    method: 'POST',
    body: form,
  })

  const data = (await response.json()) as unknown

  if (!response.ok) {
    if (
      typeof data === 'object' &&
      data !== null &&
      'detail' in data &&
      typeof (data as { detail: unknown }).detail === 'string'
    ) {
      throw new Error((data as { detail: string }).detail)
    }
    throw new Error(`Upload failed (${response.status})`)
  }

  return data as UploadResponse
}

export type UploadProgress = {
  loaded: number
  total: number
  percent: number
}

export function uploadAudioWithProgress(
  projectId: string,
  file: File,
  onProgress: (progress: UploadProgress) => void
): Promise<UploadResponse> {
  return new Promise((resolve, reject) => {
    const form = new FormData()
    form.append('file', file, file.name)

    const request = new XMLHttpRequest()
    request.open('POST', `/api/projects/${projectId}/upload`)

    request.upload.addEventListener('progress', (event) => {
      const total = event.lengthComputable ? event.total : file.size
      const percent = total > 0 ? Math.round((event.loaded / total) * 100) : 0
      onProgress({ loaded: event.loaded, total, percent })
    })

    request.addEventListener('error', () => {
      reject(new Error('Upload failed'))
    })

    request.addEventListener('load', () => {
      let payload: unknown = null
      try {
        payload = JSON.parse(request.responseText)
      } catch {
        // ignore
      }

      if (request.status >= 200 && request.status < 300) {
        resolve(payload as UploadResponse)
        return
      }

      if (
        payload &&
        typeof payload === 'object' &&
        'detail' in payload &&
        typeof (payload as { detail: unknown }).detail === 'string'
      ) {
        reject(new Error((payload as { detail: string }).detail))
        return
      }

      reject(new Error(`Upload failed (${request.status})`))
    })

    request.send(form)
  })
}

export type StartTranscriptionResponse = {
  task_id: string
  status: string
}

export type TranscriptionStatusResponse = {
  task_id: string | null
  status: 'queued' | 'processing' | 'completed' | 'failed'
  progress?: number | null
  error?: string | null
}

export async function startTranscription(
  projectId: string
): Promise<StartTranscriptionResponse> {
  const response = await fetch(`/api/projects/${projectId}/transcribe`, {
    method: 'POST',
  })

  const data = (await response.json()) as unknown

  if (!response.ok) {
    if (
      typeof data === 'object' &&
      data !== null &&
      'detail' in data &&
      typeof (data as { detail: unknown }).detail === 'string'
    ) {
      throw new Error((data as { detail: string }).detail)
    }
    throw new Error(`Transcription failed (${response.status})`)
  }

  return data as StartTranscriptionResponse
}

export async function getTranscriptionStatus(
  projectId: string
): Promise<TranscriptionStatusResponse> {
  const response = await fetch(`/api/projects/${projectId}/transcribe/status`, {
    method: 'GET',
  })

  const data = (await response.json()) as unknown

  if (!response.ok) {
    if (
      typeof data === 'object' &&
      data !== null &&
      'detail' in data &&
      typeof (data as { detail: unknown }).detail === 'string'
    ) {
      throw new Error((data as { detail: string }).detail)
    }
    throw new Error(`Failed to fetch transcription status (${response.status})`)
  }

  return data as TranscriptionStatusResponse
}

export type TranscriptToken = {
  id: string
  text: string
  start: number
  end: number
  type: 'word' | 'punctuation' | 'pause'
  status: 'original' | 'deleted' | 'replaced' | 'inserted' | 'generated'
}

export type Transcript = {
  tokens: TranscriptToken[]
  language: string
  duration: number
  created_at: string
}

export async function getTranscript(projectId: string): Promise<Transcript> {
  const response = await fetch(`/api/projects/${projectId}/transcript`, {
    method: 'GET',
  })

  const data = (await response.json()) as unknown

  if (!response.ok) {
    if (
      typeof data === 'object' &&
      data !== null &&
      'detail' in data &&
      typeof (data as { detail: unknown }).detail === 'string'
    ) {
      throw new Error((data as { detail: string }).detail)
    }
    throw new Error(`Failed to fetch transcript (${response.status})`)
  }

  return data as Transcript
}

export type EditOperationPayload = {
  id: string
  type: 'insert' | 'delete' | 'replace'
  position: number
  old_tokens: string[]
  new_text: string
  timestamp: string
}

export async function submitEditOperation(
  projectId: string,
  operation: EditOperationPayload
): Promise<Transcript> {
  const response = await fetch(`/api/projects/${projectId}/edit`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(operation),
  })

  const data = (await response.json()) as unknown

  if (!response.ok) {
    if (
      typeof data === 'object' &&
      data !== null &&
      'detail' in data &&
      typeof (data as { detail: unknown }).detail === 'string'
    ) {
      throw new Error((data as { detail: string }).detail)
    }
    throw new Error(`Failed to submit edit (${response.status})`)
  }

  return data as Transcript
}

export async function undoEdit(projectId: string): Promise<Transcript> {
  const response = await fetch(`/api/projects/${projectId}/undo`, {
    method: 'POST',
  })

  const data = (await response.json()) as unknown

  if (!response.ok) {
    if (
      typeof data === 'object' &&
      data !== null &&
      'detail' in data &&
      typeof (data as { detail: unknown }).detail === 'string'
    ) {
      throw new Error((data as { detail: string }).detail)
    }
    throw new Error(`Undo failed (${response.status})`)
  }

  return data as Transcript
}

export async function redoEdit(projectId: string): Promise<Transcript> {
  const response = await fetch(`/api/projects/${projectId}/redo`, {
    method: 'POST',
  })

  const data = (await response.json()) as unknown

  if (!response.ok) {
    if (
      typeof data === 'object' &&
      data !== null &&
      'detail' in data &&
      typeof (data as { detail: unknown }).detail === 'string'
    ) {
      throw new Error((data as { detail: string }).detail)
    }
    throw new Error(`Redo failed (${response.status})`)
  }

  return data as Transcript
}

export type TimestampDiagnosticsToken = {
  id: string
  text: string
  type: string
  active_start: number
  active_end: number
  asr_start?: number | null
  asr_end?: number | null
  refined_start?: number | null
  refined_end?: number | null
  delta_asr_start?: number | null
  delta_asr_end?: number | null
  delta_refined_start?: number | null
  delta_refined_end?: number | null
}

export type TimestampDiagnosticsSegment = {
  id: string
  source: string
  status: string
  start: number
  end: number
  token_ids: string[]
}

export type TimestampDiagnosticsBoundaryTrim = {
  prev_segment_id: string
  next_segment_id: string
  prev_end_before: number
  prev_end_snapped: number
  prev_end_trimmed: number
  next_start_before: number
  next_start_snapped: number
  next_start_trimmed: number
}

export type TimestampDiagnosticsResponse = {
  project_id: string
  computed_at: string
  transcript_active_source?: string | null
  refinement_enabled: boolean
  snap_window_ms: number
  cut_padding_ms: number
  tokens: TimestampDiagnosticsToken[]
  segments: TimestampDiagnosticsSegment[]
  boundary_trims: TimestampDiagnosticsBoundaryTrim[]
}

export async function getTimestampDiagnostics(
  projectId: string
): Promise<TimestampDiagnosticsResponse> {
  const response = await fetch(`/api/projects/${projectId}/diagnostics/timestamps`, {
    method: 'GET',
  })
  const data = (await response.json()) as unknown

  if (!response.ok) {
    if (
      typeof data === 'object' &&
      data !== null &&
      'detail' in data &&
      typeof (data as { detail: unknown }).detail === 'string'
    ) {
      throw new Error((data as { detail: string }).detail)
    }
    throw new Error(`Failed to fetch diagnostics (${response.status})`)
  }
  return data as TimestampDiagnosticsResponse
}
