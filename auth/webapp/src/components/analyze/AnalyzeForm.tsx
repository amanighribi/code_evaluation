import { useRef, useState } from 'react';

interface AnalyzeFormProps {
  onSubmit: (file: File) => void;
  isLoading: boolean;
}

export function AnalyzeForm({ onSubmit, isLoading }: AnalyzeFormProps) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [fileName, setFileName] = useState<string | null>(null);

  function handleSubmit() {
    const file = fileRef.current?.files?.[0];
    if (!file) { alert('Choose a file or a .zip project first.'); return; }
    onSubmit(file);
  }

  return (
    <div>
      <h1 className="text-[19px] font-bold text-esprit-grey mb-1.5">Code Review</h1>
      <p className="text-[13px] text-esprit-grey-light mb-6">
        Static analysis and pedagogical feedback, with progress tracking across submissions.
      </p>

      <div className="mb-5">
        <label className="block eyebrow text-muted mb-2">Source file or .zip project</label>
        <input
          ref={fileRef}
          type="file"
          onChange={(e) => setFileName(e.target.files?.[0]?.name ?? null)}
          className="w-full bg-surface-tint border border-transparent rounded-lg px-4 py-2.5 text-[12.5px] text-ink cursor-pointer outline-none focus:border-esprit-red/50 focus:bg-white transition"
        />
        <p className="text-[11.5px] text-muted mt-2 leading-relaxed">
          Python gets the full AST analysis; any other language uses the generic analyser.
          {fileName && <span className="block mt-1 text-ok font-medium">Selected: {fileName}</span>}
        </p>
      </div>

      <button
        onClick={handleSubmit}
        disabled={isLoading}
        className="w-full bg-esprit-red text-white font-semibold text-[14px] rounded-lg py-3 transition hover:bg-esprit-red-dark active:scale-[0.99] disabled:opacity-60 disabled:cursor-not-allowed"
      >
        {isLoading ? 'Analysing…' : 'Run analysis'}
      </button>
    </div>
  );
}
