export type TabId = 'analyze' | 'exam';

interface TabBarProps {
  active: TabId;
  onChange: (tab: TabId) => void;
}

const TABS: { id: TabId; label: string }[] = [
  { id: 'analyze', label: 'Code Review' },
  { id: 'exam', label: 'Exam Grading' },
];

export function TabBar({ active, onChange }: TabBarProps) {
  return (
    <div className="flex gap-0.5 px-9 mt-4">
      {TABS.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={`font-mono text-[13px] tracking-wide px-4.5 py-2.5 rounded-t-md border border-b-0 transition-colors ${
            active === tab.id
              ? 'text-chalk-white bg-slate-2 border-white/18'
              : 'text-muted border-white/12 hover:text-chalk-white'
          }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}
