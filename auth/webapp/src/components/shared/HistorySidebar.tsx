import type { HistoryEntry } from '../../types/api';

interface HistorySidebarProps {
  history: HistoryEntry[];
  loading: boolean;
}

function formatDate(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short' })
      + ' · ' + d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
  } catch {
    return iso;
  }
}

export function HistorySidebar({ history, loading }: HistorySidebarProps) {
  return (
    <aside className="w-full lg:w-72 flex-shrink-0 bg-white border-r border-border px-5 py-6 overflow-y-auto">
      <div className="eyebrow text-muted mb-4">My submissions</div>

      {loading && (
        <div className="text-[13px] text-muted">Loading…</div>
      )}

      {!loading && history.length === 0 && (
        <div className="text-[13px] text-muted leading-relaxed">
          No submissions yet. Analyse a file to start building your history.
        </div>
      )}

      {!loading && history.map((entry, i) => {
        const previous = history[i + 1];
        let trendLabel: string | null = null;
        let trendClass = '';
        if (previous && previous.filename === entry.filename) {
          if (entry.quality_score < previous.quality_score) { trendLabel = '↓ improved'; trendClass = 'text-ok'; }
          else if (entry.quality_score > previous.quality_score) { trendLabel = '↑ regressed'; trendClass = 'text-esprit-red'; }
          else { trendLabel = '= unchanged'; trendClass = 'text-muted'; }
        }

        return (
          <div key={entry.id} className="border-b border-border py-3 last:border-0">
            <div className="font-mono text-[12.5px] text-ink truncate font-medium">{entry.filename}</div>
            <div className="text-[11px] text-muted mt-1">{formatDate(entry.timestamp)}</div>
            <div className="flex items-center gap-3 mt-1.5 text-[11.5px]">
              <span className="text-esprit-grey-light">
                {entry.total_issues} issue{entry.total_issues !== 1 ? 's' : ''}
              </span>
              <span className="text-muted">score {entry.quality_score}</span>
              {trendLabel && <span className={trendClass}>{trendLabel}</span>}
            </div>
          </div>
        );
      })}
    </aside>
  );
}
