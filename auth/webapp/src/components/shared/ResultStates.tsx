export function EmptyState() {
  return (
    <div className="flex flex-col items-start justify-center py-16 text-muted">
      <div className="w-10 h-10 rounded-lg bg-surface-tint flex items-center justify-center mb-4">
        <span className="font-mono text-esprit-red text-lg">§</span>
      </div>
      <p className="text-[13.5px] max-w-sm leading-relaxed">
        Upload a file on the left. Detected issues, pedagogical feedback and — for exams —
        the grade out of 20 will appear here.
      </p>
    </div>
  );
}

export function LoadingState({ message }: { message: string }) {
  return (
    <div className="flex items-center gap-3 text-[13px] text-esprit-grey-light py-10">
      <div className="w-3.5 h-3.5 border-2 border-border border-t-esprit-red rounded-full animate-spin-slow" />
      <span>{message}</span>
    </div>
  );
}

export function ErrorBlock({ message }: { message: string }) {
  return (
    <div className="bg-white border border-esprit-red/30 rounded-lg text-esprit-red text-[13.5px] leading-relaxed px-5 py-4">
      <span className="eyebrow block mb-1.5">Failed</span>
      {message}
    </div>
  );
}

export function StatChip({ value, label }: { value: number | string | null; label: string }) {
  return (
    <div>
      <div className="font-mono text-[22px] font-bold text-ink leading-none">{value ?? '—'}</div>
      <div className="text-[11px] uppercase tracking-wider text-muted mt-1.5">{label}</div>
    </div>
  );
}
