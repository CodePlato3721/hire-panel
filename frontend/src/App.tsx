import { useSession } from './hooks/useSession'
import { Stage } from './api'
import CriteriaList from './components/CriteriaList'
import ResumeTable from './components/ResumeTable'
import JdFlow from './components/JdFlow'
import ResumeUpload from './components/ResumeUpload'
import './App.css'

function App() {
  const { sessionId, stage, criteria, resumes, handleCriteriaDone, handleResumesDone } = useSession()

  const jdDone = stage === Stage.JdDone || stage === Stage.ResumeDone || stage === Stage.FeedbackDone

  return (
    <div className="app">
      <div className="left-panel">
        <CriteriaList criteria={criteria} />
        <ResumeTable resumes={resumes} />
      </div>
      <div className="right-panel">
        {sessionId && !jdDone && (
          <JdFlow
            sessionId={sessionId}
            initialStage={stage}
            initialCriteria={criteria}
            onCriteriaDone={handleCriteriaDone}
          />
        )}
        {sessionId && jdDone && (
          <ResumeUpload
            sessionId={sessionId}
            initialStage={stage}
            onResumesDone={handleResumesDone}
          />
        )}
      </div>
    </div>
  )
}

export default App
