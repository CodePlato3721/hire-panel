import { useEffect, useState } from 'react'
import { createSession, getSession } from './api'
import './App.css'

const SESSION_KEY = 'hire_panel_session_id'

function App() {
  const [sessionId, setSessionId] = useState<string | null>(null)

  useEffect(() => {
    const stored = localStorage.getItem(SESSION_KEY)
    if (stored) {
      getSession(stored)
        .then(() => {
          setSessionId(stored)
        })
        .catch(() => {
          localStorage.removeItem(SESSION_KEY)
          createSession().then(id => {
            localStorage.setItem(SESSION_KEY, id)
            setSessionId(id)
          })
        })
    } else {
      createSession().then(id => {
        localStorage.setItem(SESSION_KEY, id)
        setSessionId(id)
      })
    }
  }, [])

  return (
    <div className="app">
      <div className="left-panel">
        {/* criteria + resume table — Task J / K */}
        <p className="placeholder">session: {sessionId ?? 'initializing…'}</p>
      </div>
      <div className="right-panel">
        {/* chat window — Task J / K / L */}
      </div>
    </div>
  )
}

export default App
