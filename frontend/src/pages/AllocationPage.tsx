import React, { useEffect, useState } from 'react';
import { Sliders, Zap, CheckCircle2, DollarSign, Wallet, Search, Filter, Info, ChevronDown, ChevronUp } from 'lucide-react';
import { api } from '../api/client';
import type { AllocationRunResponse } from '../types';
import { KpiCard } from '../components/Common/KpiCard';
import { LoadingState } from '../components/Common/LoadingState';
import { ErrorState } from '../components/Common/ErrorState';

interface AllocationPageProps {
  planningWeek: number;
}

export const AllocationPage: React.FC<AllocationPageProps> = ({ planningWeek }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AllocationRunResponse | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [storeFilter, setStoreFilter] = useState('ALL');
  const [expandedRecId, setExpandedRecId] = useState<string | null>(null);

  const runAllocationEngine = async () => {
    if (loading) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.runAllocation({
        planning_week: planningWeek,
        capital_budget_limit: 40000000.0,
      });
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Failed to execute allocation engine. Please retry.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runAllocationEngine();
  }, [planningWeek]);

  // Filter recommendations
  const filteredRecs = (result?.recommendations || []).filter((rec) => {
    const matchesSearch =
      rec.product_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      rec.product_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      rec.store_id.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStore = storeFilter === 'ALL' || rec.store_id === storeFilter;
    return matchesSearch && matchesStore;
  });

  const uniqueStores = Array.from(new Set((result?.recommendations || []).map((r) => r.store_id))).sort();

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: '24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span className="badge badge-blue">Phase 2 Engine</span>
            <span className="badge badge-green">Rupee Financial Proof</span>
          </div>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'white', letterSpacing: '-0.02em', margin: 0 }}>
            Allocation Control Center
          </h2>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '4px', margin: 0 }}>
            Constrained Greedy Stock Allocator under ₹4 Crore capital budget cap & finite warehouse inventory bounds
          </p>
        </div>
        <button onClick={runAllocationEngine} disabled={loading} className="btn btn-primary">
          <Zap size={16} />
          <span>{loading ? 'Running Engine…' : `Run Week ${planningWeek} Allocation`}</span>
        </button>
      </div>

      {loading ? (
        <LoadingState message={`Running Week ${planningWeek} Allocation — Evaluating store-product marginal candidates under ₹4 Cr budget cap…`} />
      ) : error ? (
        <ErrorState message={error} onRetry={runAllocationEngine} />
      ) : !result ? null : (
        <>
          {/* Summary KPI Grid */}
          <div className="grid-kpi">
            <KpiCard
              title="Total Units Allocated"
              value={result.total_units_allocated.toLocaleString('en-IN')}
              subtext={`Across ${result.recommendations.length} store-product positions`}
              icon={Sliders}
              iconColor="#38bdf8"
            />
            <KpiCard
              title="New Capital Allocated"
              value={`₹${(result.new_capital_allocated / 100000).toFixed(2)} L`}
              subtext={`Resulting Deployed: ₹${(result.resulting_capital_deployed / 10000000).toFixed(2)} Cr`}
              icon={Wallet}
              iconColor="#34d399"
            />
            <KpiCard
              title="Net Expected Benefit"
              value={`₹${(result.total_expected_net_benefit / 100000).toFixed(2)} L`}
              subtext="Margin + Avoided Goodwill - Logistics"
              icon={DollarSign}
              iconColor="#fbbf24"
              badge={{ label: 'Positive Marginal NMV', type: 'green' }}
            />
            <KpiCard
              title="Capital Headroom"
              value={`₹${(result.capital_headroom / 100000).toFixed(2)} L`}
              subtext={`Cap Limit: ₹${(result.budget_limit / 10000000).toFixed(1)} Cr`}
              icon={CheckCircle2}
              iconColor="#a855f7"
              badge={{ label: `${result.utilization_pct.toFixed(1)}% Utilized`, type: 'blue' }}
            />
          </div>

          {/* Search & Filter Bar */}
          <div
            className="card"
            style={{
              marginBottom: '20px',
              padding: '16px 20px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '16px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flex: 1, minWidth: '260px' }}>
              <Search size={18} color="#64748b" />
              <input
                type="text"
                placeholder="Search by product name, SKU ID, or store ID…"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="input-select"
                style={{ flex: 1, color: 'white' }}
              />
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <Filter size={16} color="#64748b" />
              <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Filter Store:</span>
              <select
                value={storeFilter}
                onChange={(e) => setStoreFilter(e.target.value)}
                className="input-select"
                style={{ fontWeight: 600, color: '#38bdf8' }}
              >
                <option value="ALL">All 25 Stores</option>
                {uniqueStores.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Recommendations Table */}
          <div className="card" style={{ padding: 0 }}>
            <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ fontWeight: 700, color: 'white', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span>Engine Allocation Recommendations ({filteredRecs.length})</span>
                {filteredRecs.length !== result.recommendations.length && (
                  <span style={{ fontSize: '0.75rem', color: '#64748b' }}>(Filtered from {result.recommendations.length})</span>
                )}
              </div>
              <span className="badge badge-green">Ranked by Net Marginal Value (NMV)</span>
            </div>

            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th style={{ width: '40px' }}></th>
                    <th>Priority</th>
                    <th>Store</th>
                    <th>Product</th>
                    <th style={{ textAlign: 'right' }}>Current Stock</th>
                    <th style={{ textAlign: 'right' }}>Forecast Demand</th>
                    <th style={{ textAlign: 'right' }}>Current WoC</th>
                    <th style={{ textAlign: 'right' }}>Allocated Qty</th>
                    <th style={{ textAlign: 'right' }}>NMV / Unit</th>
                    <th style={{ textAlign: 'right' }}>Total Benefit</th>
                    <th>Reason Code</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredRecs.map((rec, index) => {
                    const isExpanded = expandedRecId === rec.recommendation_id;
                    return (
                      <React.Fragment key={rec.recommendation_id}>
                        <tr
                          onClick={() => setExpandedRecId(isExpanded ? null : rec.recommendation_id)}
                          style={{ cursor: 'pointer', backgroundColor: isExpanded ? 'rgba(56, 189, 248, 0.05)' : undefined }}
                        >
                          <td style={{ textAlign: 'center', color: '#64748b' }}>
                            {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                          </td>
                          <td style={{ fontWeight: 700, color: '#38bdf8' }}>#{index + 1}</td>
                          <td>
                            <div style={{ fontWeight: 600, color: 'white' }}>{rec.store_id}</div>
                          </td>
                          <td>
                            <div style={{ fontWeight: 600, color: 'white' }}>{rec.product_name}</div>
                            <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{rec.product_id}</div>
                          </td>
                          <td style={{ textAlign: 'right' }}>{rec.current_stock}</td>
                          <td style={{ textAlign: 'right' }}>{rec.forecast_weekly_demand.toFixed(1)}/wk</td>
                          <td style={{ textAlign: 'right', fontWeight: 600 }}>{rec.current_woc.toFixed(1)} wks</td>
                          <td style={{ textAlign: 'right', fontWeight: 800, color: '#34d399', fontSize: '1rem' }}>
                            +{rec.recommended_qty}
                          </td>
                          <td style={{ textAlign: 'right', fontWeight: 600 }}>₹{rec.unit_marginal_value.toFixed(0)}</td>
                          <td style={{ textAlign: 'right', fontWeight: 700, color: '#38bdf8' }}>
                            ₹{rec.total_net_benefit.toLocaleString('en-IN')}
                          </td>
                          <td>
                            <span className="badge badge-blue">{rec.reason_code}</span>
                          </td>
                        </tr>

                        {/* Expanded Detail Financial Proof Breakdown */}
                        {isExpanded && (
                          <tr style={{ backgroundColor: '#0b1120' }}>
                            <td colSpan={11} style={{ padding: '16px 24px', borderBottom: '1px solid var(--border-color)' }}>
                              <div style={{ display: 'grid', gridTemplateColumns: '2fr 3fr', gap: '24px' }}>
                                <div>
                                  <h4 style={{ fontSize: '0.875rem', fontWeight: 700, color: 'white', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                                    <Info size={14} color="#38bdf8" />
                                    <span>Explanation Narrative</span>
                                  </h4>
                                  <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#38bdf8', marginBottom: '4px' }}>
                                    {rec.headline}
                                  </div>
                                  <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
                                    {rec.explanation_text}
                                  </p>
                                </div>

                                <div style={{ background: '#0f172a', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                                  <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'white', marginBottom: '10px' }}>
                                    Financial Proof Breakdown ({rec.recommended_qty} units)
                                  </h4>
                                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontSize: '0.8rem' }}>
                                    <div style={{ color: '#94a3b8' }}>Margin Contribution:</div>
                                    <div style={{ color: '#34d399', fontWeight: 600, textAlign: 'right' }}>
                                      +₹{rec.total_margin_contribution.toLocaleString('en-IN')}
                                    </div>
                                    <div style={{ color: '#94a3b8' }}>Avoided Goodwill Loss:</div>
                                    <div style={{ color: '#38bdf8', fontWeight: 600, textAlign: 'right' }}>
                                      +₹{rec.total_avoided_goodwill_benefit.toLocaleString('en-IN')}
                                    </div>
                                    <div style={{ color: '#94a3b8' }}>Warehouse Allocation Cost:</div>
                                    <div style={{ color: '#f87171', fontWeight: 600, textAlign: 'right' }}>
                                      -₹{rec.total_allocation_cost.toLocaleString('en-IN')}
                                    </div>
                                    <div style={{ color: 'white', fontWeight: 700, paddingTop: '4px', borderTop: '1px solid #334155' }}>
                                      Net Marginal Value:
                                    </div>
                                    <div style={{ color: '#38bdf8', fontWeight: 800, textAlign: 'right', paddingTop: '4px', borderTop: '1px solid #334155' }}>
                                      = ₹{rec.total_net_benefit.toLocaleString('en-IN')}
                                    </div>
                                  </div>
                                </div>
                              </div>
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
