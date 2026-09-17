import { Fragment } from 'react';
import type { TestResult } from '../../types/api';

function truncate(text: string, max = 28): string {
  if (!text) return '';
  return text.length > max ? text.slice(0, max) + '…' : text;
}

export function TestResultsTable({ results }: { results: TestResult[] }) {
  const passed = results.filter((r) => r.passed).length;

  return (
    <div>
      <div className="eyebrow text-muted mt-6 mb-2.5">
        Test execution ({passed}/{results.length} passed)
      </div>
      <table className="w-full border-collapse text-[12.5px]">
        <thead>
          <tr>
            {['#', 'Input', 'Expected', 'Actual', 'Result'].map((h) => (
              <th key={h} className="text-left eyebrow text-muted px-2 py-2 border-b border-border font-normal">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {results.map((t) => (
            <Fragment key={t.test_number}>
              <tr className="border-b border-border">
                <td className="px-2 py-2.5 font-mono text-[12px] text-esprit-grey-light">{t.test_number}</td>
                <td className="px-2 py-2.5 font-mono text-[12px] text-esprit-grey-light">{truncate(t.input)}</td>
                <td className="px-2 py-2.5 font-mono text-[12px] text-esprit-grey-light">{truncate(t.expected_output)}</td>
                <td className="px-2 py-2.5 font-mono text-[12px] text-esprit-grey-light">{truncate(t.actual_output)}</td>
                <td className="px-2 py-2.5">
                  <span className={`text-[10.5px] font-bold px-2 py-0.5 rounded ${t.passed ? 'bg-ok/12 text-ok' : 'bg-esprit-red/10 text-esprit-red'}`}>
                    {t.passed ? 'PASS' : 'FAIL'}
                  </span>
                </td>
              </tr>
              {t.compile_error && (
                <tr><td colSpan={5} className="px-2 py-1.5 text-[11.5px] text-esprit-red">Compile error: {truncate(t.compile_error, 180)}</td></tr>
              )}
              {t.infra_error && (
                <tr><td colSpan={5} className="px-2 py-1.5 text-[11.5px] text-sev-major">Infrastructure issue (not the student's fault): {t.infra_error}</td></tr>
              )}
            </Fragment>
          ))}
        </tbody>
      </table>
    </div>
  );
}
