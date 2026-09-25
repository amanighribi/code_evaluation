import { useRef, useState } from 'react';
import type { Language } from '../../types/api';

interface ExamFormProps {
  onSubmit: (params: { codeFile: File; instructionsFile: File; language: Language; entryPoint?: string }) => void;
  isLoading: boolean;
}

const LANGUAGES: { value: Language; label: string }[] = [
  { value: 'python', label: 'Python' },
  { value: 'java', label: 'Java' },
  { value: 'c', label: 'C' },
  { value: 'cpp', label: 'C++' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'ruby', label: 'Ruby' },
  { value: 'go', label: 'Go' },
  { value: 'php', label: 'PHP' },
];

export function ExamForm({ onSubmit, isLoading }: ExamFormProps) {
  const codeRef = useRef<HTMLInputElement>(null);
  const instrRef = useRef<HTMLInputElement>(null);
  const [language, setLanguage] = useState<Language>('python');
  const [entryPoint, setEntryPoint] = useState('');

  function handleSubmit() {
    const codeFile = codeRef.current?.files?.[0];
    const instructionsFile = instrRef.current?.files?.[0];
    if (!codeFile || !instructionsFile) {
      alert('Provide both the student submission and the instructions file.');
      return;
    }
    onSubmit({ codeFile, instructionsFile, language, entryPoint: entryPoint.trim() || undefined });
  }

  const inputClass =
    'w-full bg-surface-tint border border-transparent rounded-lg px-4 py-2.5 text-[13px] text-ink outline-none focus:border-esprit-red/50 focus:bg-white transition';

  return (
    <div>
      <h1 className="text-[19px] font-bold text-esprit-grey mb-1.5">Exam Grading</h1>
      <p className="text-[13px] text-esprit-grey-light mb-6">
        Checks whether the code genuinely meets the assignment, not just whether it passes tests.
      </p>

      <div className="mb-4">
        <label className="block eyebrow text-muted mb-2">Student submission</label>
        <input ref={codeRef} type="file" className={inputClass + ' cursor-pointer'} />
      </div>

      <div className="mb-4">
        <label className="block eyebrow text-muted mb-2">Exam instructions </label>
        <input ref={instrRef} type="file" accept=".txt,.pdf,.docx" className={inputClass + ' cursor-pointer'} />
        <p className="text-[11.5px] text-muted mt-2 leading-relaxed">
          Free text, French or English. Accepts .txt, .pdf, or .docx. Banned functions and test cases are extracted automatically.
        </p>
      </div>

      <div className="mb-4">
        <label className="block eyebrow text-muted mb-2">Language</label>
        <select value={language} onChange={(e) => setLanguage(e.target.value as Language)} className={inputClass + ' cursor-pointer'}>
          {LANGUAGES.map((l) => <option key={l.value} value={l.value}>{l.label}</option>)}
        </select>
      </div>

      <div className="mb-5">
        <label className="block eyebrow text-muted mb-2">Entry point (.zip projects)</label>
        <input type="text" value={entryPoint} onChange={(e) => setEntryPoint(e.target.value)} placeholder="ex. main.py" className={inputClass} />
      </div>

      <button
        onClick={handleSubmit}
        disabled={isLoading}
        className="w-full bg-esprit-red text-white font-semibold text-[14px] rounded-lg py-3 transition hover:bg-esprit-red-dark active:scale-[0.99] disabled:opacity-60 disabled:cursor-not-allowed"
      >
        {isLoading ? 'Grading…' : 'Grade submission'}
      </button>
    </div>
  );
}
