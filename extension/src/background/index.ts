// Background service worker for Chrome extension

// Install event
chrome.runtime.onInstalled.addListener(() => {
  console.log('BetterHeap extension installed')
})

// Handle messages from content scripts and popup
chrome.runtime.onMessage.addListener((message) => {
  // Relay messages between content script and popup if needed
  if (message.type === 'ELEMENT_LABELED') {
    // Forward to popup or store in chrome.storage
    chrome.storage.local.get(['labeledElements'], (result) => {
      const elements = result.labeledElements || []
      elements.push(message.element)
      chrome.storage.local.set({ labeledElements: elements })
    })
  }
  
  return true
})

export {}
