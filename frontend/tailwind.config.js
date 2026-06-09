/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        'campus-navy': '#011025',
        'campus-primary': '#052659',
        'campus-secondary': '#5482B4',
        'campus-muted': '#7EA0C5',
        'campus-surface': '#C2E8FF',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      }
    }
  },
  plugins: [],
}