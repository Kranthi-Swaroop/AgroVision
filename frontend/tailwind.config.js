export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: "var(--bg-primary)",
        secondary: "var(--bg-secondary)",
        accent: "#FF8C00",
        danger: "#DC2626",
        success: "#16A34A"
      }
    }
  },
  plugins: []
}
