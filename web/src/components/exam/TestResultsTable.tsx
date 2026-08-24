import { Fragment } from 'react';
import type { TestResult } from '../../types/api';

export function TestResultsTable({ results }: { results: TestResult[] }) {
  const passed = results.filter((r) => r.passed).length;

  return (
    <div>
      <div className="font-mono text-xs uppercase tracking-wider text-paper-muted mt-5.5 mb-2.5">
        Test execution ({passed}/{results.length} passed)
      </div>
      <table className="w-full border-collapse text-[12.5px] mb-2.5">
        <thead>
          <tr>
            {['#', 'Input', 'Expected', 'Actual', 'Result'].map((h) => (
              <th
                key={h}
                className="text-left font-mono text-[10.5px] uppercase tracking-wide text-paper-muted px-2 py-1.5 border-b border-[#D8CFB6]"
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {results.map((t) => (
            <Fragment key={t.test_number}>
              <tr className="border-b border-paper-2">
                <td className="px-2 py-2 font-mono text-xs text-[#4A4438]">{t.test_number}</td>
                <td className="px-2 py-2 font-mono text-xs text-[#4A4438]">{truncate(t.input)}</td>
                <td className="px-2 py-2 font-mono text-xs text-[#4A4438]">{truncate(t.expected_output)}</td>
                <td className="px-2 py-2 font-mono text-xs text-[#4A4438]">{truncate(t.actual_output)}</td>
                <td className="px-2 py-2">
                  {t.passed ? (
                    <span className="font-mono text-[10.5px] font-bold px-2 py-0.5 rounded-full bg-chalk-green/15 text-chalk-green">
                      PASS
                    </span>
                  ) : (
                    <span className="font-mono text-[10.5px] font-bold px-2 py-0.5 rounded-full bg-ink-red/10 text-ink-red">
                      FAIL
                    </span>
                  )}
                </td>
              </tr>
              {t.compile_error && (
                <tr>
                  <td colSpan={5} className="px-2 py-1.5 text-[11.5px] text-ink-red">
                    Compile error: {truncate(t.compile_error, 200)}
                  </td>
                </tr>
              )}
              {t.infra_error && (
                <tr>
                  <td colSpan={5} className="px-2 py-1.5 text-[11.5px] text-chalk-yellow">
                    Infrastructure issue (not the student's fault): {t.infra_error}
                  </td>
                </tr>
              )}
            </Fragment>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function truncate(text: string, max = 30): string {
  if (!text) return '';
  return text.length > max ? text.slice(0, max) + '…' : text;
}
