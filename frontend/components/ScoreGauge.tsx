export function ScoreGauge({ score }: { score: number }) {
  const color =
    score >= 75
      ? "#16a34a"
      : score >= 55
        ? "#eab308"
        : score >= 35
          ? "#f97316"
          : "#dc2626";
  const pct = Math.max(0, Math.min(100, score));
  return (
    <div className="flex items-center gap-3">
      <div className="relative h-2 w-40 overflow-hidden rounded-full bg-neutral-300 dark:bg-neutral-700">
        <div
          className="absolute left-0 top-0 h-full rounded-full transition-all"
          style={{ width: `${pct}%`, background: color }}
        />
      </div>
      <span className="text-sm font-medium tabular-nums">
        {pct}<span className="text-neutral-500">/100</span>
      </span>
    </div>
  );
}
