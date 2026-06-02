import { useResumeUpload, ResumeUiState } from '../hooks/useResumeUpload'
import type { Resume, Stage } from '../api'

interface Props {
  sessionId: string
  initialStage: Stage
  onResumesDone: (resumes: Resume[]) => void
}

export default function ResumeUpload({ sessionId, initialStage, onResumesDone }: Props) {
  const {
    uiState,
    streamText, streamRef,
    fileInputRef,
    triggerFileInput,
    handleFilesSelected,
  } = useResumeUpload({ sessionId, initialStage, onResumesDone })

  return (
    <div>
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept=".pdf,.txt"
        style={{ display: 'none' }}
        onChange={e => handleFilesSelected(Array.from(e.target.files ?? []))}
      />
      {uiState === ResumeUiState.Idle && (
        <div className="resume-idle">
          <button className="quick-action" onClick={triggerFileInput}>
            Upload Resumes
          </button>
        </div>
      )}
      {uiState === ResumeUiState.Streaming && (
        <div className="resume-streaming">
          <div className="stream-output" ref={streamRef}>{streamText || '…'}</div>
        </div>
      )}
      {uiState === ResumeUiState.Done && (
        <div className="resume-done">
          <p>Resumes scored. See table on the left.</p>
        </div>
      )}
    </div>
  )
}
