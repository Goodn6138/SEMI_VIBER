import { defineConfig } from 'vite';
import path from 'path';

export default defineConfig({
  root: './frontend',
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './frontend')
    }
  },
  build: {
    outDir: '../dist',
    emptyOutDir: true
  },
  server: {
    port: 3000,
    fs: {
      allow: ['..']
    }
  }
});