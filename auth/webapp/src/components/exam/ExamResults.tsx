import type { ExamEvaluationResponse } from '../../types/api';
import { GradeStamp } from './GradeStamp';
import { ViolationsList } from './ViolationsList';
import { TestResultsTable } from './TestResultsTable';

export function ExamResults({ data }: { data: ExamEvaluationResponse }) {
  const { evaluation, constraint_violations, test_results } = data;

  return (
    <div className="animate-fade-in-up">
      <GradeStamp evaluation={evaluation} />
      <ViolationsList violations={constraint_violations} />
      {test_results.length > 0 && <TestResultsTable results={test_results} />}

      <div className="eyebrow text-muted mt-6 mb-2.5">Instructor feedback</div>
      <FeedbackBlock label="Approach" text={evaluation.approach_assessment} />
      <FeedbackBlock label="Correctness" text={evaluation.correctness_notes} />
      <FeedbackBlock label="Feedback" text={evaluation.feedback} />
    </div>
  );
}

function FeedbackBlock({ label, text }: { label: string; text: string }) {
  return (
    <div className="bg-white border border-border rounded-lg px-5 py-4 text-[13.5px] leading-relaxed text-ink mt-2.5">
      <span className="eyebrow text-esprit-red block mb-1.5">{label}</span>
      {text || '—'}
    </div>
  );
}
