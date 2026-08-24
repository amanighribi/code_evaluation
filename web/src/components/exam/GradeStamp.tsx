import type { Evaluation } from '../../types/api';

export function GradeStamp({ evaluation }: { evaluation: Evaluation }) {
  const isPass = evaluation.meets_requirements === 'yes';
  const grade = evaluation.grade_out_of_20;

  const verdictColor =
    evaluation.meets_requirements === 'yes' ? 'text-chalk-green' :
    evaluation.meets_requirements === 'partially' ? 'text-chalk-yellow' :
    'text-ink-red';

  return (
    <div className="flex items-center gap-6 mb-6.5 pb-5.5 border-b border-dashed border-[#D8CFB6]">
      <div
        className={`relative w-24 h-24 rounded-full border-[3px] flex flex-col items-center justify-center font-mono flex-shrink-0 -rotate-[8deg] ${
          isPass ? 'border-chalk-green text-chalk-green' : 'border-ink-red text-ink-red'
        }`}
      >
        <div
          className={`absolute inset-1.5 rounded-full border opacity-50 ${
            isPass ? 'border-chalk-green' : 'border-ink-red'
          }`}
        />
        <span className="text-[26px] font-bold leading-none">{grade ?? '—'}</span>
        <span className="text-[11px] opacity-85">/ 20</span>
      </div>
      <div>
        <div className="font-mono text-[11px] uppercase tracking-wider text-paper-muted mb-1">
          Meets requirements
        </div>
        <div className={`font-mono text-base font-bold capitalize ${verdictColor}`}>
          {evaluation.meets_requirements}
        </div>
      </div>
    </div>
  );
}
