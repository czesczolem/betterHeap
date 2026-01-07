// Content script for BetterHeap element labeling

interface LabelingState {
  active: boolean
  intent: string
}

// Utility function to get CSS selector
function getCSSSelector(element: Element): string {
  if (element.id) {
    return `#${element.id}`
  }

  // Build a unique selector path
  const path: string[] = []
  let current: Element | null = element

  while (current && current !== document.body) {
    let selector = current.tagName.toLowerCase()
    
    if (current.className) {
      const classes = Array.from(current.classList)
        .filter(c => !c.startsWith('bh-')) // Exclude BetterHeap classes
        .join('.')
      if (classes) {
        selector += `.${classes}`
      }
    }

    // Add data attributes if present
    const dataAttrs = Array.from(current.attributes)
      .filter(attr => attr.name.startsWith('data-'))
      .map(attr => `[${attr.name}="${attr.value}"]`)
      .join('')
    
    if (dataAttrs) {
      selector += dataAttrs
    }

    path.unshift(selector)
    current = current.parentElement
  }

  return path.join(' > ')
}

let labelingState: LabelingState = {
  active: false,
  intent: '',
}

// Overlay element for highlighting
let overlay: HTMLDivElement | null = null

// Create overlay for element highlighting
function createOverlay() {
  const div = document.createElement('div')
  div.id = 'bh-element-overlay'
  div.style.cssText = `
    position: absolute;
    pointer-events: none;
    border: 2px solid #3b82f6;
    background: rgba(59, 130, 246, 0.1);
    z-index: 999999;
    transition: all 0.1s ease;
    display: none;
  `
  document.body.appendChild(div)
  return div
}

// Highlight element on hover
function highlightElement(element: Element) {
  if (!overlay) overlay = createOverlay()
  
  const rect = element.getBoundingClientRect()
  overlay.style.display = 'block'
  overlay.style.top = `${rect.top + window.scrollY}px`
  overlay.style.left = `${rect.left + window.scrollX}px`
  overlay.style.width = `${rect.width}px`
  overlay.style.height = `${rect.height}px`
}

// Hide overlay
function hideOverlay() {
  if (overlay) {
    overlay.style.display = 'none'
  }
}

// Handle element click during labeling
function handleElementClick(event: MouseEvent) {
  if (!labelingState.active) return
  
  event.preventDefault()
  event.stopPropagation()
  
  const target = event.target as Element
  
  // Ignore our own overlay
  if (target.id === 'bh-element-overlay') return
  
  const selector = getCSSSelector(target)
  const textContent = target.textContent?.trim().slice(0, 50) || ''
  
  const labeledElement = {
    id: Date.now().toString(),
    intent: labelingState.intent,
    selector: selector,
    textContent: textContent,
    pageUrl: window.location.href,
  }
  
  // Send to popup
  chrome.runtime.sendMessage({
    type: 'ELEMENT_LABELED',
    element: labeledElement,
  })
  
  // Stop labeling
  labelingState.active = false
  hideOverlay()
  document.body.style.cursor = 'default'
  
  // Flash element to show it was captured
  const flash = document.createElement('div')
  const rect = target.getBoundingClientRect()
  flash.style.cssText = `
    position: absolute;
    top: ${rect.top + window.scrollY}px;
    left: ${rect.left + window.scrollX}px;
    width: ${rect.width}px;
    height: ${rect.height}px;
    background: rgba(34, 197, 94, 0.3);
    border: 2px solid #22c55e;
    z-index: 999999;
    pointer-events: none;
    animation: bh-flash 0.5s ease-out;
  `
  document.body.appendChild(flash)
  setTimeout(() => flash.remove(), 500)
}

// Handle mouseover during labeling
function handleElementHover(event: MouseEvent) {
  if (!labelingState.active) return
  
  const target = event.target as Element
  if (target.id === 'bh-element-overlay') return
  
  highlightElement(target)
}

// Add flash animation
const style = document.createElement('style')
style.textContent = `
  @keyframes bh-flash {
    0% { opacity: 1; transform: scale(1); }
    100% { opacity: 0; transform: scale(1.05); }
  }
`
document.head.appendChild(style)

// Listen for messages from popup
chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.type === 'START_LABELING') {
    labelingState.active = true
    labelingState.intent = message.intent
    document.body.style.cursor = 'crosshair'
    
    sendResponse({ success: true })
  }
  
  return true
})

// Add event listeners
document.addEventListener('click', handleElementClick, true)
document.addEventListener('mouseover', handleElementHover)
document.addEventListener('mouseout', hideOverlay)

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
  if (overlay) overlay.remove()
})
