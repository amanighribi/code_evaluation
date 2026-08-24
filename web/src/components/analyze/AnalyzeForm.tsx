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
    if (!file) {
      alert('Choose a .py file or a .zip project first.');
      return;
    }
    onSubmit(file);
  }

  return (
    <div>
      <div className="font-mono text-[11px] tracking-wider uppercase text-chalk-green mb-1.5">
        Layer 2 &rarr; 4
      </div>
      <h1 className="font-mono text-[19px] font-semibold text-chalk-white mb-6">Code Review</h1>

      <div className="mb-5">
        <label className="block font-mono text-xs text-muted mb-1.5">
          Source (.py file or .zip project)
        </label>
        <input
          ref={fileRef}
          type="file"
          accept=".py,.zip"
          onChange={(e) => setFileName(e.target.files?.[0]?.name ?? null)}
          className="w-full bg-slate-3 border border-white/14 text-chalk-white text-[12.5px] rounded-md px-2.5 py-2.5 cursor-pointer focus:outline-none focus:border-chalk-green focus:ring-2 focus:ring-chalk-green/25"
        />
        <p className="text-[11.5px] text-muted mt-1.5 leading-snug">
          Upload a single Python file for a quick check, or a zipped project folder for a full multi-file review.
          {fileName && <span className="block mt-1 text-chalk-green">Selected: {fileName}</span>}
        </p>
      </div>

      <button
        onClick={handleSubmit}
        disabled={isLoading}
        className="w-full font-mono text-[13.5px] font-semibold tracking-wide bg-chalk-green text-[#0F1A16] rounded-md py-3.5 mt-2 transition-colors hover:bg-[#6DAF7E] active:scale-[0.985] disabled:bg-slate-3 disabled:text-muted disabled:cursor-not-allowed"
      >
        {isLoading ? 'Analyzing…' : 'Run analysis'}
      </button>
    </div>
  );
}
