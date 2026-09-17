import type { Evaluation } from '../../types/api';

export function GradeStamp({ evaluation }: { evaluation: Evaluation }) {
  const isPass = evaluation.meets_requirements === 'yes';
  const partial = evaluation.meets_requirements === 'partially';
  const grade = evaluation.grade_out_of_20;

  const ring = isPass ? 'border-ok text-ok' : partial ? 'border-sev-major text-sev-major' : 'border-esprit-red text-esprit-red';
  const verdictColor = isPass ? 'text-ok' : partial ? 'text-sev-major' : 'text-esprit-red';
  const verdictLabel = isPass ? 'Yes' : partial ? 'Partially' : 'No';

  return (
    <div className="flex items-center gap-6 mb-6 pb-5 border-b border-border">
      <div className={`w-24 h-24 rounded-full border-[3px] flex flex-col items-center justify-center font-mono flex-shrink-0 ${ring}`}>
        <span className="text-[27px] font-bold leading-none">{grade ?? '—'}</span>
        <span className="text-[10.5px] opacity-75 mt-0.5">out of 20</span>
      </div>
      <div>
        <div className="eyebrow text-muted mb-1.5">Meets requirements</div>
        <div className={`text-[17px] font-bold ${verdictColor}`}>{verdictLabel}</div>
      </div>
    </div>
  );
}
