import { useFeedback } from '../hooks/useFeedback'
import type { Resume } from '../api'

interface Props {
  sessionId: string
  onFeedbackDone: (resumes: Resume[]) => void
}

export default function FeedbackChat({ sessionId, onFeedbackDone }: Props) {
  const {
    feedbackText, setFeedbackText,
    streamText, streamRef,
    isLoading,
    handleSubmitFeedback,
  } = useFeedback({ sessionId, onFeedbackDone })

  return (
    <div className="feedback-chat">
      {streamText && (
        <div className="stream-output" ref={streamRef}>{streamText}</div>
      )}
      <div className="feedback-input-area">
        <textarea
          className="reply-textarea"
          placeholder="Enter feedback to re-score resumes…"
          value={feedbackText}
          onChange={e => setFeedbackText(e.target.value)}
          rows={4}
          disabled={isLoading}
          autoFocus
        />
        <div className="jd-actions">
          <button
            className="btn-primary"
            onClick={handleSubmitFeedback}
            disabled={!feedbackText.trim() || isLoading}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  )
}
