export default function SignalBadge({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  return <span aria-label={`signal-${pct}`}>{pct}%</span>;
}
