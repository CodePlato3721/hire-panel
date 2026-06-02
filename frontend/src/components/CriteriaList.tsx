import type { ScoringCriteria } from '../api'

interface Props {
  criteria: ScoringCriteria[]
}

export default function CriteriaList({ criteria }: Props) {
  if (criteria.length === 0) {
    return <p className="placeholder">No criteria yet. Fill in a JD to get started.</p>
  }
  return (
    <div className="criteria-list">
      <h2>Scoring Criteria</h2>
      <ul>
        {criteria.map((c, i) => (
          <li key={i} className="criterion-item">
            <strong>{c.name}</strong>
            <p>{c.description}</p>
          </li>
        ))}
      </ul>
    </div>
  )
}
