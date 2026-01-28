import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        background: "#050816",
        surface: "#0B1020",
        surfaceSubtle: "#12172A",
        accent: "#7C5CFC",
        accentSoft: "#2E2352",
        accentMuted: "#A396FF",
        borderSubtle: "#252A3F",
        textPrimary: "#F9FAFB",
        textSecondary: "#9CA3AF",
        danger: "#F97373",
        warning: "#FACC15",
        success: "#4ADE80"
      },
      boxShadow: {
        card: "0 18px 45px rgba(0,0,0,0.55)"
      },
      borderRadius: {
        pill: "9999px"
      }
    }
  },
  plugins: []
};

export default config;

