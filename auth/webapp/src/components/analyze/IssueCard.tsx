import type { Issue, Severity } from '../../types/api';

const SEVERITY_STYLES: Record<Severity, { label: string; chip: string; bar: string }> = {
  critical: { label: 'Critical', chip: 'bg-sev-critical text-white', bar: 'bg-sev-critical' },
  major:    { label: 'Major',   chip: 'bg-sev-major text-white',    bar: 'bg-sev-major' },
  minor:    { label: 'Minor',   chip: 'bg-sev-minor text-white',    bar: 'bg-sev-minor' },
  info:     { label: 'Info',     chip: 'bg-surface-tint text-esprit-grey-light', bar: 'bg-sev-info' },
  unknown:  { label: 'Note',     chip: 'bg-surface-tint text-esprit-grey-light', bar: 'bg-sev-info' },
};

export function IssueCard({ issue, index = 0 }: { issue: Issue; index?: number }) {
  const sev = SEVERITY_STYLES[issue.severity || 'unknown'];

  return (
    <div
      className="relative bg-white border border-border rounded-lg overflow-hidden mb-3 animate-fade-in-up"
      style={{ animationDelay: `${Math.min(index, 10) * 40}ms` }}
    >
      <div className={`absolute left-0 top-0 bottom-0 w-1 ${sev.bar}`} />
      <div className="pl-5 pr-4 py-4">
        <div className="flex justify-between items-baseline gap-3 mb-2">
          <div className="flex items-center gap-2.5">
            <span className={`text-[10px] font-bold uppercase tracking-wide px-2 py-0.5 rounded ${sev.chip}`}>
              {sev.label}
            </span>
            <span className="font-mono text-[12px] text-esprit-grey-light">{issue.rule_id}</span>
          </div>
          {issue.file && <span className="font-mono text-[11px] text-muted">{issue.file}</span>}
        </div>

        <div className="text-[13.5px] text-ink font-semibold leading-snug mb-2">{issue.message}</div>

        {issue.feedback && (
          <div className="text-[13px] leading-relaxed text-esprit-grey-light pt-2.5 border-t border-border">
            {issue.feedback}
          </div>
        )}

        {issue.suggested_fix && (
          <div className="mt-3">
            <span className="eyebrow text-ok block mb-1.5">Suggested fix</span>
            <pre className="bg-[#1B1D21] text-[#D6DCE5] text-[12px] font-mono rounded-lg px-4 py-3 overflow-x-auto leading-relaxed whitespace-pre-wrap">
              {issue.suggested_fix}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
