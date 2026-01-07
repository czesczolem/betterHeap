import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'
import { copyFileSync, mkdirSync } from 'fs'

export default defineConfig({
  plugins: [
    react(),
    {
      name: 'copy-files',
      closeBundle() {
        // Ensure dist exists
        mkdirSync('dist', { recursive: true })
        // Copy manifest.json, icon.png, and content.css to dist
        copyFileSync('manifest.json', 'dist/manifest.json')
        copyFileSync('icon.png', 'dist/icon.png')
        copyFileSync('src/content/content.css', 'dist/content.css')
      }
    }
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
    },
  },
  build: {
    outDir: 'dist',
    rollupOptions: {
      input: {
        popup: resolve(__dirname, 'popup.html'),
        content: resolve(__dirname, 'src/content/index.tsx'),
        background: resolve(__dirname, 'src/background/index.ts'),
      },
      output: {
        entryFileNames: '[name].js',
        chunkFileNames: 'chunks/[name].js',
        assetFileNames: 'assets/[name].[ext]',
      },
    },
  },
})
