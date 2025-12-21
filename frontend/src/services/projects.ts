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
