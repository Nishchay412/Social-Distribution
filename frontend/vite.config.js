import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(),
    tailwindcss(),],
  server: {
    host: '::',  // Listen on all IPv6 interfaces (includes IPv4 too)
    port: 5173,
    strictPort: true,
    cors: true,
    proxy: {
      // Proxy API requests to your backend
      '/api': {
        target: 'http://[2605:fd00:4:1001:f816:3eff:fe3e:c88d]:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  },
})