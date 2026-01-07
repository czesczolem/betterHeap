import { useState, useEffect } from 'react'
import { ChatInterface } from '@/components/ChatInterface'
import { LabelingMode, LabeledElement } from '@/components/LabelingMode'

type AppMode = 'chat' | 'labeling' | 'complete'

interface AppState {
  mode: AppMode
  labeledElements: LabeledElement[]
}

function App() {
  const [mode, setMode] = useState<AppMode>('chat')
  const [labeledElements, setLabeledElements] = useState<LabeledElement[]>([])
  const [isLoading, setIsLoading] = useState(true)

  // Restore state from storage on mount
  useEffect(() => {
    chrome.storage.local.get(['appState'], (result) => {
      if (result.appState) {
        const state: AppState = result.appState
        setMode(state.mode)
        setLabeledElements(state.labeledElements)
      }
      setIsLoading(false)
    })
  }, [])

  // Persist state whenever it changes
  useEffect(() => {
    if (!isLoading) {
      const state: AppState = { mode, labeledElements }
      chrome.storage.local.set({ appState: state })
    }
  }, [mode, labeledElements, isLoading])

  const handleStartLabeling = () => {
    setMode('labeling')
  }

  const handleLabelingComplete = (elements: LabeledElement[]) => {
    setLabeledElements(elements)
    setMode('complete')
    // TODO: Send data to backend API
    console.log('Labeled elements:', elements)
  }

  const handleCancelLabeling = () => {
    setMode('chat')
  }

  if (isLoading) {
    return (
      <div className="w-full h-screen flex items-center justify-center">
        <div className="text-sm text-muted-foreground">Loading...</div>
      </div>
    )
  }

  return (
    <div className="w-full h-screen flex flex-col">
      {mode === 'chat' && (
        <ChatInterface onStartLabeling={handleStartLabeling} />
      )}
      
      {mode === 'labeling' && (
        <LabelingMode
          onComplete={handleLabelingComplete}
          onCancel={handleCancelLabeling}
        />
      )}
      
      {mode === 'complete' && (
        <div className="flex flex-col items-center justify-center h-full p-6 text-center">
          <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mb-4">
            <svg className="w-8 h-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="text-lg font-semibold mb-2">Setup Complete!</h2>
          <p className="text-sm text-muted-foreground mb-4">
            We've labeled {labeledElements.length} elements and are generating your analytics taxonomy.
          </p>
          <p className="text-xs text-muted-foreground">
            You'll receive a confirmation once your setup is ready.
          </p>
        </div>
      )}
    </div>
  )
}

export default App
