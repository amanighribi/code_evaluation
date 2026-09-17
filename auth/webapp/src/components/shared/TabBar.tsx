export type TabId = 'analyze' | 'exam';

interface TabBarProps {
  active: TabId;
  onChange: (tab: TabId) => void;
  visibleTabs: TabId[];
}

const TABS: { id: TabId; label: string }[] = [
  { id: 'analyze', label: 'Code Review' },
  { id: 'exam', label: 'Exam Grading' },
];

export function TabBar({ active, onChange, visibleTabs }: TabBarProps) {
  const tabs = TABS.filter((t) => visibleTabs.includes(t.id));
  return (
    <div className="flex gap-1 px-6 lg:px-8 bg-white border-b border-border">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={`relative text-[13.5px] font-medium px-4 py-3 transition ${
            active === tab.id ? 'text-esprit-red' : 'text-esprit-grey-light hover:text-esprit-grey'
          }`}
        >
          {tab.label}
          {active === tab.id && (
            <span className="absolute left-3 right-3 -bottom-px h-0.5 bg-esprit-red rounded-full" />
          )}
        </button>
      ))}
    </div>
  );
}
