import { useState } from 'react';
import { login, register, storeAuth, ApiRequestError } from '../../lib/api';
import type { Role } from '../../types/api';

interface LoginScreenProps {
  onAuthenticated: (username: string, role: Role) => void;
}

export function LoginScreen({ onAuthenticated }: LoginScreenProps) {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<Role>('student');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = mode === 'login'
        ? await login(username.trim(), password)
        : await register(username.trim(), password, role);
      storeAuth(res.access_token, res.username, res.role);
      onAuthenticated(res.username, res.role);
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  }

  const inputClass =
    'w-full bg-surface-tint border border-transparent rounded-lg px-4 py-3 text-[14px] text-ink outline-none focus:border-esprit-red/50 focus:bg-white focus:ring-2 focus:ring-esprit-red/10 transition';

  return (
    <div className="min-h-screen grid grid-cols-1 lg:grid-cols-[1.35fr_1fr] bg-white">
      <div className="hidden lg:flex flex-col justify-center px-16 bg-gradient-to-br from-surface-tint to-white relative">
        <div className="mb-10">
          <img src="/esprit-logo.png" alt="ESPRIT" className="h-14 w-auto"
            onError={(e) => { (e.currentTarget as HTMLImageElement).style.display = 'none'; }} />
        </div>
        <h1 className="text-[42px] leading-[1.1] font-extrabold tracking-tight text-esprit-grey max-w-xl">
          Automated code <span className="text-esprit-red">evaluation.</span>
        </h1>
        <div className="h-1 w-56 bg-esprit-red mt-6 mb-7 rounded-full" />
        <p className="text-[15px] leading-relaxed text-esprit-grey-light max-w-md">
          Static analysis, grounded pedagogical feedback and exam grading —
          with progress tracking across your submissions.
        </p>
        <div className="absolute bottom-10 left-16 eyebrow text-muted">ESPRIT · Software Engineering</div>
      </div>

      <div className="flex flex-col justify-center px-8 sm:px-14 py-16 border-l border-border">
        <div className="lg:hidden mb-8">
          <img src="/esprit-logo.png" alt="ESPRIT" className="h-10 w-auto"
            onError={(e) => { (e.currentTarget as HTMLImageElement).style.display = 'none'; }} />
        </div>

        <h2 className="text-[22px] font-bold text-esprit-grey mb-1.5">
          {mode === 'login' ? 'Sign in' : 'Create an account'}
        </h2>
        <p className="text-[13.5px] text-esprit-grey-light">
          {mode === 'login'
            ? 'Enter your credentials to access your workspace.'
            : 'Choose a username, a password, and your account type.'}
        </p>
        <div className="h-0.5 w-full bg-esprit-red/90 mt-3 mb-7 rounded-full" />

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block eyebrow text-muted mb-2">Username</label>
            <input type="text" value={username} onChange={(e) => setUsername(e.target.value)}
              autoComplete="username" className={inputClass} placeholder="e.g. amani" />
          </div>

          <div className={mode === 'register' ? 'mb-4' : 'mb-6'}>
            <label className="block eyebrow text-muted mb-2">Password</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              className={inputClass} placeholder="••••••••" />
          </div>

          {mode === 'register' && (
            <div className="mb-6">
              <label className="block eyebrow text-muted mb-2">Account type</label>
              <div className="grid grid-cols-2 gap-3">
                <RoleCard
                  active={role === 'student'} onClick={() => setRole('student')}
                  title="Student" description="Code review only"
                />
                <RoleCard
                  active={role === 'teacher'} onClick={() => setRole('teacher')}
                  title="Teacher" description="Code review + exam grading"
                />
              </div>
            </div>
          )}

          {error && (
            <div className="mb-5 text-[13px] text-esprit-red bg-esprit-red/6 border border-esprit-red/25 rounded-lg px-4 py-3">
              {error}
            </div>
          )}

          <button type="submit" disabled={loading}
            className="w-full bg-esprit-red text-white font-semibold text-[15px] rounded-lg py-3.5 transition hover:bg-esprit-red-dark active:scale-[0.99] disabled:opacity-60 disabled:cursor-not-allowed">
            {loading ? 'Please wait…' : mode === 'login' ? 'Sign in' : 'Create account'}
          </button>
        </form>

        <button
          onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError(null); }}
          className="mt-6 text-[13.5px] text-esprit-grey-light hover:text-esprit-red transition">
          {mode === 'login' ? "No account yet? Create one" : 'Already have an account? Sign in'}
        </button>
      </div>
    </div>
  );
}

function RoleCard({ active, onClick, title, description }: {
  active: boolean; onClick: () => void; title: string; description: string;
}) {
  return (
    <button type="button" onClick={onClick}
      className={`text-left rounded-lg border px-4 py-3 transition ${
        active ? 'border-esprit-red bg-esprit-red/5' : 'border-border bg-surface-tint hover:border-esprit-grey-light/40'
      }`}>
      <div className={`text-[14px] font-semibold ${active ? 'text-esprit-red' : 'text-esprit-grey'}`}>{title}</div>
      <div className="text-[11.5px] text-muted mt-0.5 leading-snug">{description}</div>
    </button>
  );
}
