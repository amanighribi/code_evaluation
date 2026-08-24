import type { Issue } from '../../types/api';

export function IssueCard({ issue }: { issue: Issue }) {
  return (
    <div className="relative bg-white border border-paper-line border-l-3 border-l-ink-red rounded px-5 py-4 mb-3.5">
      <div className="flex justify-between items-baseline gap-2.5 mb-2">
        <span className="font-mono text-xs text-ink-red font-semibold">{issue.rule_id}</span>
        {issue.file && <span className="font-mono text-[11px] text-paper-muted">{issue.file}</span>}
      </div>
      <div className="text-[13.5px] text-[#2B2620] font-semibold mb-2">{issue.message}</div>
      {issue.feedback && (
        <div className="text-[13px] leading-relaxed text-[#4A4438] pt-2 border-t border-dotted border-paper-line">
          <span className="font-mono text-ink-red text-[11px] mr-1.5">note —</span>
          {issue.feedback}
        </div>
      )}
    </div>
  );
}
