import React from 'react';
import { RefreshCw, Calendar, Server } from 'lucide-react';

interface TopbarProps {
  title: string;
  planningWeek: number;
  onWeekChange: (week: number) => void;
  onRefresh: () => void;
  apiConnected: boolean;
  loading: boolean;
}

export const Topbar: React.FC<TopbarProps> = ({
  title,
  planningWeek,
  onWeekChange,
  onRefresh,
  apiConnected,
  loading,
}) => {
  return (
    <header className="topbar">
      {/* Title */}
      <div>
        <h1 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)' }}>{title}</h1>
      </div>

      {/* Control Actions */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        {/* Planning Week Selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', backgroundColor: 'var(--bg-input)', padding: '4px 12px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
          <Calendar size={16} color="var(--accent-blue)" />
          <span style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', fontWeight: 600 }}>Planning Week:</span>
          <select
            value={planningWeek}
            onChange={(e) => onWeekChange(Number(e.target.value))}
            className="input-select"
            style={{ padding: '2px 8px', fontSize: '0.8125rem', fontWeight: 700, color: 'var(--accent-blue)', border: 'none', background: 'transparent', cursor: 'pointer' }}
          >
            {Array.from({ length: 52 }, (_, i) => i + 1).map((w) => (
              <option key={w} value={w} style={{ backgroundColor: '#0f172a', color: 'white' }}>
                Week {w}
              </option>
            ))}
          </select>
        </div>

        {/* API Connection Indicator */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', fontWeight: 600, padding: '6px 12px', borderRadius: '6px', backgroundColor: apiConnected ? 'rgba(16, 185, 129, 0.1)' : 'rgba(244, 63, 94, 0.1)', color: apiConnected ? '#34d399' : '#f87171', border: apiConnected ? '1px solid rgba(52, 211, 153, 0.2)' : '1px solid rgba(248, 113, 113, 0.2)' }}>
          <Server size={14} />
          <span>{apiConnected ? 'FastAPI 1.0.0' : 'Disconnected'}</span>
        </div>

        {/* Refresh Button */}
        <button
          onClick={onRefresh}
          disabled={loading}
          className="btn btn-secondary"
          style={{ padding: '6px 12px', fontSize: '0.8125rem' }}
          title="Refresh API Data"
        >
          <RefreshCw size={14} className={loading ? 'spin' : ''} />
          <span>Refresh</span>
        </button>
      </div>
    </header>
  );
};
