export function EmptyState() {
  return (
    <div className="flex flex-col items-start justify-center h-[55%] text-paper-muted">
      <div className="font-mono text-[34px] text-[#D8CFB6] mb-3.5">§</div>
      <p className="text-[13.5px] max-w-[340px] leading-relaxed">
        Submit code on the left. Results — issues, grounded feedback, and for exams, a grade out of 20 —
        will appear here, marked up like a graded paper.
      </p>
    </div>
  );
}

export function LoadingState({ message }: { message: string }) {
  return (
    <div className="flex items-center gap-3 font-mono text-[13px] text-paper-muted py-10">
      <div className="w-3.5 h-3.5 border-2 border-[#D8CFB6] border-t-ink-red rounded-full animate-spin-slow" />
      <span>{message}</span>
    </div>
  );
}

export function ErrorBlock({ message }: { message: string }) {
  return (
    <div className="bg-white border border-ink-red rounded text-ink-red-dim text-[13.5px] leading-relaxed px-4.5 py-4">
      <span className="font-mono font-bold block mb-1.5">Could not complete</span>
      {message}
    </div>
  );
}

export function StatChip({ value, label }: { value: number | string; label: string }) {
  return (
    <div>
      <div className="font-mono text-[22px] font-bold text-[#2B2620] leading-none">{value}</div>
      <div className="text-[11px] uppercase tracking-wider text-paper-muted mt-1">{label}</div>
    </div>
  );
}
