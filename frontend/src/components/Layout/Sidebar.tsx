import React from 'react';
import {
  LayoutDashboard,
  Boxes,
  Store,
  Smartphone,
  Sliders,
  AlertTriangle,
  PlayCircle,
  BarChart3,
} from 'lucide-react';

interface SidebarProps {
  currentPath: string;
  onNavigate: (path: string) => void;
  apiConnected: boolean;
}

const NavItem: React.FC<{
  label: string;
  icon: React.ComponentType<{ size?: number; color?: string }>;
  isActive: boolean;
  onClick: () => void;
  badge?: string;
}> = ({ label, icon: Icon, isActive, onClick, badge }) => (
  <button
    onClick={onClick}
    title={label}
    style={{
      display: 'flex',
      alignItems: 'center',
      gap: '10px',
      padding: '9px 14px',
      borderRadius: '8px',
      fontSize: '0.875rem',
      fontWeight: isActive ? 700 : 500,
      color: isActive ? '#ffffff' : '#94a3b8',
      backgroundColor: isActive ? 'rgba(56, 189, 248, 0.16)' : 'transparent',
      border: isActive ? '1px solid rgba(56, 189, 248, 0.4)' : '1px solid transparent',
      cursor: 'pointer',
      textAlign: 'left',
      width: '100%',
      transition: 'all 0.18s ease-in-out',
      outline: 'none',
      position: 'relative',
      boxShadow: isActive ? '0 2px 8px rgba(56, 189, 248, 0.15)' : 'none',
    }}
    onMouseEnter={(e) => {
      if (!isActive) {
        (e.currentTarget as HTMLButtonElement).style.backgroundColor = 'rgba(255, 255, 255, 0.06)';
        (e.currentTarget as HTMLButtonElement).style.color = '#e2e8f0';
      }
    }}
    onMouseLeave={(e) => {
      if (!isActive) {
        (e.currentTarget as HTMLButtonElement).style.backgroundColor = 'transparent';
        (e.currentTarget as HTMLButtonElement).style.color = '#94a3b8';
      }
    }}
  >
    <Icon size={18} color={isActive ? '#38bdf8' : '#64748b'} />
    <span style={{ flex: 1 }}>{label}</span>
    {badge && (
      <span style={{ fontSize: '0.65rem', background: 'rgba(244, 63, 94, 0.2)', color: '#f87171', padding: '2px 6px', borderRadius: '4px', fontWeight: 700 }}>
        {badge}
      </span>
    )}
    {isActive && (
      <div style={{ width: '3px', height: '18px', background: '#38bdf8', borderRadius: '2px', position: 'absolute', left: 0, top: '50%', transform: 'translateY(-50%)', boxShadow: '0 0 8px #38bdf8' }} />
    )}
  </button>
);

const NavGroup: React.FC<{ label: string; children: React.ReactNode }> = ({ label, children }) => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
    <div style={{
      padding: '6px 14px 4px',
      fontSize: '0.7rem',
      fontWeight: 800,
      color: '#cbd5e1',
      textTransform: 'uppercase',
      letterSpacing: '0.08em',
      marginBottom: '2px',
    }}>
      {label}
    </div>
    {children}
  </div>
);

export const Sidebar: React.FC<SidebarProps> = ({ currentPath, onNavigate, apiConnected }) => {
  return (
    <aside className="sidebar" style={{ position: 'fixed', top: 0, left: 0, height: '100vh', overflowY: 'auto' }}>
      {/* Brand Header */}
      <div style={{
        padding: '20px 20px 18px',
        borderBottom: '1px solid var(--border-color)',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        background: 'linear-gradient(180deg, rgba(2, 132, 199, 0.08) 0%, transparent 100%)',
      }}>
        <div style={{
          width: '38px',
          height: '38px',
          borderRadius: '10px',
          background: 'linear-gradient(135deg, #0284c7 0%, #6366f1 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontWeight: 900,
          fontSize: '1.1rem',
          boxShadow: '0 4px 12px rgba(2, 132, 199, 0.4)',
          flexShrink: 0,
        }}>
          M
        </div>
        <div>
          <div style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, fontSize: '1.15rem', color: '#ffffff', letterSpacing: '-0.02em', lineHeight: 1.2 }}>
            MobiMart
          </div>
          <div style={{ fontSize: '0.675rem', color: '#38bdf8', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.07em', marginTop: '1px' }}>
            Inventory Intelligence
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav style={{ flex: 1, padding: '16px 10px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <NavGroup label="Command Center">
          <NavItem label="Executive Overview" icon={LayoutDashboard} isActive={currentPath === '/'} onClick={() => onNavigate('/')} />
          <NavItem label="Allocation Planner" icon={Sliders} isActive={currentPath === '/allocation'} onClick={() => onNavigate('/allocation')} />
        </NavGroup>

        <NavGroup label="Network Intelligence">
          <NavItem label="Stores Network" icon={Store} isActive={currentPath === '/stores'} onClick={() => onNavigate('/stores')} />
          <NavItem label="Products & Lifecycle" icon={Smartphone} isActive={currentPath === '/products'} onClick={() => onNavigate('/products')} />
          <NavItem label="EOL Risk Center" icon={AlertTriangle} isActive={currentPath === '/eol'} onClick={() => onNavigate('/eol')} />
          <NavItem label="Inventory Ledger" icon={Boxes} isActive={currentPath === '/inventory'} onClick={() => onNavigate('/inventory')} />
        </NavGroup>

        <NavGroup label="Analytics & Benchmark">
          <NavItem label="Benchmark Scorecard" icon={BarChart3} isActive={currentPath === '/benchmark'} onClick={() => onNavigate('/benchmark')} />
          <NavItem label="Decision Simulator" icon={PlayCircle} isActive={currentPath === '/simulation'} onClick={() => onNavigate('/simulation')} />
        </NavGroup>
      </nav>

      {/* Footer System Status */}
      <div style={{ padding: '16px 18px', borderTop: '1px solid var(--border-color)', backgroundColor: 'rgba(15, 23, 42, 0.6)' }}>
        <div style={{ fontSize: '0.72rem', color: '#94a3b8', marginBottom: '6px', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
          System Status
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: apiConnected ? '#34d399' : '#f87171',
            boxShadow: apiConnected ? '0 0 10px #34d399' : '0 0 10px #f87171',
          }} />
          <span style={{ fontSize: '0.825rem', color: apiConnected ? '#34d399' : '#f87171', fontWeight: 700 }}>
            {apiConnected ? 'API Connected' : 'API Offline'}
          </span>
        </div>
        <div style={{ marginTop: '4px', fontSize: '0.725rem', color: '#64748b', fontWeight: 500 }}>
          FastAPI · Python 3 · React Engine
        </div>
      </div>
    </aside>
  );
};
