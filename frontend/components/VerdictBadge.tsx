import type { Verdict } from "@/lib/types";

const STYLES: Record<Verdict, string> = {
  TRUE: "bg-verdict-true text-white",
  MOSTLY_TRUE: "bg-verdict-mostly_true text-white",
  MIXED: "bg-verdict-mixed text-black",
  MISLEADING: "bg-verdict-misleading text-white",
  FALSE: "bg-verdict-false text-white",
  UNVERIFIABLE: "bg-verdict-unverifiable text-white",
  SATIRE: "bg-verdict-satire text-white",
};

const LABELS: Record<Verdict, string> = {
  TRUE: "True",
  MOSTLY_TRUE: "Mostly true",
  MIXED: "Mixed",
  MISLEADING: "Misleading",
  FALSE: "False",
  UNVERIFIABLE: "Unverifiable",
  SATIRE: "Satire",
};

export function VerdictBadge({ verdict }: { verdict: Verdict }) {
  return (
    <span
      className={`inline-block rounded-full px-3 py-1 text-sm font-semibold tracking-wide ${STYLES[verdict]}`}
    >
      {LABELS[verdict]}
    </span>
  );
}
