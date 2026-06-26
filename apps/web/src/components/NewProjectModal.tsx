"use client";
import { useState } from "react";
import { api } from "@/lib/api";

export function NewProjectModal({ onCreated }: { onCreated: () => void }) {
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [idea, setIdea] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit() {
    setBusy(true);
    setError(null);
    try {
      if (!title.trim() || !idea.trim()) throw new Error("Title and idea are required.");
      await api.createProject(title, idea);
      setOpen(false);
      setTitle("");
      setIdea("");
      onCreated();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <button
        className="rounded-md bg-action px-4 py-2 text-sm font-medium hover:bg-action-hover"
        onClick={() => setOpen(true)}
      >
        + New project
      </button>
      {open && (
        <div
          className="fixed inset-0 flex items-center justify-center bg-black/60"
          onClick={() => setOpen(false)}
        >
          <div
            className="w-[28rem] rounded-lg border border-border bg-raised p-5"
            onClick={(e) => e.stopPropagation()}
          >
            <h2 className="mb-3 font-semibold">New project</h2>
            <input
              className="mb-2 w-full rounded-md border border-border bg-base px-3 py-2 text-sm"
              placeholder="Title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
            <textarea
              className="mb-2 h-24 w-full rounded-md border border-border bg-base px-3 py-2 text-sm"
              placeholder="Describe your idea in a sentence or two…"
              value={idea}
              onChange={(e) => setIdea(e.target.value)}
            />
            {error && <p className="mb-2 text-sm text-[#EF4444]">{error}</p>}
            <div className="flex justify-end gap-2">
              <button className="px-3 py-2 text-sm text-text-secondary" onClick={() => setOpen(false)}>
                Cancel
              </button>
              <button
                disabled={busy}
                className="rounded-md bg-action px-4 py-2 text-sm font-medium hover:bg-action-hover disabled:opacity-50"
                onClick={submit}
              >
                {busy ? "Creating…" : "Create"}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
