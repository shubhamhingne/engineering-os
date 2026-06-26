"use client";
import { useEffect, useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";

export type Command = {
  id: string;
  label: string;
  group: string;
  shortcut?: string;
  enabled?: boolean;
  run: () => void;
};

// Raycast-style command palette. ⌘K toggles; fuzzy filter; full keyboard navigation.
export function CommandPalette({ commands }: { commands: Command[] }) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [active, setActive] = useState(0);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setOpen((o) => !o);
      } else if (e.key === "Escape") {
        setOpen(false);
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return commands.filter((c) => (c.enabled ?? true) && c.label.toLowerCase().includes(q));
  }, [commands, query]);

  useEffect(() => setActive(0), [query, open]);

  function onKeyDown(e: React.KeyboardEvent) {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActive((a) => Math.min(a + 1, filtered.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActive((a) => Math.max(a - 1, 0));
    } else if (e.key === "Enter") {
      filtered[active]?.run();
      setOpen(false);
    }
  }

  const groups = useMemo(() => {
    const map = new Map<string, Command[]>();
    for (const c of filtered) {
      const arr = map.get(c.group) ?? [];
      arr.push(c);
      map.set(c.group, arr);
    }
    return [...map.entries()];
  }, [filtered]);

  let runningIndex = -1;
  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-[1300] bg-black/60"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={() => setOpen(false)}
        >
          <motion.div
            initial={{ opacity: 0, y: -8, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.16, ease: [0.2, 0, 0, 1] }}
            onClick={(e) => e.stopPropagation()}
            className="mx-auto mt-24 w-[600px] overflow-hidden rounded-xl border border-line bg-overlay shadow-2xl"
            role="dialog"
            aria-label="Command palette"
          >
            <div className="flex items-center gap-3 border-b border-border px-4 py-3.5">
              <span className="text-text-muted">⌕</span>
              <input
                autoFocus
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={onKeyDown}
                placeholder="Search or run a command"
                className="w-full bg-transparent text-[15px] text-text outline-none placeholder:text-text-muted"
              />
              <kbd className="rounded border border-line px-1.5 font-mono text-[11px] text-text-muted">esc</kbd>
            </div>
            <div className="max-h-80 overflow-auto py-1.5">
              {groups.length === 0 && (
                <div className="px-4 py-6 text-center text-sm text-text-muted">No matches</div>
              )}
              {groups.map(([group, items]) => (
                <div key={group}>
                  <div className="px-4 pb-1 pt-2 text-[10.5px] uppercase tracking-wide text-text-muted">{group}</div>
                  {items.map((c) => {
                    runningIndex++;
                    const selected = runningIndex === active;
                    return (
                      <button
                        key={c.id}
                        onMouseEnter={() => setActive(runningIndex)}
                        onClick={() => {
                          c.run();
                          setOpen(false);
                        }}
                        className={
                          "flex w-full items-center gap-3 px-4 py-2 text-left text-[13.5px] " +
                          (selected ? "bg-raised text-text" : "text-text-secondary")
                        }
                      >
                        {c.label}
                        {c.shortcut && <span className="ml-auto font-mono text-[11px] text-text-muted">{c.shortcut}</span>}
                      </button>
                    );
                  })}
                </div>
              ))}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
