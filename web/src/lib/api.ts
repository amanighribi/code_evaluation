import type { AnalyzeResponse, ExamEvaluationResponse, Language, ApiError } from '../types/api';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export class ApiRequestError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ApiRequestError';
  }
}

async function parseJsonOrThrow<T>(res: Response): Promise<T> {
  let body: unknown;
  try {
    body = await res.json();
  } catch {
    throw new ApiRequestError(`Server returned an unreadable response (status ${res.status}).`);
  }
  if (!res.ok) {
    const detail = (body as ApiError)?.detail || `Request failed with status ${res.status}.`;
    throw new ApiRequestError(detail);
  }
  return body as T;
}

export async function checkBackendHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/`, { method: 'GET',headers: { 'ngrok-skip-browser-warning': 'true' }, });
    return res.ok;
  } catch {
    return false;
  }
}

export async function analyzeCode(file: File): Promise<AnalyzeResponse> {
  const formData = new FormData();
  formData.append('file', file);

  let res: Response;
  try {
    res = await fetch(`${API_BASE}/analyze`, { method: 'POST', body: formData,headers: { 'ngrok-skip-browser-warning': 'true' }, });
  } catch {
    throw new ApiRequestError(`Could not reach the backend at ${API_BASE}. Is the server running?`);
  }
  return parseJsonOrThrow<AnalyzeResponse>(res);
}

export interface EvaluateExamParams {
  codeFile: File;
  instructionsFile: File;
  language: Language;
  entryPoint?: string;
}

export async function evaluateExam(params: EvaluateExamParams): Promise<ExamEvaluationResponse> {
  const formData = new FormData();
  formData.append('code_file', params.codeFile);
  formData.append('instructions_file', params.instructionsFile);
  formData.append('language', params.language);
  if (params.entryPoint) {
    formData.append('entry_point', params.entryPoint);
  }

  let res: Response;
  try {
    res = await fetch(`${API_BASE}/evaluate-exam`, { method: 'POST', body: formData,headers: { 'ngrok-skip-browser-warning': 'true' }, });
  } catch {
    throw new ApiRequestError(`Could not reach the backend at ${API_BASE}. Is the server running?`);
  }
  return parseJsonOrThrow<ExamEvaluationResponse>(res);
}
