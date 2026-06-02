import { useEffect, useRef, useState } from 'react'
import { submitJd, replyJd, Stage } from '../api'
import type { ScoringCriteria, SSEEvent } from '../api'

export const JdUiState = {
  Idle: 'idle',
  Input: 'input',
  Streaming: 'streaming',
  Approving: 'approving',
  Done: 'done',
} as const

export type JdUiState = typeof JdUiState[keyof typeof JdUiState]

function getInitialUiState(stage: Stage): JdUiState {
  if (stage === Stage.JdPending) return JdUiState.Approving
  if (stage === Stage.JdDone || stage === Stage.ResumeDone || stage === Stage.FeedbackDone) return JdUiState.Done
  return JdUiState.Idle
}

interface Options {
  sessionId: string
  initialStage: Stage
  initialCriteria: ScoringCriteria[]
  onCriteriaDone: (criteria: ScoringCriteria[]) => void
}

export function useJdFlow({ sessionId, initialStage, initialCriteria, onCriteriaDone }: Options) {
  const [uiState, setUiState] = useState<JdUiState>(() => getInitialUiState(initialStage))
  const [jdText, setJdText] = useState('')
  const [streamText, setStreamText] = useState('')
  const [pendingCriteria, setPendingCriteria] = useState<ScoringCriteria[]>(
    initialStage === Stage.JdPending ? initialCriteria : [],
  )
  const [replyText, setReplyText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const streamRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (streamRef.current) {
      streamRef.current.scrollTop = streamRef.current.scrollHeight
    }
  }, [streamText])

  function startInput() {
    setUiState(JdUiState.Input)
  }

  function cancelInput() {
    setUiState(JdUiState.Idle)
  }

  function enterStreaming() {
    setUiState(JdUiState.Streaming)
    setStreamText('')
    setIsLoading(true)
  }

  function enterApproving(criteria: ScoringCriteria[]) {
    setPendingCriteria(criteria)
    setUiState(JdUiState.Approving)
  }

  async function handleSubmitJd() {
    if (!jdText.trim()) return
    enterStreaming()
    try {
      await submitJd(sessionId, jdText, (event: SSEEvent) => {
        if (event.type === 'token') {
          setStreamText(prev => prev + event.content)
        } else if (event.type === 'done' && 'interrupted' in event) {
          if (event.interrupted) {
            enterApproving(event.criteria)
          } else {
            onCriteriaDone(event.criteria)
            setUiState(JdUiState.Done)
          }
        }
      })
    } finally {
      setIsLoading(false)
    }
  }

  async function handleReplyJd() {
    if (!replyText.trim() || isLoading) return
    enterStreaming()
    try {
      await replyJd(sessionId, replyText, (event: SSEEvent) => {
        if (event.type === 'token') {
          setStreamText(prev => prev + event.content)
        } else if (event.type === 'done' && 'interrupted' in event) {
          onCriteriaDone(event.criteria)
          setUiState(JdUiState.Done)
        }
      })
    } finally {
      setIsLoading(false)
    }
  }

  return {
    uiState,
    jdText,
    setJdText,
    streamText,
    streamRef,
    pendingCriteria,
    replyText,
    setReplyText,
    isLoading,
    startInput,
    cancelInput,
    handleSubmitJd,
    handleReplyJd,
  }
}
