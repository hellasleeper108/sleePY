import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        cyber: {
          dark: '#0a0e27',
          darker: '#050815',
          purple: '#6b46c1',
          blue: '#4c1d95',
          teal: '#0d9488',
          'teal-light': '#14b8a6',
          'teal-dark': '#0f766e',
          pink: '#ec4899',
          yellow: '#fbbf24',
          'gray-dark': '#1e293b',
          'gray-medium': '#334155',
          'gray-light': '#475569',
        },
      },
      backgroundImage: {
        'cyber-gradient': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'cyber-dark-gradient': 'linear-gradient(135deg, #0a0e27 0%, #1e293b 100%)',
        'teal-gradient': 'linear-gradient(135deg, #0d9488 0%, #14b8a6 100%)',
        'purple-gradient': 'linear-gradient(135deg, #6b46c1 0%, #4c1d95 100%)',
      },
      boxShadow: {
        'cyber': '0 0 20px rgba(13, 148, 136, 0.3)',
        'cyber-lg': '0 0 40px rgba(13, 148, 136, 0.5)',
        'purple': '0 0 20px rgba(107, 70, 193, 0.3)',
        'pink': '0 0 20px rgba(236, 72, 153, 0.3)',
      },
      animation: {
        'glow': 'glow 2s ease-in-out infinite alternate',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'fade-in': 'fadeIn 0.5s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 20px rgba(13, 148, 136, 0.3)' },
          '100%': { boxShadow: '0 0 40px rgba(13, 148, 136, 0.6)' },
        },
        slideUp: {
          '0%': { transform: 'translateY(100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
};

export default config;
