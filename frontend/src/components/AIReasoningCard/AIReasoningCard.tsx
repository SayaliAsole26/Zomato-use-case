interface AIReasoningCardProps {
  reason: string;
  title?: string;
}

export function AIReasoningCard({ reason, title = "CulinaAI Reason" }: AIReasoningCardProps) {
  return (
    <div className="ai-explanation">
      <div className="flex items-center gap-2 mb-1">
        <span className="material-symbols-outlined text-primary text-sm">psychology</span>
        <span className="text-sm font-bold text-on-surface">{title}</span>
      </div>
      <p className="text-base text-on-surface-variant leading-relaxed">&ldquo;{reason}&rdquo;</p>
    </div>
  );
}
