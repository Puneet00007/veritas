import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        verdict: {
          true: "#16a34a",
          mostly_true: "#22c55e",
          mixed: "#eab308",
          misleading: "#f97316",
          false: "#dc2626",
          unverifiable: "#6b7280",
          satire: "#a855f7",
        },
      },
    },
  },
  plugins: [],
};
export default config;
