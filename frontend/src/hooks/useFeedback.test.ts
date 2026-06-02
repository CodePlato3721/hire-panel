import { renderHook, act } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import { useFeedback } from './useFeedback'
import type { Resume, SSEEvent } from '../api'

vi.mock('../api', async importOriginal => {
  const actual = await importOriginal<typeof import('../api')>()
  return { ...actual, submitFeedback: vi.fn() }
})

import { submitFeedback } from '../api'

const SESSION_ID = 'test-session'
const RESUMES: Resume[] = [
  { filename: 'alice.pdf', content: '', total_score: 48, reason: 'Excellent Python', detail: '' },
]
const HR_MEMORY = { scoring_preferences: ['prefer Python'], adjustment_history: [] }

function makeOptions(overrides?: Partial<Parameters<typeof useFeedback>[0]>) {
  return { sessionId: SESSION_ID, onFeedbackDone: vi.fn(), ...overrides }
}

function mockSSE(events: SSEEvent[]) {
  vi.mocked(submitFeedback).mockImplementation(async (_sid, _text, onEvent) => {
    for (const e of events) onEvent(e)
  })
}

beforeEach(() => vi.clearAllMocks())

describe('handleSubmitFeedback', () => {
  it('does nothing when feedbackText is blank', async () => {
    const { result } = renderHook(() => useFeedback(makeOptions()))
    await act(() => result.current.handleSubmitFeedback())
    expect(result.current.isLoading).toBe(false)
    expect(result.current.streamText).toBe('')
  })

  it('clears feedbackText and starts streaming', async () => {
    mockSSE([{ type: 'done', resumes: RESUMES, hr_memory: HR_MEMORY }])
    const { result } = renderHook(() => useFeedback(makeOptions()))
    act(() => result.current.setFeedbackText('prioritize Python'))
    await act(() => result.current.handleSubmitFeedback())
    expect(result.current.feedbackText).toBe('')
  })

  it('accumulates tokens into streamText', async () => {
    mockSSE([
      { type: 'token', content: 're-' },
      { type: 'token', content: 'scoring' },
      { type: 'done', resumes: RESUMES, hr_memory: HR_MEMORY },
    ])
    const { result } = renderHook(() => useFeedback(makeOptions()))
    act(() => result.current.setFeedbackText('some feedback'))
    await act(() => result.current.handleSubmitFeedback())
    expect(result.current.streamText).toBe('re-scoring')
  })

  it('clears isLoading after completion', async () => {
    mockSSE([{ type: 'done', resumes: RESUMES, hr_memory: HR_MEMORY }])
    const { result } = renderHook(() => useFeedback(makeOptions()))
    act(() => result.current.setFeedbackText('some feedback'))
    await act(() => result.current.handleSubmitFeedback())
    expect(result.current.isLoading).toBe(false)
  })
})
