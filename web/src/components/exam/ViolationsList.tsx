import type { ConstraintViolation } from '../../types/api';

export function ViolationsList({ violations }: { violations: ConstraintViolation[] }) {
  return (
    <div>
      <div className="font-mono text-xs uppercase tracking-wider text-paper-muted mb-2.5">
        Constraint violations ({violations.length})
      </div>
      {violations.length === 0 ? (
        <div className="text-[13px] text-chalk-green py-2">No banned functions or imports detected.</div>
      ) : (
        violations.map((v, i) => (
          <div key={i} className="text-[13px] text-[#4A4438] py-2 border-b border-paper-2 flex gap-2">
            <span className="font-mono text-[11px] text-ink-red flex-shrink-0">{v.type}</span>
            <span>{v.message}</span>
          </div>
        ))
      )}
    </div>
  );
}
