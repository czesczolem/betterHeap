import { useState, useEffect } from 'react'
import { Target, Check, X } from 'lucide-react'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'

export interface LabeledElement {
  id: string
  intent: string
  selector: string
  textContent: string
  pageUrl: string
}

interface LabelingModeProps {
  onComplete: (elements: LabeledElement[]) => void
  onCancel: () => void
}

export function LabelingMode({ onComplete, onCancel }: LabelingModeProps) {
  const [labeledElements, setLabeledElements] = useState<LabeledElement[]>([])
  const [currentIntent, setCurrentIntent] = useState('')
  const [isWaitingForClick, setIsWaitingForClick] = useState(false)

  // Load existing labeled elements from storage on mount
  useEffect(() => {
    chrome.storage.local.get(['labeledElements'], (result) => {
      if (result.labeledElements && Array.isArray(result.labeledElements)) {
        setLabeledElements(result.labeledElements)
      }
    })
    
    // Always reset the waiting state when popup opens
    setIsWaitingForClick(false)
    setCurrentIntent('')
  }, [])

  // Persist only labeled elements to storage (not UI state)
  useEffect(() => {
    chrome.storage.local.set({ labeledElements })
  }, [labeledElements])

  const startLabelingElement = () => {
    if (!currentIntent.trim()) return
    
    setIsWaitingForClick(true)
    
    // Send message to content script to enable element selection
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]?.id) {
        chrome.tabs.sendMessage(tabs[0].id, {
          type: 'START_LABELING',
          intent: currentIntent.trim(),
        })
        // Close popup so user can interact with the page
        window.close()
      }
    })
  }

  const removeElement = (id: string) => {
    setLabeledElements(prev => prev.filter(el => el.id !== id))
  }

  const handleComplete = () => {
    if (labeledElements.length > 0) {
      // Clear labeling state from storage
      chrome.storage.local.remove(['labeledElements'])
      onComplete(labeledElements)
    }
  }

  // Listen for messages from content script
  useEffect(() => {
    const listener = (message: any) => {
      if (message.type === 'ELEMENT_LABELED') {
        setLabeledElements(prev => [...prev, message.element])
        setCurrentIntent('')
        setIsWaitingForClick(false)
      }
    }
    
    chrome.runtime.onMessage.addListener(listener)
    
    return () => {
      chrome.runtime.onMessage.removeListener(listener)
    }
  }, [])

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b bg-gradient-to-r from-primary/5 to-primary/10">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Target className="w-5 h-5 text-primary" />
            <h2 className="text-sm font-semibold">Label Elements</h2>
          </div>
          <div className="text-xs font-medium text-primary bg-primary/10 px-2 py-1 rounded">
            {labeledElements.length} labeled
          </div>
        </div>
        <p className="text-xs text-muted-foreground">
          {isWaitingForClick 
            ? '👉 Click an element on the page to label it'
            : 'Describe what an element does, then click it on your page'
          }
        </p>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Input for new label */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm">Add New Element</CardTitle>
            <CardDescription className="text-xs">
              Describe what this element does (e.g., "added to cart")
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <Input
              value={currentIntent}
              onChange={(e) => setCurrentIntent(e.target.value)}
              placeholder="e.g., added_to_cart, checkout_started"
              disabled={isWaitingForClick}
            />
            <Button
              onClick={startLabelingElement}
              disabled={!currentIntent.trim() || isWaitingForClick}
              className="w-full"
              size="sm"
            >
              {isWaitingForClick ? 'Waiting for click...' : 'Label Element (popup will close)'}
            </Button>
          </CardContent>
        </Card>

        {/* Labeled elements list */}
        {labeledElements.length > 0 && (
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">
                Labeled Elements ({labeledElements.length})
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {labeledElements.map((element) => (
                <div
                  key={element.id}
                  className="flex items-start gap-2 p-2 rounded-md border bg-muted/50"
                >
                  <Check className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium truncate">{element.intent}</p>
                    <p className="text-xs text-muted-foreground truncate">
                      {element.textContent}
                    </p>
                  </div>
                  <button
                    onClick={() => removeElement(element.id)}
                    className="text-muted-foreground hover:text-destructive flex-shrink-0"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        {/* Instructions */}
        <Card className="bg-primary/5 border-primary/20">
          <CardContent className="pt-4">
            <p className="text-xs text-muted-foreground">
              💡 <strong>Tip:</strong> Label 3-5 key elements like buttons, links, or forms 
              that represent important user actions.
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Footer */}
      <div className="p-4 border-t bg-background space-y-2">
        <Button
          onClick={handleComplete}
          disabled={labeledElements.length === 0}
          className="w-full"
        >
          Complete Setup ({labeledElements.length} elements)
        </Button>
        <div className="flex gap-2">
          <Button
            onClick={onCancel}
            variant="ghost"
            className="flex-1"
          >
            Back to Chat
          </Button>
          {labeledElements.length > 0 && (
            <Button
              onClick={() => {
                setLabeledElements([])
                chrome.storage.local.remove(['labeledElements'])
              }}
              variant="outline"
              className="flex-1"
            >
              Clear All
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}
