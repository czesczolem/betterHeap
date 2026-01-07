# BetterHeap Chrome Extension

AI-guided analytics setup via conversational interface and visual element labeling.

## Features

- 🤖 **Conversational Setup**: Chat with AI to describe your product and analytics goals
- 🎯 **Visual Element Labeling**: Click elements on your page to track them
- 🎨 **Clean UI**: Built with shadcn/ui components and Tailwind CSS
- ⚡ **Fast**: Built with Vite and React for optimal performance

## Development

### Install Dependencies

```bash
npm install
```

### Build Extension

```bash
# Development build with watch mode
npm run watch

# Production build
npm run build
```

### Load Extension in Chrome

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `dist` folder from this directory

### Development Workflow

1. Run `npm run watch` to start the build watcher
2. Make changes to source files in `src/`
3. Extension will rebuild automatically
4. Click refresh icon in `chrome://extensions/` to reload the extension
5. Test changes in the popup or on web pages

## Project Structure

```
extension/
├── src/
│   ├── popup/              # Extension popup UI
│   │   ├── App.tsx         # Main app component
│   │   └── index.tsx       # Entry point
│   ├── content/            # Content scripts (run on web pages)
│   │   ├── index.tsx       # Element labeling logic
│   │   └── content.css     # Content script styles
│   ├── background/         # Background service worker
│   │   └── index.ts
│   ├── components/         # React components
│   │   ├── ChatInterface.tsx
│   │   ├── LabelingMode.tsx
│   │   └── ui/            # shadcn/ui components
│   ├── lib/
│   │   └── utils.ts       # Utility functions (CSS selector, etc.)
│   └── styles/
│       └── globals.css    # Global styles and theme
├── manifest.json          # Chrome extension manifest
├── popup.html            # Popup HTML template
└── vite.config.ts        # Vite configuration
```

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **shadcn/ui** - Component library
- **Lucide React** - Icons

## Usage

1. Click the BetterHeap extension icon in Chrome
2. Chat with the AI about your product and analytics goals
3. Click "Start Labeling Elements"
4. Enter a name for the action (e.g., "added_to_cart")
5. Click the element on your webpage you want to track
6. Repeat for all key elements
7. Click "Complete Setup"

## Next Steps

- [ ] Connect to backend API for chat responses
- [ ] Implement taxonomy generation
- [ ] Add PostHog integration
- [ ] Add authentication
- [ ] Add setup progress persistence
