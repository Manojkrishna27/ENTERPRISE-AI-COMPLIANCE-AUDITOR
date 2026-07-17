/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0F172A', // Slate 900
        card: '#1E293B', // Slate 800
        border: '#334155', // Slate 700
        text: {
          primary: '#F8FAFC', // Slate 50
          secondary: '#94A3B8', // Slate 400
          muted: '#64748B' // Slate 500
        },
        brand: {
          light: '#818CF8', // Indigo 400
          DEFAULT: '#6366F1', // Indigo 500
          dark: '#4F46E5' // Indigo 600
        },
        risk: {
          high: '#EF4444', // Red 500
          medium: '#F59E0B', // Amber 500
          low: '#3B82F6' // Blue 500
        }
      }
    },
  },
  plugins: [],
}
