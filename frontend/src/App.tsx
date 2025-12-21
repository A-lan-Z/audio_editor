import viteLogo from '/vite.svg'
import { useState } from 'react'
import './App.css'
import { AudioUpload } from '@/components/AudioUpload'
import { TranscriptionTrigger } from '@/components/TranscriptionTrigger'
import { TranscriptEditor } from '@/components/TranscriptEditor'
import type { Transcript } from '@/services/projects'

function App() {
  const [projectId, setProjectId] = useState<string | null>(null)
  const [hasAudio, setHasAudio] = useState(false)
  const [transcript, setTranscript] = useState<Transcript | null>(null)

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'center', gap: 16 }}>
        <a href="https://vite.dev" target="_blank" rel="noreferrer">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
      </div>
      <h1>TextAudio Edit</h1>
      <AudioUpload
        onProjectIdChange={setProjectId}
        onAudioReadyChange={(ready) => {
          setHasAudio(ready)
          if (!ready) setTranscript(null)
        }}
      />
      <TranscriptionTrigger
        projectId={projectId}
        hasAudio={hasAudio}
        onTranscriptLoaded={setTranscript}
      />
      {transcript && projectId && (
        <TranscriptEditor
          key={transcript.created_at}
          transcript={transcript}
          projectId={projectId}
        />
      )}
    </>
  )
}

export default App
