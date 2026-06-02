import { useEffect, useState } from 'react'
import { createSession, getSession, Stage } from '../api'
import type { ScoringCriteria, Resume } from '../api'

export const SESSION_KEY = 'hire_panel_session_id'

export function useSession() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [stage, setStage] = useState<Stage>(Stage.Idle)
  const [criteria, setCriteria] = useState<ScoringCriteria[]>([])
  const [resumes, setResumes] = useState<Resume[]>([])

  useEffect(() => {
    const stored = localStorage.getItem(SESSION_KEY)
    if (stored) {
      getSession(stored)
        .then(state => {
          setStage(state.stage)
          setCriteria(state.criteria)
          setResumes(state.resumes)
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

  function handleResumesDone(newResumes: Resume[]) {
    setResumes(newResumes)
    setStage(Stage.ResumeDone)
  }

  function handleFeedbackDone(newResumes: Resume[]) {
    setResumes(newResumes)
    setStage(Stage.FeedbackDone)
  }

  return { sessionId, stage, criteria, resumes, handleCriteriaDone, handleResumesDone, handleFeedbackDone }
}
