import type { AnalyzeResponse } from '../../types/api';
import { isProjectAnalysis } from '../../types/api';
import { IssueCard } from './IssueCard';
import { StatChip } from '../shared/ResultStates';

export function AnalyzeResults({ data }: { data: AnalyzeResponse }) {
  const isProject = isProjectAnalysis(data);
  const issues = data.issues;
  const totalIssues = isProject ? data.total_issues : issues.length;
  const linesOfCode = isProject ? data.total_lines_of_code : data.lines_of_code;

  return (
    <div>
      <div className="flex gap-6 pb-5 mb-5.5 border-b border-dashed border-[#D8CFB6] flex-wrap">
        {isProject && <StatChip value={data.files_analyzed} label="files analyzed" />}
        <StatChip value={totalIssues} label="issues found" />
        <StatChip value={linesOfCode} label="lines of code" />
      </div>

      {issues.length === 0 ? (
        <div className="bg-white border border-paper-line rounded px-4.5 py-4 text-[13.5px] leading-relaxed text-[#2B2620]">
          <span className="font-mono text-ink-red text-[11px] uppercase tracking-wide block mb-1.5">
            Clean run
          </span>
          No issues detected by the analyzer.
        </div>
      ) : (
        issues.map((issue, i) => <IssueCard key={`${issue.rule_id}-${i}`} issue={issue} />)
      )}
    </div>
  );
}
