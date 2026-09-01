// Types mirroring the FastAPI backend's response shapes.
// Kept in sync manually with backend/main.py, static_analysis/analyzer.py,
// and exam_mode/full_exam_pipeline.py.

export type Severity = 'critical' | 'major' | 'minor' | 'info' | 'unknown';

export interface Issue {
  rule_id: string;
  message: string;
  file?: string;
  feedback?: string | null;
  suggested_fix?: string | null;
  severity?: Severity;
}
export interface FunctionInfo {
  name: string;
  line: number;
  num_params: number;
  length: number | null;
  cyclomatic_complexity: number;
  has_docstring: boolean;
}

export interface ClassInfo {
  name: string;
  line: number;
}

/** Response shape for a single-file POST /analyze request. */
export interface SingleFileAnalysis {
  lines_of_code: number;
  num_functions: number;
  num_classes: number;
  functions: FunctionInfo[];
  classes: ClassInfo[];
  issues: Issue[];
}

/** Response shape for a zip-project POST /analyze request. */
export interface ProjectAnalysis {
  files_analyzed: number;
  files_with_syntax_errors: { file: string; error: string }[];
  total_lines_of_code: number;
  total_functions: number;
  total_classes: number;
  total_issues: number;
  issues: Issue[];
  per_file: Record<string, SingleFileAnalysis>;
}

export type AnalyzeResponse = SingleFileAnalysis | ProjectAnalysis;

export function isProjectAnalysis(r: AnalyzeResponse): r is ProjectAnalysis {
  return (r as ProjectAnalysis).files_analyzed !== undefined;
}

export interface ConstraintViolation {
  type: 'banned_call' | 'banned_import' | 'parse_error';
  name: string | null;
  line: number | null;
  message: string;
  file?: string;
}

export interface TestResult {
  test_number: number;
  input: string;
  expected_output: string;
  actual_output: string;
  passed: boolean;
  timed_out: boolean;
  exit_code: number | null;
  stderr: string;
  compile_error: string | null;
  infra_error: string | null;
}

export interface ExamTestCase {
  input: string;
  expected_output: string;
}

export interface Evaluation {
  meets_requirements: 'yes' | 'partially' | 'no' | 'unknown';
  grade_out_of_20: number | null;
  approach_assessment: string;
  correctness_notes: string;
  feedback: string;
}

export interface ExamEvaluationResponse {
  entry_point?: string;
  banned_names: string[];
  extracted_test_cases: ExamTestCase[];
  constraint_violations: ConstraintViolation[];
  test_results: TestResult[];
  evaluation: Evaluation;
}

export type Language = 'python' | 'java';

export interface ApiError {
  detail: string;
}
