import type { ProgressComparison } from '../../types/api';

const TREND_STYLES = {
  improved:  { label: 'Improved',  bg: 'bg-chalk-green', text: 'text-white' },
  regressed: { label: 'Regressed', bg: 'bg-ink-red', text: 'text-white' },
  unchanged: { label: 'Unchanged', bg: 'bg-chalk-yellow', text: 'text-[#3A2C0A]' },
};

export function ProgressPanel({ progress }: { progress: ProgressComparison }) {
  const style = TREND_STYLES[progress.trend];

  return (
    <div className="bg-white border border-paper-line rounded px-5 py-4 mb-5 animate-fade-in-up">
      <div className="flex items-center justify-between mb-3.5">
        <div className="eyebrow text-ink-red">Compared to your last submission</div>
        <span className={`font-mono text-[10.5px] font-bold uppercase tracking-wide px-2.5 py-1 rounded ${style.bg} ${style.text}`}>
          {style.label}
        </span>
      </div>

      <div className="flex items-center gap-3 mb-4 font-mono text-sm">
        <span className="text-paper-muted">Quality score:</span>
        <span className="font-bold text-[#2B2620]">{progress.previous_quality_score}</span>
        <span className="text-paper-muted">→</span>
        <span className={`font-bold ${progress.current_quality_score < progress.previous_quality_score ? 'text-chalk-green' : progress.current_quality_score > progress.previous_quality_score ? 'text-ink-red' : 'text-[#2B2620]'}`}>
          {progress.current_quality_score}
        </span>
        <span className="text-paper-muted text-xs">(lower is better)</span>
      </div>

      <div className="flex gap-5 text-[12.5px]">
        <div>
          <span className="font-bold text-chalk-green">{progress.resolved_count}</span>{' '}
          <span className="text-paper-muted">resolved</span>
        </div>
        <div>
          <span className="font-bold text-ink-red">{progress.new_count}</span>{' '}
          <span className="text-paper-muted">new</span>
        </div>
        <div>
          <span className="font-bold text-[#2B2620]">{progress.persisting_count}</span>{' '}
          <span className="text-paper-muted">still open</span>
        </div>
      </div>

      {progress.resolved_issues.length > 0 && (
        <div className="mt-3.5 pt-3.5 border-t border-dotted border-paper-line">
          <div className="text-[11px] font-mono text-chalk-green uppercase tracking-wide mb-1.5">✓ Resolved since last time</div>
          {progress.resolved_issues.map((issue, i) => (
            <div key={i} className="text-[12.5px] text-[#4A4438] py-0.5">
              <span className="font-mono text-chalk-green mr-1.5">{issue.rule_id}</span>
              {issue.message}
            </div>
          ))}
        </div>
      )}

      {progress.new_issues.length > 0 && (
        <div className="mt-3 pt-3 border-t border-dotted border-paper-line">
          <div className="text-[11px] font-mono text-ink-red uppercase tracking-wide mb-1.5">⚠ New since last time</div>
          {progress.new_issues.map((issue, i) => (
            <div key={i} className="text-[12.5px] text-[#4A4438] py-0.5">
              <span className="font-mono text-ink-red mr-1.5">{issue.rule_id}</span>
              {issue.message}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}