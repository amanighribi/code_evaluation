import type { AnalyzeResponse } from '../../types/api';
import { isProjectAnalysis } from '../../types/api';
import { IssueCard } from './IssueCard';
import { ProgressPanel } from './ProgressPanel';
import { StatChip } from '../shared/ResultStates';

export function AnalyzeResults({ data }: { data: AnalyzeResponse }) {
  const isProject = isProjectAnalysis(data);
  const issues = data.issues;
  const totalIssues = isProject ? data.total_issues : issues.length;
  const linesOfCode = isProject ? data.total_lines_of_code : data.lines_of_code;

  return (
    <div>
      {data.progress && <ProgressPanel progress={data.progress} />}

      <div className="flex gap-8 pb-5 mb-5 border-b border-border flex-wrap">
        {isProject && <StatChip value={data.files_analyzed} label="files analysed" />}
        <StatChip value={totalIssues} label="issues found" />
        <StatChip value={linesOfCode} label="lines of code" />
      </div>

      {issues.length === 0 ? (
        <div className="bg-white border border-border rounded-lg px-5 py-4 text-[13.5px] text-ink">
          <span className="eyebrow text-ok block mb-1.5">Clean run</span>
          No issues were detected in this file.
        </div>
      ) : (
        issues.map((issue, i) => <IssueCard key={`${issue.rule_id}-${i}`} issue={issue} index={i} />)
      )}
    </div>
  );
}
