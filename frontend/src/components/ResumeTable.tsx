import type { Resume } from '../api'

interface Props {
  resumes: Resume[]
  maxScore: number
}

export default function ResumeTable({ resumes, maxScore }: Props) {
  if (resumes.length === 0) return null
  return (
    <div className="resume-table-section">
      <h2>Resumes</h2>
      <table className="resume-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Score</th>
            <th>Summary</th>
          </tr>
        </thead>
        <tbody>
          {resumes.map((r, i) => (
            <tr key={i}>
              <td className="resume-name">{r.filename}</td>
              <td className="resume-score">
                {r.total_score != null ? `${r.total_score} / ${maxScore}` : '—'}
              </td>
              <td className="resume-reason">{r.reason}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
