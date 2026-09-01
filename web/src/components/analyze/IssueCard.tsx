import type { Issue, Severity } from '../../types/api';

const SEVERITY_STYLES: Record<Severity, { label: string; bg: string; text: string; border: string }> = {
  critical: { label: 'Critical', bg: 'bg-ink-red', text: 'text-white', border: 'border-l-ink-red' },
  major:    { label: 'Major',    bg: 'bg-chalk-yellow', text: 'text-[#3A2C0A]', border: 'border-l-chalk-yellow' },
  minor:    { label: 'Minor',    bg: 'bg-[#D8CFB6]', text: 'text-[#4A4438]', border: 'border-l-[#B8AE8E]' },
  info:     { label: 'Info',     bg: 'bg-[#E5DCC4]', text: 'text-paper-muted', border: 'border-l-paper-line' },
  unknown:  { label: 'Note',     bg: 'bg-[#E5DCC4]', text: 'text-paper-muted', border: 'border-l-paper-line' },
};

export function IssueCard({ issue, index = 0 }: { issue: Issue; index?: number }) {
  const sev = SEVERITY_STYLES[issue.severity || 'unknown'];

  return (
    <div
      className={`relative bg-white border border-paper-line border-l-3 ${sev.border} rounded px-5 py-4 mb-3.5 animate-fade-in-up shadow-[0_1px_2px_rgba(43,38,32,0.04)]`}
      style={{ animationDelay: `${Math.min(index, 10) * 45}ms` }}
    >
      <div className="flex justify-between items-baseline gap-2.5 mb-2">
        <div className="flex items-center gap-2">
          <span className={`font-mono text-[10px] font-bold uppercase tracking-wide px-2 py-0.5 rounded ${sev.bg} ${sev.text}`}>
            {sev.label}
          </span>
          <span className="font-mono text-xs text-ink-red font-semibold tracking-wide">{issue.rule_id}</span>
        </div>
        {issue.file && <span className="font-mono text-[11px] text-paper-muted">{issue.file}</span>}
      </div>
      <div className="text-[13.5px] text-[#2B2620] font-semibold mb-2 leading-snug">{issue.message}</div>
            {issue.feedback && (
        <div className="text-[13px] leading-relaxed text-[#4A4438] pt-2.5 border-t border-dotted border-paper-line">
          <span className="font-mono text-ink-red text-[11px] mr-1.5 font-medium">note —</span>
          {issue.feedback}
        </div>
      )}
      {issue.suggested_fix && (
        <div className="mt-3">
          <span className="font-mono text-chalk-green text-[11px] font-medium block mb-1.5">suggested fix —</span>
          <pre className="bg-[#1B2622] text-[#C9D6C9] text-[12px] font-mono rounded px-3.5 py-3 overflow-x-auto leading-relaxed whitespace-pre-wrap">
            {issue.suggested_fix}
          </pre>
        </div>
      )}
    </div>
  );
}