import { renderHook, waitFor } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import { useSession, SESSION_KEY } from './useSession'
import { Stage } from '../api'
import type { SessionState } from '../api'

vi.mock('../api', async importOriginal => {
  const actual = await importOriginal<typeof import('../api')>()
  return {
    ...actual,
    createSession: vi.fn(),
    getSession: vi.fn(),
  }
})

import { createSession, getSession } from '../api'

const SESSION_ID = 'session-abc'
const RESTORED_STATE: SessionState = {
  session_id: SESSION_ID,
  stage: Stage.JdDone,
  criteria: [{ name: 'Python', description: '5+ years' }],
  resumes: [],
  hr_memory: { scoring_preferences: [], adjustment_history: [] },
}

beforeEach(() => {
  vi.clearAllMocks()
  localStorage.clear()
})

describe('new session (nothing in localStorage)', () => {
  it('creates a session and sets sessionId', async () => {
    vi.mocked(createSession).mockResolvedValue(SESSION_ID)
    const { result } = renderHook(() => useSession())

    await waitFor(() => expect(result.current.sessionId).toBe(SESSION_ID))
    expect(localStorage.getItem(SESSION_KEY)).toBe(SESSION_ID)
    expect(result.current.stage).toBe(Stage.Idle)
    expect(result.current.criteria).toEqual([])
  })
})

describe('existing session in localStorage', () => {
  it('restores sessionId, stage and criteria from server', async () => {
    localStorage.setItem(SESSION_KEY, SESSION_ID)
    vi.mocked(getSession).mockResolvedValue(RESTORED_STATE)

    const { result } = renderHook(() => useSession())

    await waitFor(() => expect(result.current.sessionId).toBe(SESSION_ID))
    expect(result.current.stage).toBe(Stage.JdDone)
    expect(result.current.criteria).toEqual(RESTORED_STATE.criteria)
  })

  it('creates a new session when getSession fails', async () => {
    const NEW_ID = 'session-new'
    localStorage.setItem(SESSION_KEY, SESSION_ID)
    vi.mocked(getSession).mockRejectedValue(new Error('not found'))
    vi.mocked(createSession).mockResolvedValue(NEW_ID)

    const { result } = renderHook(() => useSession())

    await waitFor(() => expect(result.current.sessionId).toBe(NEW_ID))
    expect(localStorage.getItem(SESSION_KEY)).toBe(NEW_ID)
    expect(result.current.stage).toBe(Stage.Idle)
  })
})

describe('handleCriteriaDone', () => {
  it('updates criteria and advances stage to JdDone', async () => {
    vi.mocked(createSession).mockResolvedValue(SESSION_ID)
    const { result } = renderHook(() => useSession())
    await waitFor(() => expect(result.current.sessionId).toBe(SESSION_ID))

    const newCriteria = [{ name: 'Go', description: '3+ years' }]
    result.current.handleCriteriaDone(newCriteria)

    await waitFor(() => {
      expect(result.current.criteria).toEqual(newCriteria)
      expect(result.current.stage).toBe(Stage.JdDone)
    })
  })
})

describe('handleResumesDone', () => {
  it('updates resumes and advances stage to ResumeDone', async () => {
    vi.mocked(createSession).mockResolvedValue(SESSION_ID)
    const { result } = renderHook(() => useSession())
    await waitFor(() => expect(result.current.sessionId).toBe(SESSION_ID))

    const newResumes = [
      { filename: 'alice.pdf', content: '', total_score: 42, reason: 'Strong Python', detail: '' },
    ]
    result.current.handleResumesDone(newResumes)

    await waitFor(() => {
      expect(result.current.resumes).toEqual(newResumes)
      expect(result.current.stage).toBe(Stage.ResumeDone)
    })
  })
})
