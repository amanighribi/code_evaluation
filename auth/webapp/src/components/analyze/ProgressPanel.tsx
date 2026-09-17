import type { ProgressComparison } from '../../types/api';

const TREND_STYLES = {
  improved:  { label: 'Improved',  chip: 'bg-ok text-white' },
  regressed: { label: 'Regressed',  chip: 'bg-esprit-red text-white' },
  unchanged: { label: 'Unchanged',  chip: 'bg-surface-tint text-esprit-grey-light' },
};

export function ProgressPanel({ progress }: { progress: ProgressComparison }) {
  const style = TREND_STYLES[progress.trend];
  const improved = progress.current_quality_score < progress.previous_quality_score;
  const worse = progress.current_quality_score > progress.previous_quality_score;

  return (
    <div className="bg-white border border-border rounded-lg px-5 py-4 mb-5 animate-fade-in-up">
      <div className="flex items-center justify-between mb-3.5">
        <div className="eyebrow text-esprit-red">Compared to your last submission</div>
        <span className={`text-[10px] font-bold uppercase tracking-wide px-2.5 py-1 rounded ${style.chip}`}>
          {style.label}
        </span>
      </div>

      <div className="flex items-center gap-2.5 mb-4 font-mono text-[14px]">
        <span className="text-muted text-[12px]">Quality score:</span>
        <span className="font-bold text-ink">{progress.previous_quality_score}</span>
        <span className="text-muted">→</span>
        <span className={`font-bold ${improved ? 'text-ok' : worse ? 'text-esprit-red' : 'text-ink'}`}>
          {progress.current_quality_score}
        </span>
        <span className="text-muted text-[11.5px]">(lower is better)</span>
      </div>

      <div className="flex gap-5 text-[12.5px]">
        <div><span className="font-bold text-ok">{progress.resolved_count}</span> <span className="text-muted">resolved</span></div>
        <div><span className="font-bold text-esprit-red">{progress.new_count}</span> <span className="text-muted">new</span></div>
        <div><span className="font-bold text-ink">{progress.persisting_count}</span> <span className="text-muted">still open</span></div>
      </div>

      {progress.resolved_issues.length > 0 && (
        <div className="mt-4 pt-3.5 border-t border-border">
          <div className="eyebrow text-ok mb-2">Resolved since last time</div>
          {progress.resolved_issues.map((issue, i) => (
            <div key={i} className="text-[12.5px] text-esprit-grey-light py-0.5">
              <span className="font-mono text-ok mr-2">{issue.rule_id}</span>{issue.message}
            </div>
          ))}
        </div>
      )}

      {progress.new_issues.length > 0 && (
        <div className="mt-3 pt-3 border-t border-border">
          <div className="eyebrow text-esprit-red mb-2">New since last time</div>
          {progress.new_issues.map((issue, i) => (
            <div key={i} className="text-[12.5px] text-esprit-grey-light py-0.5">
              <span className="font-mono text-esprit-red mr-2">{issue.rule_id}</span>{issue.message}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
