import type { RubricBreakdown as R } from "@/lib/types";

const LABELS: Record<keyof R, string> = {
  source_credibility: "Source credibility",
  source_diversity: "Source diversity",
  evidence_strength: "Evidence strength",
  fact_checker_consensus: "Fact-checker consensus",
  media_authenticity: "Media authenticity",
  temporal_integrity: "Temporal integrity",
  original_source_traceability: "Original source traceability",
};

const WEIGHTS: Record<keyof R, number> = {
  source_credibility: 25,
  source_diversity: 10,
  evidence_strength: 25,
  fact_checker_consensus: 15,
  media_authenticity: 10,
  temporal_integrity: 5,
  original_source_traceability: 10,
};

export function RubricView({ rubric }: { rubric: R }) {
  return (
    <div className="space-y-2 text-sm">
      {(Object.keys(LABELS) as (keyof R)[]).map((k) => {
        const v = Math.round(rubric[k]);
        return (
          <div key={k} className="flex items-center gap-3">
            <div className="w-56 shrink-0 text-neutral-600 dark:text-neutral-400">
              {LABELS[k]}{" "}
              <span className="text-xs text-neutral-400">(×{WEIGHTS[k]}%)</span>
            </div>
            <div className="relative h-2 flex-1 overflow-hidden rounded-full bg-neutral-200 dark:bg-neutral-800">
              <div
                className="absolute left-0 top-0 h-full rounded-full bg-neutral-900 dark:bg-neutral-100"
                style={{ width: `${v}%` }}
              />
            </div>
            <div className="w-10 text-right tabular-nums">{v}</div>
          </div>
        );
      })}
    </div>
  );
}
