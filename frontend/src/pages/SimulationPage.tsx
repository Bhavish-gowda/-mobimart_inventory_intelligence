import React, { useState } from 'react';
import { PlayCircle, TrendingUp, ShieldAlert, DollarSign, Clock, Sliders } from 'lucide-react';
import { api } from '../api/client';
import type { SimulationRunResult } from '../types';
import { KpiCard } from '../components/Common/KpiCard';
import { LoadingState } from '../components/Common/LoadingState';
import { ErrorState } from '../components/Common/ErrorState';

export const SimulationPage: React.FC = () => {
  const [strategy, setStrategy] = useState<'BASELINE' | 'MOBIMART'>('MOBIMART');
  const [startWeek, setStartWeek] = useState(1);
  const [endWeek, setEndWeek] = useState(12);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<SimulationRunResult | null>(null);

  const handleRunSimulation = async () => {
    if (loading) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.runSimulation(strategy, startWeek, endWeek);
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Simulation run failed. Please retry.');
    } finally {
      setLoading(false);
    }
  };

  const applyPreset = (sWeek: number, eWeek: number) => {
    setStartWeek(sWeek);
    setEndWeek(eWeek);
  };

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: '24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span className="badge badge-blue">Live Decision Studio</span>
            <span className="badge badge-green">Zero-Future Data Leakage</span>
          </div>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'white', letterSpacing: '-0.02em', margin: 0 }}>
            52-Week Rolling Strategy Simulator
          </h2>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '4px', margin: 0 }}>
            Stress-test the retail inventory network and watch MobiMart reallocate capital week by week
          </p>
        </div>
      </div>

      {/* Control Panel */}
      <div className="card" style={{ marginBottom: '24px', padding: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
          <div style={{ fontSize: '0.875rem', fontWeight: 700, color: 'white', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Sliders size={16} color="#38bdf8" />
            <span>Simulation Horizon & Engine Controls</span>
          </div>

          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={() => applyPreset(1, 12)}
              className="badge"
              style={{ background: startWeek === 1 && endWeek === 12 ? 'rgba(56,189,248,0.2)' : 'rgba(255,255,255,0.05)', color: '#38bdf8', cursor: 'pointer', border: '1px solid rgba(56,189,248,0.3)' }}
            >
              Q1 Preset (W1-12)
            </button>
            <button
              onClick={() => applyPreset(1, 24)}
              className="badge"
              style={{ background: startWeek === 1 && endWeek === 24 ? 'rgba(56,189,248,0.2)' : 'rgba(255,255,255,0.05)', color: '#38bdf8', cursor: 'pointer', border: '1px solid rgba(56,189,248,0.3)' }}
            >
              H1 Preset (W1-24)
            </button>
            <button
              onClick={() => applyPreset(1, 52)}
              className="badge"
              style={{ background: startWeek === 1 && endWeek === 52 ? 'rgba(56,189,248,0.2)' : 'rgba(255,255,255,0.05)', color: '#38bdf8', cursor: 'pointer', border: '1px solid rgba(56,189,248,0.3)' }}
            >
              Full Year (W1-52)
            </button>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', alignItems: 'flex-end' }}>
          <div>
            <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#94a3b8', display: 'block', marginBottom: '6px' }}>Strategy Engine</label>
            <select
              value={strategy}
              onChange={(e) => setStrategy(e.target.value as any)}
              className="input-select"
              style={{ width: '100%', fontWeight: 700, color: strategy === 'MOBIMART' ? '#38bdf8' : '#fbbf24' }}
            >
              <option value="MOBIMART">MobiMart Intelligent Engine (Greedy + EOL)</option>
              <option value="BASELINE">Naive Baseline (Last-4-Week Proportional)</option>
            </select>
          </div>

          <div>
            <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#94a3b8', display: 'block', marginBottom: '6px' }}>Start Week</label>
            <input type="number" min={1} max={52} value={startWeek} onChange={(e) => setStartWeek(Number(e.target.value))} className="input-text" style={{ width: '100%' }} />
          </div>

          <div>
            <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#94a3b8', display: 'block', marginBottom: '6px' }}>End Week</label>
            <input type="number" min={1} max={52} value={endWeek} onChange={(e) => setEndWeek(Number(e.target.value))} className="input-text" style={{ width: '100%' }} />
          </div>

          <div>
            <button onClick={handleRunSimulation} disabled={loading} className="btn btn-primary" style={{ width: '100%' }}>
              <PlayCircle size={16} />
              <span>{loading ? 'Simulating Weeks…' : `Run ${strategy} Simulation`}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Results View */}
      {loading ? (
        <LoadingState message={`Executing ${strategy} multi-week simulation — Weeks ${startWeek} to ${endWeek} (rolling zero-leakage engine)…`} />
      ) : error ? (
        <ErrorState message={error} onRetry={handleRunSimulation} />
      ) : !result ? (
        <div className="card" style={{ padding: '48px', textAlign: 'center', color: '#94a3b8' }}>
          <PlayCircle size={48} color="#38bdf8" style={{ marginBottom: '16px' }} />
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'white' }}>Decision Studio Ready</h3>
          <p style={{ fontSize: '0.875rem', marginTop: '4px' }}>Select strategy engine and week range above, then click Run Simulation.</p>
        </div>
      ) : (
        <>
          {/* Result KPI Grid */}
          <div className="grid-kpi">
            <KpiCard
              title="Total Revenue Generated"
              value={`₹${(result.total_revenue / 10000000).toFixed(2)} Cr`}
              subtext={`Gross Margin: ₹${(result.total_gross_margin / 10000000).toFixed(2)} Cr`}
              icon={DollarSign}
              iconColor="#34d399"
            />
            <KpiCard
              title="Service Level (Fill Rate)"
              value={`${result.service_level_pct.toFixed(1)}%`}
              subtext={`Fulfilled ${result.total_fulfilled_units.toLocaleString('en-IN')} units`}
              icon={TrendingUp}
              iconColor="#38bdf8"
            />
            <KpiCard
              title="Stockout Rate"
              value={`${result.stockout_rate.toFixed(1)}%`}
              subtext={`Lost Sales: ₹${(result.total_lost_sales_value / 100000).toFixed(2)} L`}
              icon={ShieldAlert}
              iconColor="#f43f5e"
            />
            <KpiCard
              title="Capital Turns"
              value={`${result.capital_turns.toFixed(2)}x`}
              subtext={`Dead Stock: ${result.dead_stock_pct.toFixed(1)}%`}
              icon={Clock}
              iconColor="#a855f7"
            />
          </div>

          {/* Weekly Results Table */}
          {result.weekly_results && result.weekly_results.length > 0 && (
            <div className="card" style={{ padding: 0 }}>
              <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ fontWeight: 700, color: 'white', fontSize: '1rem' }}>
                  Weekly Simulation Trace Ledger ({result.weekly_results.length} Weeks)
                </div>
                <span className="badge badge-blue">{result.strategy_name} Strategy Execution</span>
              </div>

              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Week</th>
                      <th style={{ textAlign: 'right' }}>Store Cost</th>
                      <th style={{ textAlign: 'right' }}>Allocated Units</th>
                      <th style={{ textAlign: 'right' }}>Fulfilled Units</th>
                      <th style={{ textAlign: 'right' }}>Demand Units</th>
                      <th style={{ textAlign: 'right' }}>Weekly Revenue</th>
                      <th style={{ textAlign: 'right' }}>Weekly Margin</th>
                      <th style={{ textAlign: 'right' }}>Ending Store Cost</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.weekly_results.map((wk: any) => (
                      <tr key={wk.week_number}>
                        <td style={{ fontWeight: 700, color: '#38bdf8' }}>Week {wk.week_number}</td>
                        <td style={{ textAlign: 'right', color: '#94a3b8' }}>₹{(wk.starting_store_cost / 100000).toFixed(2)} L</td>
                        <td style={{ textAlign: 'right', fontWeight: 700, color: wk.units_allocated > 0 ? '#34d399' : '#64748b' }}>
                          +{wk.units_allocated}
                        </td>
                        <td style={{ textAlign: 'right', fontWeight: 600 }}>{wk.fulfilled_units}</td>
                        <td style={{ textAlign: 'right', color: '#94a3b8' }}>{wk.demand_units}</td>
                        <td style={{ textAlign: 'right', fontWeight: 700, color: 'white' }}>₹{(wk.revenue / 100000).toFixed(2)} L</td>
                        <td style={{ textAlign: 'right', fontWeight: 700, color: '#34d399' }}>₹{(wk.gross_margin / 100000).toFixed(2)} L</td>
                        <td style={{ textAlign: 'right', color: '#94a3b8' }}>₹{(wk.ending_store_cost / 100000).toFixed(2)} L</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};
