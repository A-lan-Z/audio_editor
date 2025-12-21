import viteLogo from '/vite.svg'
import { useState } from 'react'
import './App.css'
import { AudioUpload } from '@/components/AudioUpload'
import { TranscriptionTrigger } from '@/components/TranscriptionTrigger'

function App() {
  const [projectId, setProjectId] = useState<string | null>(null)
  const [hasAudio, setHasAudio] = useState(false)

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
        onAudioReadyChange={setHasAudio}
      />
      <TranscriptionTrigger projectId={projectId} hasAudio={hasAudio} />
    </>
  )
}

export default App
