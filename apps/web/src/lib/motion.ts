import type { Variants } from "framer-motion";

// Shared, purposeful motion. Components reference these — never bespoke inline animations.
export const fadeRise: Variants = {
  hidden: { opacity: 0, y: 4 },
  show: { opacity: 1, y: 0, transition: { duration: 0.18, ease: [0.2, 0, 0, 1] } },
};

export const listStagger: Variants = {
  show: { transition: { staggerChildren: 0.04 } },
};
