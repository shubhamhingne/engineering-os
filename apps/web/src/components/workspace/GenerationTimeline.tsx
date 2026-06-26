"use client";
import { motion } from "framer-motion";
import { Check, Loader2 } from "lucide-react";
import { cn } from "@/lib/cn";
import { fadeRise, listStagger } from "@/lib/motion";

const STEPS = [
  "Building context",
  "Selecting prompt",
  "Calling the model",
  "Drafting",
  "Formatting Markdown",
  "Version saved",
];

// Live AI timeline. `current` = index of the running step; steps before it are done.
export function GenerationTimeline({ active, current = STEPS.length }: { active: boolean; current?: number }) {
  return (
    <div className="rounded-lg border border-line bg-raised p-3">
      <div className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-text-muted">Generation</div>
      <motion.ul variants={listStagger} initial="hidden" animate="show" className="space-y-1">
        {STEPS.map((step, i) => {
          const done = i < current;
          const running = active && i === current;
          return (
            <motion.li
              key={step}
              variants={fadeRise}
              className={cn("flex items-center gap-2 py-0.5 text-[12.5px]", done || running ? "text-text" : "text-text-muted")}
            >
              <span
                className={cn(
                  "grid h-[15px] w-[15px] place-items-center rounded-full",
                  running ? "bg-accent/20 text-accent-soft" : done ? "bg-success/15 text-success" : "bg-sunken text-text-muted",
                )}
              >
                {running ? <Loader2 className="h-2.5 w-2.5 animate-spin" /> : <Check className="h-2.5 w-2.5" />}
              </span>
              {step}
            </motion.li>
          );
        })}
      </motion.ul>
    </div>
  );
}
