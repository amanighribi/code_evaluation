import { useRef, useState } from 'react';
import type { Language } from '../../types/api';

interface ExamFormProps {
  onSubmit: (params: { codeFile: File; instructionsFile: File; language: Language; entryPoint?: string }) => void;
  isLoading: boolean;
}

export function ExamForm({ onSubmit, isLoading }: ExamFormProps) {
  const codeRef = useRef<HTMLInputElement>(null);
  const instrRef = useRef<HTMLInputElement>(null);
  const [language, setLanguage] = useState<Language>('python');
  const [entryPoint, setEntryPoint] = useState('');

  function handleSubmit() {
    const codeFile = codeRef.current?.files?.[0];
    const instructionsFile = instrRef.current?.files?.[0];
    if (!codeFile || !instructionsFile) {
      alert('Please provide both the student submission and the exam instructions file.');
      return;
    }
    onSubmit({ codeFile, instructionsFile, language, entryPoint: entryPoint.trim() || undefined });
  }

  const inputClass =
    'w-full bg-slate-3 border border-white/14 text-chalk-white text-[13.5px] rounded-md px-3 py-2.5 focus:outline-none focus:border-chalk-green focus:ring-2 focus:ring-chalk-green/25';

  return (
    <div>
      <div className="font-mono text-[11px] tracking-wider uppercase text-chalk-green mb-1.5">
        Exam-correction mode
      </div>
      <h1 className="font-mono text-[19px] font-semibold text-chalk-white mb-6">Exam Grading</h1>

      <div className="mb-5">
        <label className="block font-mono text-xs text-muted mb-1.5">
          Student submission (file or .zip project)
        </label>
        <input ref={codeRef} type="file" accept=".py,.java,.zip" className={inputClass + ' cursor-pointer'} />
      </div>

      <div className="mb-5">
        <label className="block font-mono text-xs text-muted mb-1.5">Exam instructions (.txt)</label>
        <input ref={instrRef} type="file" accept=".txt" className={inputClass + ' cursor-pointer'} />
        <p className="text-[11.5px] text-muted mt-1.5 leading-snug">
          Free text, French or English. Banned functions and example test cases are extracted automatically.
        </p>
      </div>

      <div className="mb-5">
        <label className="block font-mono text-xs text-muted mb-1.5">Language</label>
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value as Language)}
          className={inputClass + ' cursor-pointer'}
        >
          <option value="python">Python</option>
          <option value="java">Java</option>
        </select>
      </div>

      <div className="mb-5">
        <label className="block font-mono text-xs text-muted mb-1.5">
          Entry point <span className="opacity-60">— only needed for multi-file zip projects</span>
        </label>
        <input
          type="text"
          value={entryPoint}
          onChange={(e) => setEntryPoint(e.target.value)}
          placeholder="e.g. main.py"
          className={inputClass}
        />
      </div>

      <button
        onClick={handleSubmit}
        disabled={isLoading}
        className="w-full font-mono text-[13.5px] font-semibold tracking-wide bg-chalk-green text-[#0F1A16] rounded-md py-3.5 mt-2 transition-colors hover:bg-[#6DAF7E] active:scale-[0.985] disabled:bg-slate-3 disabled:text-muted disabled:cursor-not-allowed"
      >
        {isLoading ? 'Grading…' : 'Grade submission'}
      </button>
    </div>
  );
}
