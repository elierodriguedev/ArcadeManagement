import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path' // Import path module

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/', // Set the base path for assets relative to the server root
  build: {
    // Output directory relative to the project root (arcade-agent/react-ui/)
    // This places the build output in arcade-agent/build/react_ui_dist
    // Use path.resolve without __dirname, it resolves relative to the config file location
    outDir: path.resolve('../build/react_ui_dist'),
    emptyOutDir: true, // Clean the output directory before building
  },
})
