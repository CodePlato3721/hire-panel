import { useEffect, useRef, useState } from 'react'
import { submitFeedback } from '../api'
import type { Resume, SSEEvent } from '../api'

interface Options {
  sessionId: string
  onFeedbackDone: (resumes: Resume[]) => void
}

export function useFeedback({ sessionId, onFeedbackDone }: Options) {
  const [feedbackText, setFeedbackText] = useState('')
  const [streamText, setStreamText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const streamRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (streamRef.current) {
      streamRef.current.scrollTop = streamRef.current.scrollHeight
    }
  }, [streamText])

  function enterStreaming() {
    setStreamText('')
    setIsLoading(true)
  }

  async function handleSubmitFeedback() {
    if (!feedbackText.trim() || isLoading) return
    const text = feedbackText
    setFeedbackText('')
    enterStreaming()
    try {
      await submitFeedback(sessionId, text, (event: SSEEvent) => {
        if (event.type === 'token') {
          setStreamText(prev => prev + event.content)
        } else if (event.type === 'done' && 'hr_memory' in event) {
          onFeedbackDone(event.resumes)
        }
      })
    } finally {
      setIsLoading(false)
    }
  }

  return { feedbackText, setFeedbackText, streamText, streamRef, isLoading, handleSubmitFeedback }
}
