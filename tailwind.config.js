/** @type {import('tailwindcss').Config} */
module.exports = {
  theme: {
    extend: {
      colors: {
        'theme': {
          light: '#FFF',
          dark: '#373D3B'
          // light: '#9BBFCE',
          // dark: '#373D3B'
        }
      },
    }
  },
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}"
  ],
  
  extend: {},
}
