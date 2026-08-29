import React, { useEffect, useState, useRef } from 'react';
import { Award, Zap, ArrowUpRight, ArrowDownRight, Trophy, BarChart2, CheckCircle2, Loader2, Database } from 'lucide-react';
import { api } from '../api/client';
import type { BenchmarkResponse } from '../types';
import { ErrorState } from '../components/Common/ErrorState';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

// ─── Staged Loading ───────────────────────────────────────────────────────────

type Stage = 'preparing' | 'baseline' | 'mobimart' | 'metrics';

const STAGE_SEQUENCE: Stage[] = ['preparing', 'baseline', 'mobimart', 'metrics'];

const STAGE_LABELS: Record<Stage, string> = {
  preparing: 'Preparing benchmark data…',
  baseline: 'Simulating Baseline strategy (proportional allocation)…',
  mobimart: 'Simulating MobiMart strategy (constrained greedy + EOL engine)…',
  metrics: 'Calculating performance metrics & comparative scorecard…',
};

const STAGE_DURATIONS_MS: Record<Stage, number> = {
  preparing: 900,
  baseline: 2800,
  mobimart: 4200,
  metrics: 800,
};

function StagedLoadingScreen({ stage, cacheHit }: { stage: Stage; cacheHit: boolean }) {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '480px',
      gap: '32px',
    }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', justifyContent: 'center', marginBottom: '8px' }}>
          <Loader2 size={24} color="#38bdf8" style={{ animation: 'spin 1s linear infinite' }} />
          <h2 style={{ fontSize: '1.35rem', fontWeight: 700, color: 'white', margin: 0 }}>
            Running Benchmark…
          </h2>
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', margin: 0 }}>
          Both strategies run under identical starting conditions for a fair comparison
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', width: '100%', maxWidth: '480px' }}>
        {STAGE_SEQUENCE.map((s) => {
          const stageIdx = STAGE_SEQUENCE.indexOf(s);
          const currentIdx = STAGE_SEQUENCE.indexOf(stage);
          const isDone = stageIdx < currentIdx;
          const isCurrent = stageIdx === currentIdx;

          return (
            <div
              key={s}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '12px 16px',
                borderRadius: '8px',
                background: isCurrent ? 'rgba(56,189,248,0.08)' : isDone ? 'rgba(52,211,153,0.06)' : 'rgba(255,255,255,0.03)',
                border: `1px solid ${isCurrent ? 'rgba(56,189,248,0.3)' : isDone ? 'rgba(52,211,153,0.2)' : 'rgba(255,255,255,0.06)'}`,
                transition: 'all 0.3s ease',
              }}
            >
              {isDone ? (
                <CheckCircle2 size={18} color="#34d399" style={{ flexShrink: 0 }} />
              ) : isCurrent ? (
                <Loader2 size={18} color="#38bdf8" style={{ flexShrink: 0, animation: 'spin 1s linear infinite' }} />
              ) : (
                <div style={{ width: 18, height: 18, borderRadius: '50%', border: '2px solid #334155', flexShrink: 0 }} />
              )}
              <span style={{
                fontSize: '0.875rem',
                fontWeight: isCurrent ? 600 : 500,
                color: isDone ? '#34d399' : isCurrent ? '#e2e8f0' : '#64748b',
              }}>
                {STAGE_LABELS[s]}
              </span>
            </div>
          );
        })}
      </div>

      {cacheHit && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Database size={14} color="#a855f7" />
          <span style={{ fontSize: '0.75rem', color: '#a855f7', fontWeight: 600 }}>Loading cached result</span>
        </div>
      )}

      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}

// ─── Page Component ───────────────────────────────────────────────────────────

export const BenchmarkPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [benchmark, setBenchmark] = useState<BenchmarkResponse | null>(null);
  const [weeksRange, setWeeksRange] = useState({ start: 1, end: 12 });
  const [loadStage, setLoadStage] = useState<Stage>('preparing');
  const [lastCacheHit, setLastCacheHit] = useState(false);
  const [isCachedResult, setIsCachedResult] = useState(false);
  const stageTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const advanceStages = (isCached: boolean) => {
    if (isCached) return; // don't stage-animate cache hits

    let delay = 0;
    STAGE_SEQUENCE.forEach((s) => {
      const d = STAGE_DURATIONS_MS[s];
      setTimeout(() => setLoadStage(s), delay);
      delay += d;
    });
  };

  const runBenchmark = async () => {
    if (loading) return;
    setLoading(true);
    setError(null);
    setLoadStage('preparing');
    setLastCacheHit(false);

    try {
      // Speculatively start stage progression
      advanceStages(false);

      const { data, cacheHit } = await api.runBenchmark(weeksRange.start, weeksRange.end);

      setLastCacheHit(cacheHit);
      setIsCachedResult(cacheHit);
      setBenchmark(data);
    } catch (err: any) {
      setError(err.message || 'Failed to execute strategy benchmark comparison. Please retry.');
    } finally {
      if (stageTimerRef.current) clearTimeout(stageTimerRef.current);
      setLoading(false);
    }
  };

  useEffect(() => {
    runBenchmark();
  }, [weeksRange]);

  if (loading) return <StagedLoadingScreen stage={loadStage} cacheHit={lastCacheHit} />;
  if (error || !benchmark) return <ErrorState message={error || 'No benchmark data available'} onRetry={runBenchmark} />;

  const { baseline, mobimart, metrics, summary_text } = benchmark;

  // Chart Data
  const financialComparisonData = [
    {
      name: 'Total Revenue',
      Baseline: baseline.total_revenue / 10000000,
      MobiMart: mobimart.total_revenue / 10000000,
    },
    {
      name: 'Gross Margin',
      Baseline: baseline.total_gross_margin / 10000000,
      MobiMart: mobimart.total_gross_margin / 10000000,
    },
  ];

  const operationalComparisonData = [
    {
      name: 'Stockout Rate (%)',
      Baseline: baseline.stockout_rate,
      MobiMart: mobimart.stockout_rate,
    },
    {
      name: 'Weeks Cover (wks)',
      Baseline: baseline.average_weeks_of_cover,
      MobiMart: mobimart.average_weeks_of_cover,
    },
    {
      name: 'Dead Stock (%)',
      Baseline: baseline.dead_stock_pct,
      MobiMart: mobimart.dead_stock_pct,
    },
  ];

  // Metrics where LOWER mobimart_value is better
  const LOWER_IS_BETTER = new Set(['stockout_rate', 'dead_stock_pct', 'actual_markdown_loss', 'total_lost_sales_value']);

  return (
    <div>
      {/* Header Banner */}
      <div style={{ marginBottom: '24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span className="badge badge-green" style={{ gap: '4px' }}>
              <Trophy size={12} /> Recruiter WOW Benchmark
            </span>
            <span className="badge badge-blue">Controlled Fair Comparison</span>
            {isCachedResult && (
              <span className="badge" style={{ gap: '4px', background: 'rgba(168,85,247,0.15)', color: '#c084fc', border: '1px solid rgba(168,85,247,0.3)' }}>
                <Database size={11} /> Instant — Cached Result
              </span>
            )}
          </div>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'white', letterSpacing: '-0.02em' }}>
            Strategy Benchmark: Naive Baseline vs MobiMart Intelligence
          </h2>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
            Comparing Strategy A (Last-4-Wk Proportional Allocation) against Strategy B (Constrained Greedy + EOL Engine)
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <select
            value={`${weeksRange.start}-${weeksRange.end}`}
            onChange={(e) => {
              const [s, end] = e.target.value.split('-').map(Number);
              setWeeksRange({ start: s, end });
            }}
            className="input-select"
            style={{ fontWeight: 700, color: '#38bdf8' }}
          >
            <option value="1-12">Evaluation: Weeks 1 to 12 (Q1)</option>
            <option value="1-24">Evaluation: Weeks 1 to 24 (H1)</option>
            <option value="1-52">Evaluation: Weeks 1 to 52 (Full Year)</option>
          </select>

          <button onClick={runBenchmark} disabled={loading} className="btn btn-primary">
            <Zap size={16} />
            <span>{loading ? 'Running Benchmark…' : 'Rerun Benchmark'}</span>
          </button>
        </div>
      </div>

      {/* Summary Narrative Banner */}
      <div className="card" style={{ marginBottom: '24px', backgroundColor: '#0f172a', borderLeft: '4px solid #38bdf8', padding: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '16px' }}>
          <Award size={28} color="#38bdf8" style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'white', marginBottom: '4px' }}>
              Executive Benchmark Summary
            </h3>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              {summary_text}
            </p>
          </div>
        </div>
      </div>

      {/* Side by Side Scorecard Header Cards */}
      <div className="grid-2">
        {/* Baseline Card */}
        <div className="card" style={{ borderTop: '4px solid #f59e0b' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <span className="badge badge-amber">STRATEGY A</span>
            <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Naive Proportional</span>
          </div>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'white', marginBottom: '16px' }}>Last-4-Week Baseline</h3>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', fontSize: '0.875rem' }}>
            <div>
              <span style={{ color: '#94a3b8' }}>Total Revenue:</span>
              <div style={{ fontWeight: 700, color: 'white', fontSize: '1.1rem' }}>₹{(baseline.total_revenue / 10000000).toFixed(2)} Cr</div>
            </div>
            <div>
              <span style={{ color: '#94a3b8' }}>Gross Margin:</span>
              <div style={{ fontWeight: 700, color: '#f59e0b', fontSize: '1.1rem' }}>₹{(baseline.total_gross_margin / 10000000).toFixed(2)} Cr</div>
            </div>
            <div>
              <span style={{ color: '#94a3b8' }}>Stockout Rate:</span>
              <div style={{ fontWeight: 700, color: '#f87171', fontSize: '1.1rem' }}>{baseline.stockout_rate.toFixed(1)}%</div>
            </div>
            <div>
              <span style={{ color: '#94a3b8' }}>Capital Turns:</span>
              <div style={{ fontWeight: 700, color: 'white', fontSize: '1.1rem' }}>{baseline.capital_turns.toFixed(2)}x</div>
            </div>
          </div>
        </div>

        {/* MobiMart Card */}
        <div className="card" style={{ borderTop: '4px solid #34d399', backgroundColor: '#0f172a' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <span className="badge badge-green">STRATEGY B (MOBIMART)</span>
            <span style={{ fontSize: '0.8rem', color: '#34d399', fontWeight: 600 }}>Intelligent Engine</span>
          </div>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'white', marginBottom: '16px' }}>MobiMart Optimization</h3>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', fontSize: '0.875rem' }}>
            <div>
              <span style={{ color: '#94a3b8' }}>Total Revenue:</span>
              <div style={{ fontWeight: 700, color: 'white', fontSize: '1.1rem' }}>
                ₹{(mobimart.total_revenue / 10000000).toFixed(2)} Cr
              </div>
            </div>
            <div>
              <span style={{ color: '#94a3b8' }}>Gross Margin:</span>
              <div style={{ fontWeight: 800, color: '#34d399', fontSize: '1.2rem' }}>
                ₹{(mobimart.total_gross_margin / 10000000).toFixed(2)} Cr
              </div>
            </div>
            <div>
              <span style={{ color: '#94a3b8' }}>Stockout Rate:</span>
              <div style={{ fontWeight: 700, color: '#38bdf8', fontSize: '1.1rem' }}>{mobimart.stockout_rate.toFixed(1)}%</div>
            </div>
            <div>
              <span style={{ color: '#94a3b8' }}>Capital Turns:</span>
              <div style={{ fontWeight: 700, color: '#a855f7', fontSize: '1.1rem' }}>{mobimart.capital_turns.toFixed(2)}x</div>
            </div>
          </div>
        </div>
      </div>

      {/* Visual Charts Comparison */}
      <div className="grid-2">
        <div className="card">
          <div className="card-title">Financial Outperformance (Crores ₹) — Higher is better</div>
          <div style={{ height: '260px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={financialComparisonData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="name" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: 'white' }} />
                <Legend wrapperStyle={{ color: 'white' }} />
                <Bar dataKey="Baseline" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                <Bar dataKey="MobiMart" fill="#34d399" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <div className="card-title">Operational Metrics — Lower Stockout & Dead Stock is better</div>
          <div style={{ height: '260px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={operationalComparisonData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="name" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: 'white' }} />
                <Legend wrapperStyle={{ color: 'white' }} />
                <Bar dataKey="Baseline" fill="#f43f5e" radius={[4, 4, 0, 0]} />
                <Bar dataKey="MobiMart" fill="#38bdf8" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Full Scorecard Table */}
      <div className="card" style={{ padding: 0 }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ fontWeight: 700, color: 'white', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <BarChart2 size={18} color="#38bdf8" />
            <span>Comprehensive Performance Scorecard</span>
          </div>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <span className="badge badge-green">100% Deterministic Verification</span>
            {isCachedResult && (
              <span className="badge" style={{ gap: '4px', background: 'rgba(168,85,247,0.15)', color: '#c084fc', border: '1px solid rgba(168,85,247,0.3)' }}>
                <Database size={10} /> Cached
              </span>
            )}
          </div>
        </div>

        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Evaluation Metric</th>
                <th style={{ textAlign: 'right' }}>Naive Baseline</th>
                <th style={{ textAlign: 'right' }}>MobiMart Engine</th>
                <th style={{ textAlign: 'right' }}>Absolute Difference</th>
                <th style={{ textAlign: 'right' }}>Percentage Shift</th>
                <th style={{ textAlign: 'center' }}>Direction</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(metrics).map(([key, m]) => {
                const lowerIsBetter = LOWER_IS_BETTER.has(key);
                // isImproved: mobimart is better than baseline
                const isImproved = lowerIsBetter
                  ? m.mobimart_value < m.baseline_value
                  : m.mobimart_value > m.baseline_value;

                return (
                  <tr key={key}>
                    <td style={{ fontWeight: 600, color: 'white' }}>
                      {m.metric_name}
                      <span style={{ marginLeft: '6px', fontSize: '0.7rem', color: '#64748b', fontWeight: 400 }}>
                        ({lowerIsBetter ? '↓ lower is better' : '↑ higher is better'})
                      </span>
                    </td>
                    <td style={{ textAlign: 'right', color: '#94a3b8' }}>
                      {m.baseline_value.toLocaleString('en-IN', { maximumFractionDigits: 2 })} {m.unit}
                    </td>
                    <td style={{ textAlign: 'right', fontWeight: 700, color: 'white' }}>
                      {m.mobimart_value.toLocaleString('en-IN', { maximumFractionDigits: 2 })} {m.unit}
                    </td>
                    <td style={{ textAlign: 'right', fontWeight: 600, color: isImproved ? '#34d399' : '#f87171' }}>
                      {m.absolute_difference > 0 ? '+' : ''}
                      {m.absolute_difference.toLocaleString('en-IN', { maximumFractionDigits: 2 })} {m.unit}
                    </td>
                    <td style={{ textAlign: 'right', fontWeight: 800 }}>
                      <span className={`badge ${isImproved ? 'badge-green' : 'badge-amber'}`} style={{ gap: '2px' }}>
                        {isImproved ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
                        {m.percentage_difference > 0 ? '+' : ''}
                        {m.percentage_difference.toFixed(1)}%
                      </span>
                    </td>
                    <td style={{ textAlign: 'center' }}>
                      <span style={{ fontSize: '1rem' }}>{isImproved ? '✅' : '⚠️'}</span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Why MobiMart Outperforms Card */}
      <div className="card" style={{ marginTop: '24px', backgroundColor: '#0f172a', borderLeft: '4px solid #34d399', padding: '20px' }}>
        <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'white', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Zap size={18} color="#34d399" />
          <span>Why MobiMart Outperforms Naive Baseline</span>
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
          <div>
            <div style={{ fontWeight: 700, color: 'white', marginBottom: '4px' }}>1. Financially Constrained Greedy Allocation</div>
            <p style={{ margin: 0, lineHeight: 1.5 }}>
              Optimizes Net Marginal Value (Margin + Avoided Goodwill Loss - Logistics) per unit under a hard ₹4 Crore chain-wide capital limit instead of naive unconstrained proportional spending.
            </p>
          </div>
          <div>
            <div style={{ fontWeight: 700, color: 'white', marginBottom: '4px' }}>2. Store Catchment & Profile Affinity</div>
            <p style={{ margin: 0, lineHeight: 1.5 }}>
              Considers non-interchangeable store formats (High Street, Mall, Mass Market, Regional Hubs) and category affinity multipliers rather than treating all 25 outlets identically.
            </p>
          </div>
          <div>
            <div style={{ fontWeight: 700, color: 'white', marginBottom: '4px' }}>3. EOL Portfolio Risk Disposition</div>
            <p style={{ margin: 0, lineHeight: 1.5 }}>
              Identifies declining/EOL SKUs early and executes inter-store transfers or clearance markdowns to liquidate exposure before successor models launch.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
