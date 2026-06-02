import { renderHook, act } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import { useResumeUpload, ResumeUiState } from './useResumeUpload'
import { Stage } from '../api'
import type { Resume, SSEEvent } from '../api'

vi.mock('../api', async importOriginal => {
  const actual = await importOriginal<typeof import('../api')>()
  return { ...actual, uploadResumes: vi.fn() }
})

import { uploadResumes } from '../api'

const SESSION_ID = 'test-session'
const RESUMES: Resume[] = [
  { filename: 'alice.pdf', content: '', total_score: 42, reason: 'Strong Python', detail: '' },
  { filename: 'bob.txt', content: '', total_score: 35, reason: 'Good LLM exp', detail: '' },
]

function makeOptions(overrides?: Partial<Parameters<typeof useResumeUpload>[0]>) {
  return {
    sessionId: SESSION_ID,
    initialStage: Stage.JdDone,
    onResumesDone: vi.fn(),
    ...overrides,
  }
}

function mockSSE(events: SSEEvent[]) {
  vi.mocked(uploadResumes).mockImplementation(async (_sid, _files, onEvent) => {
    for (const e of events) onEvent(e)
  })
}

beforeEach(() => vi.clearAllMocks())

describe('initial uiState', () => {
  it('is Idle when stage is jd_done', () => {
    const { result } = renderHook(() => useResumeUpload(makeOptions()))
    expect(result.current.uiState).toBe(ResumeUiState.Idle)
  })

  it('is Done when stage is resume_done', () => {
    const { result } = renderHook(() =>
      useResumeUpload(makeOptions({ initialStage: Stage.ResumeDone })),
    )
    expect(result.current.uiState).toBe(ResumeUiState.Done)
  })

  it('is Done when stage is feedback_done', () => {
    const { result } = renderHook(() =>
      useResumeUpload(makeOptions({ initialStage: Stage.FeedbackDone })),
    )
    expect(result.current.uiState).toBe(ResumeUiState.Done)
  })
})

describe('handleFilesSelected', () => {
  it('does nothing when file list is empty', async () => {
    const { result } = renderHook(() => useResumeUpload(makeOptions()))
    await act(() => result.current.handleFilesSelected([]))
    expect(result.current.uiState).toBe(ResumeUiState.Idle)
  })

  it('streams tokens into streamText', async () => {
    mockSSE([
      { type: 'token', content: 'scoring' },
      { type: 'token', content: '...' },
      { type: 'done', resumes: RESUMES },
    ])
    const { result } = renderHook(() => useResumeUpload(makeOptions()))
    await act(() => result.current.handleFilesSelected([new File([''], 'cv.pdf')]))
    expect(result.current.streamText).toBe('scoring...')
  })

  it('transitions to Done', async () => {
    mockSSE([{ type: 'done', resumes: RESUMES }])
    const { result } = renderHook(() => useResumeUpload(makeOptions()))
    await act(() => result.current.handleFilesSelected([new File([''], 'cv.pdf')]))
    expect(result.current.uiState).toBe(ResumeUiState.Done)
  })

  it('falls back to Idle on upload error', async () => {
    vi.mocked(uploadResumes).mockRejectedValue(new Error('network error'))
    const { result } = renderHook(() => useResumeUpload(makeOptions()))
    await act(() => result.current.handleFilesSelected([new File([''], 'cv.pdf')]))
    expect(result.current.uiState).toBe(ResumeUiState.Idle)
  })
})
