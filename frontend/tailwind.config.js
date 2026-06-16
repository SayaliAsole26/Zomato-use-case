/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: "#b12037",
        secondary: "#1c6c40",
        tertiary: "#006a45",
        surface: "#fff8f7",
        background: "#fff8f7",
        "on-surface": "#261818",
        "on-surface-variant": "#594041",
        "on-primary": "#ffffff",
        "outline-variant": "#e1bebe",
        "surface-container": "#ffe9e8",
        "surface-container-low": "#fff0f0",
        "surface-container-high": "#fde2e2",
        "surface-container-highest": "#f7dcdc",
        "surface-variant": "#f7dcdc",
        "primary-container": "#d43b4d",
        "primary-fixed": "#ffdada",
        "tertiary-container": "#008558",
        "on-tertiary-container": "#f6fff6",
        "inverse-surface": "#3c2c2d",
        "inverse-on-surface": "#ffedec",
        "error-container": "#ffdad6",
        "on-error-container": "#93000a",
      },
      fontFamily: {
        sans: ["Plus Jakarta Sans", "system-ui", "sans-serif"],
      },
      maxWidth: {
        "container-max": "1200px",
      },
      boxShadow: {
        card: "0 4px 20px rgba(26, 26, 26, 0.05)",
        "card-hover": "0 8px 30px rgba(26, 26, 26, 0.08)",
      },
    },
  },
  plugins: [],
};
