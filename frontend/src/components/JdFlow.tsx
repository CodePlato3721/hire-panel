import { useEffect, useRef, useState } from 'react'
import { submitJd, replyJd, Stage } from '../api'
import type { ScoringCriteria, SSEEvent } from '../api'

const JdUiState = {
  Idle: 'idle',
  Input: 'input',
  Streaming: 'streaming',
  Approving: 'approving',
  Done: 'done',
} as const

type JdUiState = typeof JdUiState[keyof typeof JdUiState]

function getInitialUiState(stage: Stage): JdUiState {
  if (stage === Stage.JdPending) return JdUiState.Approving
  if (stage === Stage.JdDone || stage === Stage.ResumeDone || stage === Stage.FeedbackDone) return JdUiState.Done
  return JdUiState.Idle
}

interface Props {
  sessionId: string
  initialStage: Stage
  initialCriteria: ScoringCriteria[]
  onCriteriaDone: (criteria: ScoringCriteria[]) => void
}

export default function JdFlow({ sessionId, initialStage, initialCriteria, onCriteriaDone }: Props) {
  const [uiState, setUiState] = useState<JdUiState>(() => getInitialUiState(initialStage))
  const [jdText, setJdText] = useState('')
  const [streamText, setStreamText] = useState('')
  const [pendingCriteria, setPendingCriteria] = useState<ScoringCriteria[]>(
    initialStage === Stage.JdPending ? initialCriteria : [],
  )
  const [replyText, setReplyText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const streamRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (streamRef.current) {
      streamRef.current.scrollTop = streamRef.current.scrollHeight
    }
  }, [streamText])

  async function handleSubmitJd() {
    if (!jdText.trim()) return
    setUiState(JdUiState.Streaming)
    setStreamText('')
    setIsLoading(true)
    try {
      await submitJd(sessionId, jdText, (event: SSEEvent) => {
        if (event.type === 'token') {
          setStreamText(prev => prev + event.content)
        } else if (event.type === 'done' && 'interrupted' in event) {
          if (event.interrupted) {
            setPendingCriteria(event.criteria)
            setUiState(JdUiState.Approving)
          } else {
            onCriteriaDone(event.criteria)
            setUiState(JdUiState.Done)
          }
        }
      })
    } finally {
      setIsLoading(false)
    }
  }

  async function handleReplyJd() {
    if (!replyText.trim() || isLoading) return
    setUiState(JdUiState.Streaming)
    setStreamText('')
    setIsLoading(true)
    try {
      await replyJd(sessionId, replyText, (event: SSEEvent) => {
        if (event.type === 'token') {
          setStreamText(prev => prev + event.content)
        } else if (event.type === 'done' && 'interrupted' in event) {
          onCriteriaDone(event.criteria)
          setUiState(JdUiState.Done)
        }
      })
    } finally {
      setIsLoading(false)
    }
  }

  if (uiState === JdUiState.Done) {
    return (
      <div className="jd-done">
        <p>JD criteria confirmed. See criteria panel on the left.</p>
      </div>
    )
  }

  if (uiState === JdUiState.Idle) {
    return (
      <div className="jd-idle">
        <button className="quick-action" onClick={() => setUiState(JdUiState.Input)}>Fill JD</button>
      </div>
    )
  }

  if (uiState === JdUiState.Input) {
    return (
      <div className="jd-input">
        <textarea
          className="jd-textarea"
          placeholder="Paste job description here…"
          value={jdText}
          onChange={e => setJdText(e.target.value)}
          rows={14}
          autoFocus
        />
        <div className="jd-actions">
          <button className="btn-secondary" onClick={() => setUiState(JdUiState.Idle)}>Cancel</button>
          <button className="btn-primary" onClick={handleSubmitJd} disabled={!jdText.trim()}>
            Analyze
          </button>
        </div>
      </div>
    )
  }

  if (uiState === JdUiState.Streaming) {
    return (
      <div className="jd-streaming">
        <div className="stream-output" ref={streamRef}>{streamText || '…'}</div>
      </div>
    )
  }

  // JdUiState.Approving
  return (
    <div className="jd-approving">
      {streamText && <div className="stream-output" ref={streamRef}>{streamText}</div>}
      <div className="approval-section">
        <h2>Review Criteria</h2>
        <ul className="pending-criteria">
          {pendingCriteria.map((c, i) => (
            <li key={i}>
              <strong>{c.name}</strong>: {c.description}
            </li>
          ))}
        </ul>
        <textarea
          className="reply-textarea"
          placeholder="Type 'approve' to confirm, or suggest modifications…"
          value={replyText}
          onChange={e => setReplyText(e.target.value)}
          rows={3}
          autoFocus
        />
        <div className="jd-actions">
          <button
            className="btn-primary"
            onClick={handleReplyJd}
            disabled={!replyText.trim() || isLoading}
          >
            Submit
          </button>
        </div>
      </div>
    </div>
  )
}
