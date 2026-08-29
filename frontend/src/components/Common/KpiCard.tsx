import React from 'react';
import type { LucideIcon } from 'lucide-react';

interface KpiCardProps {
  title: string;
  value: string | number;
  subtext?: string;
  icon?: LucideIcon;
  iconColor?: string;
  badge?: { label: string; type: 'green' | 'amber' | 'red' | 'blue' };
}

export const KpiCard: React.FC<KpiCardProps> = ({
  title,
  value,
  subtext,
  icon: Icon,
  iconColor = '#38bdf8',
  badge,
}) => {
  return (
    <div
      className="card"
      style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        transition: 'transform 0.15s ease, box-shadow 0.15s ease',
        cursor: 'default',
      }}
      onMouseEnter={(e) => {
        (e.currentTarget as HTMLDivElement).style.transform = 'translateY(-2px)';
        (e.currentTarget as HTMLDivElement).style.boxShadow = '0 8px 24px rgba(0,0,0,0.3)';
      }}
      onMouseLeave={(e) => {
        (e.currentTarget as HTMLDivElement).style.transform = 'translateY(0)';
        (e.currentTarget as HTMLDivElement).style.boxShadow = '';
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
        {/* Title: higher contrast */}
        <span style={{ fontSize: '0.775rem', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
          {title}
        </span>
        {Icon && (
          <div style={{
            width: '34px',
            height: '34px',
            borderRadius: '8px',
            backgroundColor: `${iconColor}18`,
            border: `1px solid ${iconColor}30`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <Icon size={18} color={iconColor} />
          </div>
        )}
      </div>

      <div>
        <div className="kpi-value" style={{ color: '#f0f6ff' }}>{value}</div>
        {subtext && (
          <div style={{ fontSize: '0.8125rem', color: '#7e94b0', marginTop: '4px', fontWeight: 500 }}>
            {subtext}
          </div>
        )}
      </div>

      {badge && (
        <div style={{ marginTop: '12px' }}>
          <span className={`badge badge-${badge.type}`}>{badge.label}</span>
        </div>
      )}
    </div>
  );
};
