import type { Config } from "tailwindcss";

// Tokens inherited from the Engineering Brand Book / design system.
export default {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        base: "#0F172A",
        raised: "#1E293B",
        overlay: "#273449",
        border: "#334155",
        text: { DEFAULT: "#F8FAFC", secondary: "#94A3B8", muted: "#64748B" },
        action: { DEFAULT: "#2563EB", hover: "#1D4ED8" },
        accent: "#06B6D4",
      },
      borderRadius: { md: "8px", lg: "12px" },
    },
  },
  plugins: [],
} satisfies Config;
