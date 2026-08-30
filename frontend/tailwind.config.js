/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        raycast: {
          bg: '#070709',
          card: '#0e0f14',
          surface: '#14161f',
          surfaceHover: '#1c1e2b',
          border: 'rgba(255, 255, 255, 0.08)',
          borderHover: 'rgba(255, 255, 255, 0.16)',
          red: '#ff6363',
          redGlow: 'rgba(255, 99, 99, 0.25)',
          emerald: '#10b981',
          amber: '#f59e0b',
          purple: '#a855f7',
          cyan: '#06b6d4',
          blue: '#3b82f6',
        },
        brand: {
          50: '#f0f7ff',
          100: '#e0effe',
          500: '#0284c7',
          600: '#0265d6',
          700: '#034ea2',
          900: '#0c2a4d',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      boxShadow: {
        'raycast-card': '0 8px 32px 0 rgba(0, 0, 0, 0.36), inset 0 1px 0 0 rgba(255, 255, 255, 0.08)',
        'raycast-card-hover': '0 12px 40px 0 rgba(0, 0, 0, 0.48), inset 0 1px 0 0 rgba(255, 255, 255, 0.14)',
        'raycast-btn': '0 0 20px -3px rgba(255, 99, 99, 0.35), inset 0 1px 0 0 rgba(255, 255, 255, 0.2)',
        'raycast-glow-cyan': '0 0 25px -4px rgba(6, 182, 212, 0.3)',
        'raycast-glow-emerald': '0 0 25px -4px rgba(16, 185, 129, 0.3)',
      },
      letterSpacing: {
        tightest: '-0.03em',
        tighter: '-0.02em',
      }
    },
  },
  plugins: [],
}

