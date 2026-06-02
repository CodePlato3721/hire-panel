import { useEffect, useState } from 'react'
import { createSession, getSession, Stage } from '../api'
import type { ScoringCriteria } from '../api'

export const SESSION_KEY = 'hire_panel_session_id'

export function useSession() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [stage, setStage] = useState<Stage>(Stage.Idle)
  const [criteria, setCriteria] = useState<ScoringCriteria[]>([])

  useEffect(() => {
    const stored = localStorage.getItem(SESSION_KEY)
    if (stored) {
      getSession(stored)
        .then(state => {
          setStage(state.stage)
          setCriteria(state.criteria)
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

  function handleCriteriaDone(newCriteria: ScoringCriteria[]) {
    setCriteria(newCriteria)
    setStage(Stage.JdDone)
  }

  return { sessionId, stage, criteria, handleCriteriaDone }
}
