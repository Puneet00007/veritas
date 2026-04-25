"use client";

import { useState } from "react";
import type { CheckResult } from "@/lib/types";
import { VerdictBadge } from "./VerdictBadge";
import { ScoreGauge } from "./ScoreGauge";
import { RubricView } from "./RubricBreakdown";
import { EvidenceList } from "./EvidenceList";

type Tab = "evidence" | "rubric" | "claims" | "wrong" | "critic";

export function VerdictCard({ result }: { result: CheckResult }) {
  const [tab, setTab] = useState<Tab>("evidence");
  const mock = Boolean(result.extras?.llm_mock);

  return (
    <article className="rounded-2xl border border-neutral-200 bg-white p-5 shadow-sm dark:border-neutral-800 dark:bg-neutral-950">
      <header className="flex flex-wrap items-center gap-3">
        <VerdictBadge verdict={result.verdict} />
        <ScoreGauge score={result.legitimacy_score} />
        <span className="text-sm text-neutral-500">
          confidence {(result.confidence * 100).toFixed(0)}%
        </span>
      </header>

      <p className="mt-3 text-base leading-relaxed">{result.tl_dr}</p>

      {mock && (
        <p className="mt-2 rounded border border-amber-300 bg-amber-50 p-2 text-xs text-amber-900 dark:border-amber-700 dark:bg-amber-950 dark:text-amber-200">
          Running without an LLM / search API key — verdict is produced by the
          fallback heuristic pipeline. Add keys in <code>backend/.env</code> for
          real answers.
        </p>
      )}

      {result.red_flags.length > 0 && (
        <ul className="mt-2 flex flex-wrap gap-2">
          {result.red_flags.map((f) => (
            <li
              key={f}
              className="rounded-full bg-amber-100 px-2 py-0.5 text-xs text-amber-900 dark:bg-amber-950 dark:text-amber-200"
            >
              ⚑ {f.replaceAll("_", " ")}
            </li>
          ))}
        </ul>
      )}

      <nav className="mt-4 flex gap-1 border-b border-neutral-200 text-sm dark:border-neutral-800">
        {(
          [
            ["evidence", `Evidence (${result.evidence.length})`],
            ["rubric", "Rubric"],
            ["claims", `Claims (${result.claims.length})`],
            ["wrong", "Why might I be wrong?"],
            ["critic", "Critic"],
          ] as [Tab, string][]
        ).map(([id, label]) => (
          <button
            key={id}
            onClick={() => setTab(id)}
            className={`border-b-2 px-3 py-2 transition-colors ${
              tab === id
                ? "border-neutral-900 font-medium dark:border-neutral-100"
                : "border-transparent text-neutral-500 hover:text-neutral-900 dark:hover:text-neutral-100"
            }`}
          >
            {label}
          </button>
        ))}
      </nav>

      <div className="pt-4">
        {tab === "evidence" && (
          <EvidenceList sources={result.sources} evidence={result.evidence} />
        )}
        {tab === "rubric" && <RubricView rubric={result.rubric} />}
        {tab === "claims" && (
          <ol className="list-decimal space-y-2 pl-5 text-sm">
            {result.claims.map((c, i) => (
              <li key={i}>{c.text}</li>
            ))}
          </ol>
        )}
        {tab === "wrong" && (
          <p className="text-sm leading-relaxed text-neutral-700 dark:text-neutral-300">
            {result.why_might_i_be_wrong}
          </p>
        )}
        {tab === "critic" && (
          <p className="text-sm italic text-neutral-700 dark:text-neutral-300">
            {result.critic_notes || "Critic had no concerns."}
          </p>
        )}
      </div>

      <footer className="mt-4 text-xs text-neutral-500">
        trace {result.trace_id} · generated{" "}
        {new Date(result.generated_at).toLocaleString()}
      </footer>
    </article>
  );
}
