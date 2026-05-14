// vite.config.mjs (or vite.config.js with "type":"module" in package.json)
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
  },
  server: {
    proxy: {
      '/upload': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
 