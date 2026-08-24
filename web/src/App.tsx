import { useState } from 'react';
import { Header } from './components/shared/Header';
import { TabBar, type TabId } from './components/shared/TabBar';
import { EmptyState, LoadingState, ErrorBlock } from './components/shared/ResultStates';
import { AnalyzeForm } from './components/analyze/AnalyzeForm';
import { AnalyzeResults } from './components/analyze/AnalyzeResults';
import { ExamForm } from './components/exam/ExamForm';
import { ExamResults } from './components/exam/ExamResults';
import { analyzeCode, evaluateExam, ApiRequestError } from './lib/api';
import type { AnalyzeResponse, ExamEvaluationResponse, Language } from './types/api';

type ResultState =
  | { status: 'empty' }
  | { status: 'loading'; message: string }
  | { status: 'error'; message: string }
  | { status: 'analyze-success'; data: AnalyzeResponse }
  | { status: 'exam-success'; data: ExamEvaluationResponse };

export default function App() {
  const [tab, setTab] = useState<TabId>('analyze');
  const [result, setResult] = useState<ResultState>({ status: 'empty' });

  function handleTabChange(next: TabId) {
    setTab(next);
    setResult({ status: 'empty' });
  }

  async function handleAnalyze(file: File) {
    setResult({ status: 'loading', message: 'Running static analysis + generating grounded feedback…' });
    try {
      const data = await analyzeCode(file);
      setResult({ status: 'analyze-success', data });
    } catch (err) {
      setResult({ status: 'error', message: err instanceof ApiRequestError ? err.message : 'Analysis failed.' });
    }
  }

  async function handleExam(params: {
    codeFile: File;
    instructionsFile: File;
    language: Language;
    entryPoint?: string;
  }) {
    setResult({ status: 'loading', message: 'Extracting constraints, running sandboxed tests, evaluating…' });
    try {
      const data = await evaluateExam(params);
      setResult({ status: 'exam-success', data });
    } catch (err) {
      setResult({ status: 'error', message: err instanceof ApiRequestError ? err.message : 'Evaluation failed.' });
    }
  }

  const isLoading = result.status === 'loading';
  const paperTitle = tab === 'analyze' ? 'Code review' : 'Grading result';
  const paperEyebrow = tab === 'analyze' ? 'Layer 2 → 4' : 'Exam-correction mode';

  return (
    <div className="min-h-screen bg-slate text-chalk-white">
      <Header />
      <TabBar active={tab} onChange={handleTabChange} />

      <main className="grid grid-cols-1 md:grid-cols-2 min-h-[calc(100vh-140px)]">
        <section className="bg-slate-2 px-9 pt-8 pb-15 border-r border-white/8">
          {tab === 'analyze' ? (
            <AnalyzeForm onSubmit={handleAnalyze} isLoading={isLoading} />
          ) : (
            <ExamForm onSubmit={handleExam} isLoading={isLoading} />
          )}
        </section>

        <section className="bg-paper text-[#2B2620] px-9 pt-8 pb-15 relative">
          <div className="font-mono text-[11px] uppercase tracking-wider text-ink-red mb-1.5">
            {result.status === 'empty' ? 'Result' : paperEyebrow}
          </div>
          <h1 className="font-mono text-[19px] font-semibold text-[#2B2620] mb-6">
            {result.status === 'empty' ? 'Graded output' : paperTitle}
          </h1>

          {result.status === 'empty' && <EmptyState />}
          {result.status === 'loading' && <LoadingState message={result.message} />}
          {result.status === 'error' && <ErrorBlock message={result.message} />}
          {result.status === 'analyze-success' && <AnalyzeResults data={result.data} />}
          {result.status === 'exam-success' && <ExamResults data={result.data} />}
        </section>
      </main>
    </div>
  );
}
