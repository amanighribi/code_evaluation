import { useState, useEffect, useCallback } from 'react';
import { Header } from './components/shared/Header';
import { TabBar, type TabId } from './components/shared/TabBar';
import { HistorySidebar } from './components/shared/HistorySidebar';
import { EmptyState, LoadingState, ErrorBlock } from './components/shared/ResultStates';
import { LoginScreen } from './components/auth/LoginScreen';
import { AnalyzeForm } from './components/analyze/AnalyzeForm';
import { AnalyzeResults } from './components/analyze/AnalyzeResults';
import { ExamForm } from './components/exam/ExamForm';
import { ExamResults } from './components/exam/ExamResults';
import {
  analyzeCode, evaluateExam, fetchHistory, fetchHistoryDetail, ApiRequestError,
  getStoredUsername, getStoredRole, clearAuth,
} from './lib/api';
import type { AnalyzeResponse, ExamEvaluationResponse, Language, HistoryEntry, HistoryDetail, Role } from './types/api';

type ResultState =
  | { status: 'empty' }
  | { status: 'loading'; message: string }
  | { status: 'error'; message: string }
  | { status: 'analyze-success'; data: AnalyzeResponse }
  | { status: 'exam-success'; data: ExamEvaluationResponse }
  | { status: 'history-success'; data: HistoryDetail };

export default function App() {
  const [username, setUsername] = useState<string | null>(getStoredUsername());
  const [role, setRole] = useState<Role>(getStoredRole() || 'student');
  const [tab, setTab] = useState<TabId>('analyze');
  const [result, setResult] = useState<ResultState>({ status: 'empty' });
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [selectedHistoryId, setSelectedHistoryId] = useState<number | null>(null);

  const loadHistory = useCallback(async () => {
    if (!username) return;
    setHistoryLoading(true);
    try {
      setHistory(await fetchHistory());
    } catch {
      setHistory([]);
    } finally {
      setHistoryLoading(false);
    }
  }, [username]);

  useEffect(() => { loadHistory(); }, [loadHistory]);

  if (!username) {
    return (
      <LoginScreen
        onAuthenticated={(name, userRole) => { setUsername(name); setRole(userRole); setTab('analyze'); }}
      />
    );
  }

  // Students only get code review; teachers get both features.
  const visibleTabs: TabId[] = role === 'teacher' ? ['analyze', 'exam'] : ['analyze'];

  function handleLogout() {
    clearAuth();
    setUsername(null);
    setHistory([]);
    setResult({ status: 'empty' });
    setSelectedHistoryId(null);
  }

  function handleTabChange(next: TabId) {
    setTab(next);
    setResult({ status: 'empty' });
    setSelectedHistoryId(null);
  }

  async function handleAnalyze(file: File) {
    setSelectedHistoryId(null);
    setResult({ status: 'loading', message: 'Running static analysis and generating feedback…' });
    try {
      const data = await analyzeCode(file);
      setResult({ status: 'analyze-success', data });
      loadHistory();
    } catch (err) {
      setResult({ status: 'error', message: err instanceof ApiRequestError ? err.message : 'Analysis failed.' });
    }
  }

  async function handleExam(params: { codeFile: File; instructionsFile: File; language: Language; entryPoint?: string }) {
    setSelectedHistoryId(null);
    setResult({ status: 'loading', message: 'Extracting constraints, running sandboxed tests, evaluating…' });
    try {
      const data = await evaluateExam(params);
      setResult({ status: 'exam-success', data });
    } catch (err) {
      setResult({ status: 'error', message: err instanceof ApiRequestError ? err.message : 'Grading failed.' });
    }
  }

  async function handleSelectHistory(id: number) {
    setSelectedHistoryId(id);
    setResult({ status: 'loading', message: 'Loading submission…' });
    try {
      const data = await fetchHistoryDetail(id);
      setResult({ status: 'history-success', data });
    } catch (err) {
      setResult({ status: 'error', message: err instanceof ApiRequestError ? err.message : 'Could not load this submission.' });
    }
  }

  const isLoading = result.status === 'loading';
  const activeTab: TabId = visibleTabs.includes(tab) ? tab : 'analyze';

  return (
    <div className="min-h-screen flex flex-col bg-surface-alt">
      <Header username={username} role={role} onLogout={handleLogout} />
      <TabBar active={activeTab} onChange={handleTabChange} visibleTabs={visibleTabs} />

      <div className="flex flex-1 flex-col lg:flex-row">
        <HistorySidebar
          history={history}
          loading={historyLoading}
          selectedId={selectedHistoryId}
          onSelect={handleSelectHistory}
        />

        <main className="flex-1 grid grid-cols-1 xl:grid-cols-[minmax(320px,420px)_1fr]">
          <section className="bg-white border-r border-border px-7 py-7">
            {activeTab === 'analyze'
              ? <AnalyzeForm onSubmit={handleAnalyze} isLoading={isLoading} />
              : <ExamForm onSubmit={handleExam} isLoading={isLoading} />}
          </section>

          <section className="px-7 py-7 bg-surface-alt">
            <div className="eyebrow text-esprit-red mb-2">
              {result.status === 'history-success'
                ? 'Past submission'
                : activeTab === 'analyze' ? 'Review result' : 'Grading result'}
            </div>
            <h2 className="text-[19px] font-bold text-esprit-grey mb-6">
              {result.status === 'history-success'
                ? result.data.filename
                : activeTab === 'analyze' ? 'Code Review' : 'Exam Grading'}
            </h2>

            {result.status === 'empty' && <EmptyState />}
            {result.status === 'loading' && <LoadingState message={result.message} />}
            {result.status === 'error' && <ErrorBlock message={result.message} />}
            {result.status === 'analyze-success' && <AnalyzeResults data={result.data} />}
            {result.status === 'exam-success' && <ExamResults data={result.data} />}
            {result.status === 'history-success' && (
              <AnalyzeResults
                data={{
                  lines_of_code: result.data.lines_of_code,
                  num_functions: null,
                  num_classes: null,
                  functions: [],
                  classes: [],
                  issues: result.data.issues,
                }}
              />
            )}
          </section>
        </main>
      </div>
    </div>
  );
}