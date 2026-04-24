"use client";

import { useRef, useState } from "react";
import { streamCheck } from "@/lib/api";
import type { CheckResult, StreamEvent } from "@/lib/types";
import { VerdictCard } from "./VerdictCard";

interface Entry {
  input: string;
  events: StreamEvent[];
  result: CheckResult | null;
  error?: string;
  loading: boolean;
}

export function Chat() {
  const [entries, setEntries] = useState<Entry[]>([]);
  const [value, setValue] = useState("");
  const abortRef = useRef<AbortController | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    const input = value.trim();
    if (!input) return;
    setValue("");

    const controller = new AbortController();
    abortRef.current = controller;

    const entry: Entry = { input, events: [], result: null, loading: true };
    setEntries((prev) => [...prev, entry]);
    const idx = entries.length;

    try {
      const result = await streamCheck(
        input,
        (ev) => {
          setEntries((prev) => {
            const next = [...prev];
            const cur = next[idx];
            if (cur) next[idx] = { ...cur, events: [...cur.events, ev] };
            return next;
          });
        },
        controller.signal
      );
      setEntries((prev) => {
        const next = [...prev];
        const cur = next[idx];
        if (cur) next[idx] = { ...cur, result, loading: false };
        return next;
      });
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      setEntries((prev) => {
        const next = [...prev];
        const cur = next[idx];
        if (cur) next[idx] = { ...cur, loading: false, error: msg };
        return next;
      });
    }
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-3xl flex-col gap-6 px-4 py-8">
      <header>
        <h1 className="text-3xl font-bold tracking-tight">
          Veritas <span className="text-neutral-400">· fact-check anything</span>
        </h1>
        <p className="mt-1 text-sm text-neutral-600 dark:text-neutral-400">
          Paste a claim, article URL, tweet, or Reddit link. Eight agents run in
          parallel — you&apos;ll see live progress, a scored verdict, sources,
          and a built-in &ldquo;why might I be wrong?&rdquo; tab.
        </p>
      </header>

      <ul className="flex flex-col gap-6">
        {entries.map((e, i) => (
          <li key={i} className="flex flex-col gap-3">
            <div className="self-end max-w-[85%] rounded-2xl bg-neutral-900 px-4 py-2 text-sm text-white dark:bg-neutral-100 dark:text-neutral-900">
              {e.input}
            </div>
            <Timeline events={e.events} loading={e.loading} />
            {e.error && (
              <p className="rounded bg-red-100 p-2 text-sm text-red-900 dark:bg-red-950 dark:text-red-200">
                {e.error}
              </p>
            )}
            {e.result && <VerdictCard result={e.result} />}
          </li>
        ))}
      </ul>

      <form onSubmit={submit} className="sticky bottom-0 mt-auto">
        <div className="flex gap-2 rounded-2xl border border-neutral-300 bg-white p-2 shadow-sm dark:border-neutral-700 dark:bg-neutral-900">
          <input
            value={value}
            onChange={(ev) => setValue(ev.target.value)}
            placeholder="Paste a claim or URL…"
            className="flex-1 bg-transparent px-2 py-1 text-sm outline-none"
          />
          <button
            type="submit"
            className="rounded-xl bg-neutral-900 px-4 py-1.5 text-sm font-medium text-white hover:bg-neutral-700 dark:bg-neutral-100 dark:text-neutral-900 dark:hover:bg-neutral-300"
          >
            Check
          </button>
        </div>
      </form>
    </div>
  );
}

function Timeline({
  events,
  loading,
}: {
  events: StreamEvent[];
  loading: boolean;
}) {
  if (events.length === 0 && !loading) return null;
  return (
    <ol className="flex flex-col gap-1 rounded-xl border border-neutral-200 bg-neutral-50 p-3 text-xs text-neutral-700 dark:border-neutral-800 dark:bg-neutral-900 dark:text-neutral-300">
      {events.map((e, i) => (
        <li key={i} className="font-mono">
          <span className="text-neutral-400">▸</span>{" "}
          <span className="font-semibold">{e.name}</span>{" "}
          <span className="text-neutral-500">
            {formatEventSummary(e)}
          </span>
        </li>
      ))}
      {loading && (
        <li className="font-mono text-neutral-400">▸ working…</li>
      )}
    </ol>
  );
}

function formatEventSummary(ev: StreamEvent): string {
  const p = ev.payload as Record<string, unknown>;
  switch (ev.name) {
    case "intake":
      return `kind=${p.kind}${p.url ? ` url=${p.url}` : ""}`;
    case "claims":
      return `${(p.claims as unknown[] | undefined)?.length ?? 0} atomic claim(s)`;
    case "agent_results":
      return `web=${p.web_hits} fact-check=${p.fact_check_hits} reddit=${p.reddit_hits}`;
    case "draft_verdict":
      return `${p.verdict} · score ${p.score} · conf ${Number(p.confidence).toFixed(2)}`;
    case "critic":
      return p.needs_another_round ? "needs another round" : "no concerns";
    case "satire_detected":
      return `domain=${p.domain}`;
    default:
      return "";
  }
}
