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
        sunken: "#0B1220",
        border: "#1E293B",
        line: "#334155",
        text: { DEFAULT: "#F8FAFC", secondary: "#94A3B8", muted: "#64748B", body: "#E2E8F0" },
        action: { DEFAULT: "#2563EB", hover: "#1D4ED8" },
        accent: { DEFAULT: "#06B6D4", soft: "#22D3EE" },
        success: "#22C55E",
        warning: "#F59E0B",
        danger: "#EF4444",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["'JetBrains Mono'", "ui-monospace", "monospace"],
      },
      borderRadius: { md: "8px", lg: "12px" },
    },
  },
  plugins: [],
} satisfies Config;
