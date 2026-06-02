import { useJdFlow, JdUiState } from '../hooks/useJdFlow'
import type { ScoringCriteria, Stage } from '../api'

interface Props {
  sessionId: string
  initialStage: Stage
  initialCriteria: ScoringCriteria[]
  onCriteriaDone: (criteria: ScoringCriteria[]) => void
}

export default function JdFlow({ sessionId, initialStage, initialCriteria, onCriteriaDone }: Props) {
  const {
    uiState,
    jdText, setJdText,
    streamText, streamRef,
    pendingCriteria,
    replyText, setReplyText,
    isLoading,
    startInput, cancelInput,
    handleSubmitJd, handleReplyJd,
  } = useJdFlow({ sessionId, initialStage, initialCriteria, onCriteriaDone })

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
        <button className="quick-action" onClick={startInput}>Fill JD</button>
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
          <button className="btn-secondary" onClick={cancelInput}>Cancel</button>
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
