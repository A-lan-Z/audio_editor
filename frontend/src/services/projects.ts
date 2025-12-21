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
