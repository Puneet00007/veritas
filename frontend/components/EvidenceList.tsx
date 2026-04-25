import type { Evidence, Source } from "@/lib/types";

const STANCE_COLOR: Record<Evidence["stance"], string> = {
  supports: "text-green-700 dark:text-green-400",
  refutes: "text-red-700 dark:text-red-400",
  context: "text-neutral-600 dark:text-neutral-400",
};

const STANCE_LABEL: Record<Evidence["stance"], string> = {
  supports: "↑ supports",
  refutes: "↓ refutes",
  context: "· context",
};

export function EvidenceList({
  sources,
  evidence,
}: {
  sources: Source[];
  evidence: Evidence[];
}) {
  const byId = new Map(sources.map((s) => [s.id, s]));
  if (evidence.length === 0) {
    return (
      <p className="text-sm text-neutral-500">
        No evidence retrieved — try again with a search API key configured.
      </p>
    );
  }
  return (
    <ol className="space-y-3">
      {evidence.map((e, i) => {
        const src = byId.get(e.source_id);
        return (
          <li
            key={i}
            className="rounded-lg border border-neutral-200 bg-white p-3 text-sm dark:border-neutral-800 dark:bg-neutral-900"
          >
            <div className="flex items-center gap-2 text-xs text-neutral-500">
              <span className={STANCE_COLOR[e.stance]}>{STANCE_LABEL[e.stance]}</span>
              <span>·</span>
              <span>{e.agent}</span>
              {src && (
                <>
                  <span>·</span>
                  <span>
                    credibility {(src.credibility * 100).toFixed(0)}% · {src.kind}
                  </span>
                </>
              )}
            </div>
            <blockquote className="mt-1 border-l-2 border-neutral-300 pl-3 text-neutral-700 dark:border-neutral-700 dark:text-neutral-300">
              {e.quote}
            </blockquote>
            {src && (
              <a
                href={src.url}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-1 block truncate text-xs text-blue-600 hover:underline dark:text-blue-400"
              >
                [{src.id}] {src.publisher || src.domain} — {src.title || src.url}
              </a>
            )}
          </li>
        );
      })}
    </ol>
  );
}
