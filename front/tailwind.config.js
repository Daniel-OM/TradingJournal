/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#6366f1',
        secondary: '#8b5cf6',
        success: '#10b981',
        warning: '#f59e0b',
        danger: '#ef4444',
        info: '#06b6d4',
        profit: '#20b26c',
        loss: '#eb2323',
        'dark-color': '#f8fafc',
        'light-color': '#1f2937',
        'bg-color': '#171f29',
        'card-bg': '#1f2937',
        'text-muted': '#818181',
      },
      borderRadius: {
        pill: '20px',
      },
      boxShadow: {
        custom: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
      },
    },
  },
  plugins: [],
  darkMode: 'class',
}
