import type {
  AnalyzeResponse, ExamEvaluationResponse, Language, ApiError,
  AuthResponse, HistoryEntry, HistoryDetail, Role,
} from '../types/api';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const TOKEN_KEY = 'code_eval_token';
const USERNAME_KEY = 'code_eval_username';
const ROLE_KEY = 'code_eval_role';

export class ApiRequestError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ApiRequestError';
  }
}

export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}
export function getStoredUsername(): string | null {
  return localStorage.getItem(USERNAME_KEY);
}
export function getStoredRole(): Role | null {
  return localStorage.getItem(ROLE_KEY) as Role | null;
}
export function storeAuth(token: string, username: string, role: Role) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USERNAME_KEY, username);
  localStorage.setItem(ROLE_KEY, role);
}
export function clearAuth() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USERNAME_KEY);
  localStorage.removeItem(ROLE_KEY);
}

function baseHeaders(): Record<string, string> {
  const headers: Record<string, string> = { 'ngrok-skip-browser-warning': 'true' };
  const token = getStoredToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return headers;
}

async function parseJsonOrThrow<T>(res: Response): Promise<T> {
  let body: unknown;
  try {
    body = await res.json();
  } catch {
    throw new ApiRequestError(`The server returned an unreadable response (status ${res.status}).`);
  }
  if (!res.ok) {
    const detail = (body as ApiError)?.detail || `Request failed with status ${res.status}.`;
    throw new ApiRequestError(detail);
  }
  return body as T;
}

export async function checkBackendHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/`, { method: 'GET', headers: baseHeaders() });
    return res.ok;
  } catch {
    return false;
  }
}

export async function register(username: string, password: string, role: Role = 'student'): Promise<AuthResponse> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { ...baseHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password, role }),
    });
  } catch {
    throw new ApiRequestError(`Cannot reach the server at ${API_BASE}.`);
  }
  return parseJsonOrThrow<AuthResponse>(res);
}

export async function login(username: string, password: string): Promise<AuthResponse> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { ...baseHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
  } catch {
    throw new ApiRequestError(`Cannot reach the server at ${API_BASE}.`);
  }
  return parseJsonOrThrow<AuthResponse>(res);
}

export async function fetchHistory(): Promise<HistoryEntry[]> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}/history`, { method: 'GET', headers: baseHeaders() });
  } catch {
    throw new ApiRequestError(`Cannot reach the server at ${API_BASE}.`);
  }
  return parseJsonOrThrow<HistoryEntry[]>(res);
}

export async function fetchHistoryDetail(id: number): Promise<HistoryDetail> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}/history/${id}`, { method: 'GET', headers: baseHeaders() });
  } catch {
    throw new ApiRequestError(`Cannot reach the server at ${API_BASE}.`);
  }
  return parseJsonOrThrow<HistoryDetail>(res);
}

export async function analyzeCode(file: File): Promise<AnalyzeResponse> {
  const formData = new FormData();
  formData.append('file', file);
  let res: Response;
  try {
    res = await fetch(`${API_BASE}/analyze`, { method: 'POST', body: formData, headers: baseHeaders() });
  } catch {
    throw new ApiRequestError(`Cannot reach the server at ${API_BASE}.`);
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
  if (params.entryPoint) formData.append('entry_point', params.entryPoint);

  let res: Response;
  try {
    res = await fetch(`${API_BASE}/evaluate-exam`, { method: 'POST', body: formData, headers: baseHeaders() });
  } catch {
    throw new ApiRequestError(`Cannot reach the server at ${API_BASE}.`);
  }
  return parseJsonOrThrow<ExamEvaluationResponse>(res);
}