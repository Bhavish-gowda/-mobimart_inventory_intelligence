import React, { useState } from 'react';
import { X, TrendingUp, Cpu, CheckCircle2 } from 'lucide-react';
import { api } from '../api/client';
import type { ForecastResponse } from '../types';

interface ForecastModalProps {
  initialStoreId?: string;
  initialProductId?: string;
  planningWeek: number;
  onClose: () => void;
}

export const ForecastModal: React.FC<ForecastModalProps> = ({
  initialStoreId = 'STORE_01',
  initialProductId = 'PROD_001',
  planningWeek,
  onClose,
}) => {
  const [storeId, setStoreId] = useState(initialStoreId);
  const [productId, setProductId] = useState(initialProductId);
  const [week, setWeek] = useState(planningWeek);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [forecast, setForecast] = useState<ForecastResponse | null>(null);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.generateForecast({
        store_id: storeId,
        product_id: productId,
        planning_week: week,
      });
      setForecast(res);
    } catch (err: any) {
      setError(err.message || 'Failed to generate forecast');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(10, 14, 23, 0.8)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100, padding: '16px' }}>
      <div className="card" style={{ width: '100%', maxWidth: '580px', backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '12px', padding: '24px', boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5)' }}>
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', paddingBottom: '12px', borderBottom: '1px solid #1e293b' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <TrendingUp size={22} color="#38bdf8" />
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'white' }}>Historical Demand Forecaster</h3>
          </div>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer' }}>
            <X size={20} />
          </button>
        </div>

        {/* Form Controls */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px', marginBottom: '20px' }}>
          <div>
            <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Store ID</label>
            <input
              type="text"
              value={storeId}
              onChange={(e) => setStoreId(e.target.value)}
              className="input-text"
              style={{ width: '100%' }}
            />
          </div>
          <div>
            <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Product SKU</label>
            <input
              type="text"
              value={productId}
              onChange={(e) => setProductId(e.target.value)}
              className="input-text"
              style={{ width: '100%' }}
            />
          </div>
          <div>
            <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Target Week</label>
            <input
              type="number"
              min={1}
              max={52}
              value={week}
              onChange={(e) => setWeek(Number(e.target.value))}
              className="input-text"
              style={{ width: '100%' }}
            />
          </div>
        </div>

        <button onClick={handleGenerate} disabled={loading} className="btn btn-primary" style={{ width: '100%', marginBottom: '20px' }}>
          <Cpu size={16} />
          <span>{loading ? 'Executing Engine Forecast...' : 'Run Demand Forecast Engine'}</span>
        </button>

        {error && (
          <div style={{ backgroundColor: 'rgba(244, 63, 94, 0.1)', border: '1px solid rgba(244, 63, 94, 0.3)', color: '#f87171', padding: '10px 14px', borderRadius: '6px', fontSize: '0.85rem', marginBottom: '16px' }}>
            {error}
          </div>
        )}

        {/* Forecast Results */}
        {forecast && (
          <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
              <div>
                <span style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Forecasted Weekly Demand</span>
                <div style={{ fontSize: '2rem', fontWeight: 800, color: '#38bdf8', fontFamily: 'var(--font-heading)' }}>
                  {forecast.forecast_weekly_demand.toFixed(1)} <span style={{ fontSize: '1rem', color: '#94a3b8' }}>units/wk</span>
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <span className="badge badge-green" style={{ gap: '4px' }}>
                  <CheckCircle2 size={12} /> Confidence: {(forecast.confidence * 100).toFixed(0)}%
                </span>
                <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>
                  Zero Future Leakage Guarded
                </div>
              </div>
            </div>

            {/* Factor Decomposition */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px', paddingTop: '12px', borderTop: '1px solid #334155', fontSize: '0.8rem' }}>
              <div>
                <span style={{ color: '#94a3b8' }}>Recent Velocity:</span>
                <div style={{ fontWeight: 600, color: 'white' }}>{forecast.recent_sales_velocity.toFixed(1)}</div>
              </div>
              <div>
                <span style={{ color: '#94a3b8' }}>6-Wk Rolling Avg:</span>
                <div style={{ fontWeight: 600, color: 'white' }}>{forecast.rolling_avg.toFixed(1)}</div>
              </div>
              <div>
                <span style={{ color: '#94a3b8' }}>Trend Factor:</span>
                <div style={{ fontWeight: 600, color: '#38bdf8' }}>{forecast.trend_factor.toFixed(2)}x</div>
              </div>
              <div>
                <span style={{ color: '#94a3b8' }}>Seasonality:</span>
                <div style={{ fontWeight: 600, color: '#fbbf24' }}>{forecast.seasonal_factor.toFixed(2)}x</div>
              </div>
              <div>
                <span style={{ color: '#94a3b8' }}>Lifecycle Factor:</span>
                <div style={{ fontWeight: 600, color: '#a855f7' }}>{forecast.lifecycle_factor.toFixed(2)}x</div>
              </div>
              <div>
                <span style={{ color: '#94a3b8' }}>Store Affinity:</span>
                <div style={{ fontWeight: 600, color: '#34d399' }}>{forecast.affinity_factor.toFixed(2)}x</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
