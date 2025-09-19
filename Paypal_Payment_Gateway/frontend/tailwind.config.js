/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'paypal-blue': '#0070ba',
        'paypal-dark-blue': '#003087',
        'paypal-yellow': '#ffc439',
      },
    },
  },
  plugins: [],
}
