import { useSession } from './hooks/useSession'
import CriteriaList from './components/CriteriaList'
import JdFlow from './components/JdFlow'
import './App.css'

function App() {
  const { sessionId, stage, criteria, handleCriteriaDone } = useSession()

  return (
    <div className="app">
      <div className="left-panel">
        <CriteriaList criteria={criteria} />
      </div>
      <div className="right-panel">
        {sessionId && (
          <JdFlow
            sessionId={sessionId}
            initialStage={stage}
            initialCriteria={criteria}
            onCriteriaDone={handleCriteriaDone}
          />
        )}
      </div>
    </div>
  )
}

export default App
