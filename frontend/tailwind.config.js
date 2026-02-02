/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Custom dark theme colors
        dark: {
          900: '#0a0a0f',
          800: '#12121a',
          700: '#1a1a24',
          600: '#22222e',
          500: '#2a2a38',
          400: '#3a3a4a',
          300: '#4a4a5c',
          200: '#6a6a7c',
          100: '#8a8a9c',
        },
        accent: {
          primary: '#00d4aa',
          secondary: '#0099ff',
          warning: '#ffaa00',
          danger: '#ff4466',
          success: '#00ff88',
        },
        geo: {
          land: '#1a472a',
          water: '#0a2463',
          urban: '#4a4458',
          vegetation: '#2d5a27',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Menlo', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'slide-up': 'slideUp 0.3s ease-out',
        'fade-in': 'fadeIn 0.3s ease-out',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px #00d4aa, 0 0 10px #00d4aa' },
          '100%': { boxShadow: '0 0 10px #00d4aa, 0 0 20px #00d4aa, 0 0 30px #00d4aa' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
