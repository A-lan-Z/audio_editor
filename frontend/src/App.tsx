import viteLogo from '/vite.svg'
import './App.css'
import { AudioUpload } from '@/components/AudioUpload'

function App() {
  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'center', gap: 16 }}>
        <a href="https://vite.dev" target="_blank" rel="noreferrer">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
      </div>
      <h1>TextAudio Edit</h1>
      <AudioUpload />
    </>
  )
}

export default App
