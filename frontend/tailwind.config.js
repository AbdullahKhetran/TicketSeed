/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        surface: "#f7f8fa",
        border: "#e5e7eb",
        muted: "#57606a",
        accent: "#3b82d4",
        secondary: "#7c5cd8",
      },
    },
  },
  plugins: [require("@tailwindcss/typography")],
}
