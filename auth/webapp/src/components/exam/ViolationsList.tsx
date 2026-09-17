import type { ConstraintViolation } from '../../types/api';

export function ViolationsList({ violations }: { violations: ConstraintViolation[] }) {
  return (
    <div>
      <div className="eyebrow text-muted mb-2.5">Constraint violations ({violations.length})</div>
      {violations.length === 0 ? (
        <div className="text-[13px] text-ok py-1.5">No banned functions or imports detected.</div>
      ) : (
        violations.map((v, i) => (
          <div key={i} className="text-[13px] text-esprit-grey-light py-2 border-b border-border flex gap-2.5">
            <span className="font-mono text-[11px] text-esprit-red flex-shrink-0 mt-0.5">{v.type}</span>
            <span>{v.message}</span>
          </div>
        ))
      )}
    </div>
  );
}
