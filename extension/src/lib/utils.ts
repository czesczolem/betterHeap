import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function getCSSSelector(element: Element): string {
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
