const BASE_URL = 'http://localhost:8000'

// --- Types ---

export type Stage = 'idle' | 'jd_pending' | 'jd_done' | 'resume_done' | 'feedback_done'

export interface ScoringCriteria {
  name: string
  description: string
}

export interface Resume {
  filename: string
  content: string
  total_score: number | null
  reason: string
  detail: string
}

export interface HRMemory {
  scoring_preferences: string[]
  adjustment_history: string[]
}

export interface SessionState {
  session_id: string
  stage: Stage
  criteria: ScoringCriteria[]
  resumes: Resume[]
  hr_memory: HRMemory
}

export type TokenEvent = { type: 'token'; content: string }
export type JDDoneEvent = { type: 'done'; interrupted: boolean; criteria: ScoringCriteria[] }
export type ResumeDoneEvent = { type: 'done'; resumes: Resume[] }
export type FeedbackDoneEvent = { type: 'done'; resumes: Resume[]; hr_memory: HRMemory }
export type SSEEvent = TokenEvent | JDDoneEvent | ResumeDoneEvent | FeedbackDoneEvent

// --- SSE helper ---

const DATA_PREFIX = 'data: '

function stripDataPrefix(line: string): string {
  return line.slice(DATA_PREFIX.length)
}

async function streamSSE(response: Response, onEvent: (event: SSEEvent) => void): Promise<void> {
  const reader = response.body!.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() ?? ''
    for (const line of lines) {
      if (line.startsWith(DATA_PREFIX)) {
        onEvent(JSON.parse(stripDataPrefix(line)) as SSEEvent)
      }
    }
  }
}

// --- API functions ---

export async function createSession(): Promise<string> {
  const res = await fetch(`${BASE_URL}/api/sessions`, { method: 'POST' })
  const data = await res.json()
  return data.session_id as string
}

export async function getSession(sessionId: string): Promise<SessionState> {
  const res = await fetch(`${BASE_URL}/api/sessions/${sessionId}`)
  return res.json() as Promise<SessionState>
}

export async function submitJd(
  sessionId: string,
  jdText: string,
  onEvent: (event: SSEEvent) => void,
): Promise<void> {
  const res = await fetch(`${BASE_URL}/api/sessions/${sessionId}/jd`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ jd_text: jdText }),
  })
  await streamSSE(res, onEvent)
}

export async function replyJd(
  sessionId: string,
  reply: string,
  onEvent: (event: SSEEvent) => void,
): Promise<void> {
  const res = await fetch(`${BASE_URL}/api/sessions/${sessionId}/jd/reply`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ reply }),
  })
  await streamSSE(res, onEvent)
}

export async function uploadResumes(
  sessionId: string,
  files: File[],
  onEvent: (event: SSEEvent) => void,
): Promise<void> {
  const form = new FormData()
  for (const file of files) {
    form.append('files', file)
  }
  const res = await fetch(`${BASE_URL}/api/sessions/${sessionId}/resumes`, {
    method: 'POST',
    body: form,
  })
  await streamSSE(res, onEvent)
}

export async function submitFeedback(
  sessionId: string,
  feedback: string,
  onEvent: (event: SSEEvent) => void,
): Promise<void> {
  const res = await fetch(`${BASE_URL}/api/sessions/${sessionId}/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ feedback }),
  })
  await streamSSE(res, onEvent)
}
