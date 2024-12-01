/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [],
  theme: {
    extend: {
      colors: {
        neonGreen: "#39FF14",
        darkGray: "#1A1A1A",
        midnightBlue: "#121063",
      },
      animation: {
        pulseSlow: "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      },
      backgroundImage: {
        gradientRadial: "radial-gradient(circle, #39FF14, #121063)",
      },
    },
  },
  plugins: [],
}

