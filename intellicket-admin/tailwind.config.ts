import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Intellicket Admin Theme Colors
        admin: {
          primary: '#1e40af',      // Blue-700
          secondary: '#64748b',    // Slate-500
          success: '#059669',      // Emerald-600
          warning: '#d97706',      // Amber-600
          danger: '#dc2626',       // Red-600
          info: '#0284c7',         // Sky-600
        },
        background: {
          primary: '#f8fafc',      // Slate-50
          secondary: '#f1f5f9',    // Slate-100
          card: '#ffffff',         // White
          muted: '#f8fafc',        // Slate-50
        },
        border: {
          primary: '#e2e8f0',      // Slate-200
          secondary: '#cbd5e1',    // Slate-300
        },
        text: {
          primary: '#0f172a',      // Slate-900
          secondary: '#475569',    // Slate-600
          muted: '#64748b',        // Slate-500
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Menlo', 'Monaco', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-slow': 'bounce 2s infinite',
        'spin-slow': 'spin 3s linear infinite',
      },
      backdropBlur: {
        xs: '2px',
      },
      boxShadow: {
        'admin-card': '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
        'admin-elevated': '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
      }
    },
  },
  plugins: [],
}

export default config