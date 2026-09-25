export type Severity = 'critical' | 'major' | 'minor' | 'info' | 'unknown';
export type Role = 'student' | 'teacher';

export interface Issue {
  rule_id: string;
  message: string;
  file?: string;
  feedback?: string | null;
  suggested_fix?: string | null;
  severity?: Severity;
}

export interface FunctionInfo {
  name: string; line: number; num_params: number;
  length: number | null; cyclomatic_complexity: number; has_docstring: boolean;
}
export interface ClassInfo { name: string; line: number; }

export interface ProgressComparison {
  trend: 'improved' | 'regressed' | 'unchanged';
  previous_quality_score: number;
  current_quality_score: number;
  resolved_issues: Issue[];
  new_issues: Issue[];
  persisting_issues: Issue[];
  resolved_count: number;
  new_count: number;
  persisting_count: number;
}

export interface SingleFileAnalysis {
  lines_of_code: number;
  num_functions: number | null;
  num_classes: number | null;
  functions: FunctionInfo[];
  classes: ClassInfo[];
  issues: Issue[];
  progress?: ProgressComparison;
}

export interface ProjectAnalysis {
  files_analyzed: number;
  files_with_syntax_errors: { file: string; error: string }[];
  total_lines_of_code: number;
  total_functions: number;
  total_classes: number;
  total_issues: number;
  issues: Issue[];
  per_file: Record<string, SingleFileAnalysis>;
  progress?: ProgressComparison;
}

export type AnalyzeResponse = SingleFileAnalysis | ProjectAnalysis;

export function isProjectAnalysis(r: AnalyzeResponse): r is ProjectAnalysis {
  return (r as ProjectAnalysis).files_analyzed !== undefined;
}

export interface ConstraintViolation {
  type: 'banned_call' | 'banned_import' | 'parse_error';
  name: string | null; line: number | null; message: string; file?: string;
}

export interface TestResult {
  test_number: number; input: string; expected_output: string; actual_output: string;
  passed: boolean; timed_out: boolean; exit_code: number | null;
  stderr: string; compile_error: string | null; infra_error: string | null;
}

export interface ExamTestCase { input: string; expected_output: string; }

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

export type Language = 'python' | 'java' | 'c' | 'cpp' | 'javascript' | 'ruby' | 'go' | 'php';

export interface HistoryEntry {
  id: number; filename: string; timestamp: string;
  total_issues: number; quality_score: number;
}

export interface HistoryDetail extends HistoryEntry {
  issues: Issue[];
}

export interface AuthResponse {
  access_token: string; token_type: string; username: string; role: Role;
}

export interface ApiError { detail: string; }