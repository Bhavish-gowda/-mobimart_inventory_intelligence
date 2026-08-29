import React, { useEffect, useState } from 'react';
import { AlertTriangle, ArrowRightLeft, Tag, ShieldAlert, CheckCircle2, ChevronDown, ChevronUp, Info } from 'lucide-react';
import { api } from '../api/client';
import type { EOLRiskPortfolioResponse } from '../types';
import { KpiCard } from '../components/Common/KpiCard';
import { LoadingState } from '../components/Common/LoadingState';
import { ErrorState } from '../components/Common/ErrorState';

interface EolPageProps {
  planningWeek: number;
}

export const EolPage: React.FC<EolPageProps> = ({ planningWeek }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<EOLRiskPortfolioResponse | null>(null);
  const [minRiskLevel, setMinRiskLevel] = useState('MEDIUM');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const fetchEolData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getEolRiskPortfolio(planningWeek, minRiskLevel);
      setData(res);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch EOL portfolio risk assessment');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEolData();
  }, [planningWeek, minRiskLevel]);

  if (loading) return <LoadingState message={`Evaluating EOL portfolio risk for Week ${planningWeek}…`} />;
  if (error || !data) return <ErrorState message={error || 'No EOL data available'} onRetry={fetchEolData} />;

  const totalEolExposure = data.assessments.reduce((acc, a) => acc + a.inventory_value, 0);
  const criticalCount = data.assessments.filter((a) => a.risk_level === 'CRITICAL').length;
  const highCount = data.assessments.filter((a) => a.risk_level === 'HIGH').length;

  const getActionBadge = (action: string) => {
    switch (action) {
      case 'TRANSFER':
        return <span className="badge badge-green">TRANSFER</span>;
      case 'MARKDOWN':
        return <span className="badge badge-amber">MARKDOWN</span>;
      case 'HOLD':
        return <span className="badge badge-red">HOLD</span>;
      default:
        return <span className="badge badge-blue">{action}</span>;
    }
  };

  const getRiskBadge = (level: string) => {
    switch (level) {
      case 'CRITICAL':
        return <span className="badge badge-red">CRITICAL ({level})</span>;
      case 'HIGH':
        return <span className="badge badge-red">HIGH</span>;
      case 'MEDIUM':
        return <span className="badge badge-amber">MEDIUM</span>;
      default:
        return <span className="badge badge-green">LOW</span>;
    }
  };

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: '24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span className="badge badge-red">Phase 3B Engine</span>
            <span className="badge badge-blue">Disposition Decision Matrix</span>
          </div>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'white', letterSpacing: '-0.02em', margin: 0 }}>
            EOL Risk & Portfolio Transfer Center
          </h2>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '4px', margin: 0 }}>
            End-of-Life financial explainability engine & inter-store transfer capacity ledgers
          </p>
        </div>
        <div>
          <select
            value={minRiskLevel}
            onChange={(e) => setMinRiskLevel(e.target.value)}
            className="input-select"
            style={{ fontWeight: 600, color: '#38bdf8' }}
          >
            <option value="MEDIUM">Filter: MEDIUM Risk & Above</option>
            <option value="HIGH">Filter: HIGH Risk & Above</option>
            <option value="CRITICAL">Filter: CRITICAL Only</option>
            <option value="LOW">Show All Risk Levels</option>
          </select>
        </div>
      </div>

      {/* Top KPI Summary */}
      <div className="grid-kpi">
        <KpiCard
          title="EOL Inventory at Risk"
          value={`₹${(totalEolExposure / 100000).toFixed(2)} L`}
          subtext={`${data.assessments_count} Positions Assessed`}
          icon={AlertTriangle}
          iconColor="#f43f5e"
          badge={{ label: `${criticalCount} Critical, ${highCount} High`, type: 'red' }}
        />
        <KpiCard
          title="Candidate Transfer Opportunity"
          value={`₹${(data.portfolio_resolution.candidate_transfer_opportunity / 1000).toFixed(1)}k`}
          subtext="Unconstrained Transfer Value"
          icon={ArrowRightLeft}
          iconColor="#38bdf8"
        />
        <KpiCard
          title="Approved Transfer Savings"
          value={`₹${(data.portfolio_resolution.approved_transfer_opportunity / 1000).toFixed(1)}k`}
          subtext="Capacity Resolved Savings"
          icon={CheckCircle2}
          iconColor="#34d399"
          badge={{ label: 'Capacity Ledger Enforced', type: 'green' }}
        />
        <KpiCard
          title="Approved Transfer Routes"
          value={data.portfolio_resolution.approved_routes.length}
          subtext={`${data.portfolio_resolution.rejected_routes.length} Rejected Routes`}
          icon={Tag}
          iconColor="#a855f7"
        />
      </div>

      {/* Approved Transfer Routes Table */}
      {data.portfolio_resolution.approved_routes.length > 0 && (
        <div className="card" style={{ marginBottom: '24px', padding: 0 }}>
          <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ fontWeight: 700, color: 'white', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ArrowRightLeft size={18} color="#34d399" />
              <span>Approved Inter-Store Transfer Routes ({data.portfolio_resolution.approved_routes.length})</span>
            </div>
            <span className="badge badge-green">Zero-Overcommit Capacity Enforced</span>
          </div>

          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Source Store</th>
                  <th>Destination Store</th>
                  <th>Product SKU</th>
                  <th style={{ textAlign: 'right' }}>Requested Qty</th>
                  <th style={{ textAlign: 'right' }}>Approved Qty</th>
                  <th style={{ textAlign: 'right' }}>Transfer Cost</th>
                  <th style={{ textAlign: 'right' }}>Net Savings vs Hold</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {data.portfolio_resolution.approved_routes.map((route, idx) => (
                  <tr key={idx}>
                    <td style={{ fontWeight: 600, color: 'white' }}>{route.source_store_id}</td>
                    <td style={{ fontWeight: 600, color: '#38bdf8' }}>{route.destination_store_id}</td>
                    <td style={{ fontWeight: 600, color: 'white' }}>{route.product_id}</td>
                    <td style={{ textAlign: 'right' }}>{route.requested_units}</td>
                    <td style={{ textAlign: 'right', fontWeight: 800, color: '#34d399' }}>{route.approved_units}</td>
                    <td style={{ textAlign: 'right' }}>₹{route.expected_cost.toLocaleString('en-IN')}</td>
                    <td style={{ textAlign: 'right', fontWeight: 700, color: '#34d399' }}>
                      +₹{route.savings_vs_hold.toLocaleString('en-IN')}
                    </td>
                    <td>
                      <span className="badge badge-green">{route.status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Risk Assessment Table */}
      <div className="card" style={{ padding: 0 }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ fontWeight: 700, color: 'white', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ShieldAlert size={18} color="#f43f5e" />
            <span>Store-Product Risk Assessments ({data.assessments_count})</span>
          </div>
          <span className="badge badge-blue">Click Row to Expand Decision Matrix</span>
        </div>

        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th style={{ width: '36px' }}></th>
                <th>Store</th>
                <th>Product Model</th>
                <th>Lifecycle</th>
                <th style={{ textAlign: 'right' }}>Stock Units</th>
                <th style={{ textAlign: 'right' }}>Weeks Cover</th>
                <th style={{ textAlign: 'right' }}>Risk Score</th>
                <th>Risk Level</th>
                <th>Recommended Action</th>
                <th style={{ textAlign: 'right' }}>Expected Impact</th>
              </tr>
            </thead>
            <tbody>
              {data.assessments.map((a) => {
                const isExpanded = expandedId === a.assessment_id;
                return (
                  <React.Fragment key={a.assessment_id}>
                    <tr
                      onClick={() => setExpandedId(isExpanded ? null : a.assessment_id)}
                      style={{
                        cursor: 'pointer',
                        backgroundColor: isExpanded ? 'rgba(56, 189, 248, 0.05)' : a.risk_level === 'CRITICAL' ? 'rgba(244, 63, 94, 0.04)' : undefined,
                      }}
                    >
                      <td style={{ textAlign: 'center', color: '#64748b' }}>
                        {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                      </td>
                      <td style={{ fontWeight: 600, color: 'white' }}>{a.store_id}</td>
                      <td>
                        <div style={{ fontWeight: 600, color: 'white' }}>{a.product_name}</div>
                        <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{a.product_id}</div>
                      </td>
                      <td>
                        <span className="badge badge-red">{a.lifecycle_stage}</span>
                      </td>
                      <td style={{ textAlign: 'right', fontWeight: 600 }}>{a.inventory_units}</td>
                      <td style={{ textAlign: 'right', fontWeight: 600 }}>{a.weeks_of_cover.toFixed(1)} wks</td>
                      <td style={{ textAlign: 'right', fontWeight: 800, color: a.risk_score > 70 ? '#f87171' : '#fbbf24' }}>
                        {a.risk_score.toFixed(0)}/100
                      </td>
                      <td>{getRiskBadge(a.risk_level)}</td>
                      <td>{getActionBadge(a.recommended_action)}</td>
                      <td style={{ textAlign: 'right', fontWeight: 700, color: a.expected_financial_impact < 0 ? '#f87171' : '#34d399' }}>
                        ₹{a.expected_financial_impact.toLocaleString('en-IN')}
                      </td>
                    </tr>

                    {/* Decision Matrix Drawer */}
                    {isExpanded && (
                      <tr style={{ backgroundColor: '#0b1120' }}>
                        <td colSpan={10} style={{ padding: '18px 24px', borderBottom: '1px solid var(--border-color)' }}>
                          <div style={{ marginBottom: '12px', fontSize: '0.875rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <Info size={16} color="#38bdf8" />
                            <span>{a.explanation}</span>
                          </div>

                          <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'white', marginBottom: '10px' }}>
                            Disposition Decision Matrix Comparison (MARKDOWN vs TRANSFER vs HOLD):
                          </div>

                          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '12px' }}>
                            {/* Transfer Option */}
                            {a.transfer_option && (
                              <div
                                style={{
                                  padding: '12px 14px',
                                  borderRadius: '8px',
                                  background: a.recommended_action === 'TRANSFER' ? 'rgba(52, 211, 153, 0.08)' : '#0f172a',
                                  border: `1px solid ${a.recommended_action === 'TRANSFER' ? 'rgba(52, 211, 153, 0.4)' : '#334155'}`,
                                }}
                              >
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                                  <span style={{ fontWeight: 700, color: '#34d399', fontSize: '0.85rem' }}>TRANSFER OPTION</span>
                                  {a.recommended_action === 'TRANSFER' && <span className="badge badge-green">RECOMMENDED</span>}
                                </div>
                                <div style={{ fontSize: '0.8rem', color: 'white', fontWeight: 600, marginBottom: '4px' }}>
                                  {a.transfer_option.explanation}
                                </div>
                                <div style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
                                  Cost: ₹{a.transfer_option.expected_cost.toLocaleString('en-IN')} | Net Loss: ₹{a.transfer_option.net_financial_loss.toLocaleString('en-IN')}
                                </div>
                              </div>
                            )}

                            {/* Markdown Option */}
                            {a.markdown_option && (
                              <div
                                style={{
                                  padding: '12px 14px',
                                  borderRadius: '8px',
                                  background: a.recommended_action === 'MARKDOWN' ? 'rgba(245, 158, 11, 0.08)' : '#0f172a',
                                  border: `1px solid ${a.recommended_action === 'MARKDOWN' ? 'rgba(245, 158, 11, 0.4)' : '#334155'}`,
                                }}
                              >
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                                  <span style={{ fontWeight: 700, color: '#fbbf24', fontSize: '0.85rem' }}>MARKDOWN OPTION</span>
                                  {a.recommended_action === 'MARKDOWN' && <span className="badge badge-amber">RECOMMENDED</span>}
                                </div>
                                <div style={{ fontSize: '0.8rem', color: 'white', fontWeight: 600, marginBottom: '4px' }}>
                                  {a.markdown_option.explanation}
                                </div>
                                <div style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
                                  Cost: ₹{a.markdown_option.expected_cost.toLocaleString('en-IN')} | Net Loss: ₹{a.markdown_option.net_financial_loss.toLocaleString('en-IN')}
                                </div>
                              </div>
                            )}

                            {/* Hold Option */}
                            {a.hold_option && (
                              <div
                                style={{
                                  padding: '12px 14px',
                                  borderRadius: '8px',
                                  background: a.recommended_action === 'HOLD' ? 'rgba(244, 63, 94, 0.08)' : '#0f172a',
                                  border: `1px solid ${a.recommended_action === 'HOLD' ? 'rgba(244, 63, 94, 0.4)' : '#334155'}`,
                                }}
                              >
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                                  <span style={{ fontWeight: 700, color: '#f87171', fontSize: '0.85rem' }}>HOLD OPTION</span>
                                  {a.recommended_action === 'HOLD' && <span className="badge badge-red">RECOMMENDED</span>}
                                </div>
                                <div style={{ fontSize: '0.8rem', color: 'white', fontWeight: 600, marginBottom: '4px' }}>
                                  {a.hold_option.explanation}
                                </div>
                                <div style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
                                  Cost: ₹{a.hold_option.expected_cost.toLocaleString('en-IN')} | Net Loss: ₹{a.hold_option.net_financial_loss.toLocaleString('en-IN')}
                                </div>
                              </div>
                            )}
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
    </div>
  );
};
