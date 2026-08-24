import type { ExamEvaluationResponse } from '../../types/api';
import { GradeStamp } from './GradeStamp';
import { ViolationsList } from './ViolationsList';
import { TestResultsTable } from './TestResultsTable';

export function ExamResults({ data }: { data: ExamEvaluationResponse }) {
  const { evaluation, constraint_violations, test_results } = data;

  return (
    <div>
      <GradeStamp evaluation={evaluation} />
      <ViolationsList violations={constraint_violations} />
      {test_results.length > 0 && <TestResultsTable results={test_results} />}

      <div className="font-mono text-xs uppercase tracking-wider text-paper-muted mt-5.5 mb-2.5">
        Instructor feedback
      </div>
      <FeedbackBlock label="Approach" text={evaluation.approach_assessment} />
      <FeedbackBlock label="Correctness" text={evaluation.correctness_notes} />
      <FeedbackBlock label="Feedback" text={evaluation.feedback} />
    </div>
  );
}

function FeedbackBlock({ label, text }: { label: string; text: string }) {
  return (
    <div className="bg-white border border-paper-line rounded px-4.5 py-4 text-[13.5px] leading-relaxed text-[#2B2620] mt-2">
      <span className="font-mono text-[11px] text-ink-red uppercase tracking-wide block mb-1.5">{label}</span>
      {text || '—'}
    </div>
  );
}
