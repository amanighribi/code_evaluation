import { useEffect, useState } from 'react';
import { checkBackendHealth } from '../../lib/api';

interface HeaderProps {
  username: string;
  role: string;
  onLogout: () => void;
}

export function Header({ username, role, onLogout }: HeaderProps) {
  const [status, setStatus] = useState<'checking' | 'ok' | 'down'>('checking');

  useEffect(() => {
    let cancelled = false;
    async function poll() {
      const ok = await checkBackendHealth();
      if (!cancelled) setStatus(ok ? 'ok' : 'down');
    }
    poll();
    const interval = setInterval(poll, 15000);
    return () => { cancelled = true; clearInterval(interval); };
  }, []);

  const dotClass =
    status === 'ok' ? 'bg-ok' : status === 'down' ? 'bg-esprit-red' : 'bg-muted';
  const label =
    status === 'ok' ? 'server connected' :
    status === 'down' ? 'server unreachable' : 'checking…';

  return (
    <header className="flex items-center justify-between px-6 lg:px-8 py-3.5 bg-white border-b border-border">
      <div className="flex items-center gap-4">
        <img
          src="/esprit-logo.png"
          alt="ESPRIT"
          className="h-8 w-auto"
          onError={(e) => { (e.currentTarget as HTMLImageElement).style.display = 'none'; }}
        />
        <div className="h-6 w-px bg-border hidden sm:block" />
        <span className="font-semibold text-[14px] text-esprit-grey hidden sm:block">
          Automated Code Evaluation
        </span>
      </div>

      <div className="flex items-center gap-5">
        <div className="flex items-center gap-2 text-[11.5px] text-muted font-mono">
          <span className={`w-1.5 h-1.5 rounded-full ${dotClass}`} />
          <span className="hidden sm:inline">{label}</span>
        </div>
        <div className="h-5 w-px bg-border" />
        <div className="flex items-center gap-3">
          <span className="text-[13px] text-esprit-grey font-medium">{username}</span>
          <span className="text-[10px] font-bold uppercase tracking-wide px-2 py-0.5 rounded bg-surface-tint text-esprit-grey-light">
            {role}
          </span>
          <button
            onClick={onLogout}
            className="text-[12.5px] text-esprit-grey-light hover:text-esprit-red transition"
          >
            Sign out
          </button>
        </div>
      </div>
    </header>
  );
}
