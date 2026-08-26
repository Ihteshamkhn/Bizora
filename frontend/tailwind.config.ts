import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef2ff",
          100: "#e0e7ff",
          200: "#c7d2fe",
          300: "#a5b4fc",
          400: "#818cf8",
          500: "#6366f1",
          600: "#4f46e5",
          700: "#4338ca",
        },
        // Palette from the AI Business Manager UI design
        moss: {
          50: "#F0F7EB",
          100: "#DCEBCF",
          200: "#C8DDB8",
          300: "#A8C594",
          400: "#6E9440",
          500: "#3a6620",
          600: "#2D5016",
          700: "#24400F",
        },
        cream: {
          DEFAULT: "#F7F6F3",
          border: "#E5E0D8",
          muted: "#F3F0EB",
          sand: "#E8DCC8",
        },
      },
    },
  },
  plugins: [],
};
export default config;
