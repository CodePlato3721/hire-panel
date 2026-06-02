import { useEffect, useRef, useState } from 'react'
import { uploadResumes, Stage } from '../api'
import type { Resume, SSEEvent } from '../api'

export const ResumeUiState = {
  Idle: 'idle',
  Streaming: 'streaming',
  Done: 'done',
} as const

export type ResumeUiState = typeof ResumeUiState[keyof typeof ResumeUiState]

function getInitialUiState(stage: Stage): ResumeUiState {
  if (stage === Stage.ResumeDone || stage === Stage.FeedbackDone) return ResumeUiState.Done
  return ResumeUiState.Idle
}

interface Options {
  sessionId: string
  initialStage: Stage
  onResumesDone: (resumes: Resume[]) => void
}

export function useResumeUpload({ sessionId, initialStage, onResumesDone }: Options) {
  const [uiState, setUiState] = useState<ResumeUiState>(() => getInitialUiState(initialStage))
  const [streamText, setStreamText] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)
  const streamRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (streamRef.current) {
      streamRef.current.scrollTop = streamRef.current.scrollHeight
    }
  }, [streamText])

  function triggerFileInput() {
    fileInputRef.current?.click()
  }

  function enterStreaming() {
    setUiState(ResumeUiState.Streaming)
    setStreamText('')
  }

  function enterDone(resumes: Resume[]) {
    onResumesDone(resumes)
    setUiState(ResumeUiState.Done)
  }

  async function handleFilesSelected(files: File[]) {
    if (!files.length) return
    enterStreaming()
    try {
      await uploadResumes(sessionId, files, (event: SSEEvent) => {
        if (event.type === 'token') {
          setStreamText(prev => prev + event.content)
        } else if (event.type === 'done' && 'resumes' in event) {
          enterDone(event.resumes)
        }
      })
    } catch {
      setUiState(ResumeUiState.Idle)
    }
  }

  return {
    uiState,
    streamText,
    streamRef,
    fileInputRef,
    triggerFileInput,
    handleFilesSelected,
  }
}
