/** @type {import('tailwindcss').Config} */

module.exports = {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      keyframes: {
        float: {
          "0%": { transform: "translateY(0px)", opacity: 0.3 },
          "50%": { transform: "translateY(20px)", opacity: 0.5 },
          "100%": { transform: "translateY(0px)", opacity: 0.3 },
        },
      },
      animation: {
        float: "float 8s ease-in-out infinite",
        floatSlow: "float 15s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
