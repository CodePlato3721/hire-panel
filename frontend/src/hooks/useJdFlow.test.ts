import { renderHook, act } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import { useJdFlow, JdUiState } from './useJdFlow'
import { Stage } from '../api'
import type { ScoringCriteria, SSEEvent } from '../api'

vi.mock('../api', async importOriginal => {
  const actual = await importOriginal<typeof import('../api')>()
  return {
    ...actual,
    submitJd: vi.fn(),
    replyJd: vi.fn(),
  }
})

import { submitJd, replyJd } from '../api'

const SESSION_ID = 'test-session'
const CRITERIA: ScoringCriteria[] = [
  { name: 'Python', description: '5+ years' },
  { name: 'LLMs', description: 'LangChain experience' },
]

function makeOptions(overrides?: Partial<Parameters<typeof useJdFlow>[0]>) {
  return {
    sessionId: SESSION_ID,
    initialStage: Stage.Idle,
    initialCriteria: [],
    onCriteriaDone: vi.fn(),
    ...overrides,
  }
}

// Simulate submitJd/replyJd firing SSE events then resolving
function mockSSE(fn: typeof submitJd | typeof replyJd, events: SSEEvent[]) {
  vi.mocked(fn).mockImplementation(async (_sid, _payload, onEvent) => {
    for (const e of events) onEvent(e)
  })
}

describe('initial uiState', () => {
  it('is Idle when stage is idle', () => {
    const { result } = renderHook(() => useJdFlow(makeOptions()))
    expect(result.current.uiState).toBe(JdUiState.Idle)
  })

  it('is Approving when stage is jd_pending, with initialCriteria pre-loaded', () => {
    const { result } = renderHook(() =>
      useJdFlow(makeOptions({ initialStage: Stage.JdPending, initialCriteria: CRITERIA })),
    )
    expect(result.current.uiState).toBe(JdUiState.Approving)
    expect(result.current.pendingCriteria).toEqual(CRITERIA)
  })

  it('is Done when stage is jd_done', () => {
    const { result } = renderHook(() =>
      useJdFlow(makeOptions({ initialStage: Stage.JdDone })),
    )
    expect(result.current.uiState).toBe(JdUiState.Done)
  })

  it('is Done when stage is resume_done or feedback_done', () => {
    for (const stage of [Stage.ResumeDone, Stage.FeedbackDone]) {
      const { result } = renderHook(() => useJdFlow(makeOptions({ initialStage: stage })))
      expect(result.current.uiState).toBe(JdUiState.Done)
    }
  })
})

describe('startInput / cancelInput', () => {
  it('transitions Idle → Input → Idle', () => {
    const { result } = renderHook(() => useJdFlow(makeOptions()))
    act(() => result.current.startInput())
    expect(result.current.uiState).toBe(JdUiState.Input)
    act(() => result.current.cancelInput())
    expect(result.current.uiState).toBe(JdUiState.Idle)
  })
})

describe('handleSubmitJd', () => {
  beforeEach(() => vi.clearAllMocks())

  it('does nothing when jdText is blank', async () => {
    const { result } = renderHook(() => useJdFlow(makeOptions()))
    await act(() => result.current.handleSubmitJd())
    expect(result.current.uiState).toBe(JdUiState.Idle)
  })

  it('streams tokens into streamText', async () => {
    mockSSE(submitJd, [
      { type: 'token', content: 'hello' },
      { type: 'token', content: ' world' },
      { type: 'done', interrupted: false, criteria: CRITERIA },
    ])
    const { result } = renderHook(() => useJdFlow(makeOptions()))
    act(() => result.current.setJdText('some JD'))
    await act(() => result.current.handleSubmitJd())
    expect(result.current.streamText).toBe('hello world')
  })

  it('transitions to Approving when interrupted', async () => {
    mockSSE(submitJd, [{ type: 'done', interrupted: true, criteria: CRITERIA }])
    const { result } = renderHook(() => useJdFlow(makeOptions()))
    act(() => result.current.setJdText('some JD'))
    await act(() => result.current.handleSubmitJd())
    expect(result.current.uiState).toBe(JdUiState.Approving)
    expect(result.current.pendingCriteria).toEqual(CRITERIA)
  })

  it('transitions to Done when not interrupted', async () => {
    mockSSE(submitJd, [{ type: 'done', interrupted: false, criteria: CRITERIA }])
    const { result } = renderHook(() => useJdFlow(makeOptions()))
    act(() => result.current.setJdText('some JD'))
    await act(() => result.current.handleSubmitJd())
    expect(result.current.uiState).toBe(JdUiState.Done)
  })

  it('clears isLoading after completion', async () => {
    mockSSE(submitJd, [{ type: 'done', interrupted: false, criteria: CRITERIA }])
    const { result } = renderHook(() => useJdFlow(makeOptions()))
    act(() => result.current.setJdText('some JD'))
    await act(() => result.current.handleSubmitJd())
    expect(result.current.isLoading).toBe(false)
  })
})

describe('handleReplyJd', () => {
  beforeEach(() => vi.clearAllMocks())

  it('does nothing when replyText is blank', async () => {
    const { result } = renderHook(() =>
      useJdFlow(makeOptions({ initialStage: Stage.JdPending, initialCriteria: CRITERIA })),
    )
    await act(() => result.current.handleReplyJd())
    expect(result.current.uiState).toBe(JdUiState.Approving)
  })

  it('transitions to Done', async () => {
    mockSSE(replyJd, [{ type: 'done', interrupted: false, criteria: CRITERIA }])
    const { result } = renderHook(() =>
      useJdFlow(makeOptions({ initialStage: Stage.JdPending, initialCriteria: CRITERIA })),
    )
    act(() => result.current.setReplyText('approve'))
    await act(() => result.current.handleReplyJd())
    expect(result.current.uiState).toBe(JdUiState.Done)
  })

  it('clears isLoading after completion', async () => {
    mockSSE(replyJd, [{ type: 'done', interrupted: false, criteria: CRITERIA }])
    const { result } = renderHook(() =>
      useJdFlow(makeOptions({ initialStage: Stage.JdPending, initialCriteria: CRITERIA })),
    )
    act(() => result.current.setReplyText('approve'))
    await act(() => result.current.handleReplyJd())
    expect(result.current.isLoading).toBe(false)
  })
})
