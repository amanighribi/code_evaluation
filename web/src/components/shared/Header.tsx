import { useEffect, useState } from 'react';
import { checkBackendHealth } from '../../lib/api';

export function Header() {
  const [status, setStatus] = useState<'checking' | 'ok' | 'down'>('checking');

  useEffect(() => {
    let cancelled = false;

    async function poll() {
      const ok = await checkBackendHealth();
      if (!cancelled) setStatus(ok ? 'ok' : 'down');
    }

    poll();
    const interval = setInterval(poll, 15000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  const dotColor =
    status === 'ok' ? 'bg-chalk-green shadow-[0_0_6px_theme(colors.chalk-green)]' :
    status === 'down' ? 'bg-ink-red shadow-[0_0_6px_theme(colors.ink-red)]' :
    'bg-muted';

  const label =
    status === 'ok' ? 'backend connected' :
    status === 'down' ? 'backend unreachable — is it running?' :
    'checking backend…';

  return (
    <header className="flex items-center justify-between px-9 py-5 border-b border-white/8">
      <div className="flex items-baseline gap-2.5">
        <span className="font-mono font-bold text-xl text-chalk-green tracking-tight">&gt;_</span>
        <span className="font-mono text-sm text-muted tracking-wide">SUBJECT 9 · CODE EVALUATION</span>
      </div>
      <div className="font-mono text-xs text-muted flex items-center gap-2">
        <span className={`w-1.5 h-1.5 rounded-full ${dotColor}`} />
        <span>{label}</span>
      </div>
    </header>
  );
}
