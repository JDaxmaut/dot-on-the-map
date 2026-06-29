/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "../../tours/templates/**/*.html",
    "../../tochka/**/*.html",
  ],
  theme: {
    extend: {
      colors: {
        rice:               "#F4F1EA",
        moss:               "#2C3E2D",
        terracotta:         "#C86B49",
        "terracotta-dark":  "#B65D3D",
        bamboo:             "#D9CDBF",
        "bamboo-line":      "#E3DCCF",
        muted:              "#6F6A5E",
        "muted-2":          "#9A9384",
      },
      fontFamily: {
        serif: ["Cormorant Garamond", "Georgia", "serif"],
        sans:  ["Inter", "system-ui", "sans-serif"],
      },
      letterSpacing: {
        wide:    "0.08em",
        wider:   "0.16em",
        widest:  "0.28em",
      },
      borderRadius: {
        card: "20px",
      },
      boxShadow: {
        zen:    "0 10px 40px rgba(44,62,45,0.05)",
        "zen-lg": "0 20px 60px rgba(44,62,45,0.08)",
      },
      lineHeight: {
        zen: "1.72",
      },
    },
  },
  plugins: [],
};
