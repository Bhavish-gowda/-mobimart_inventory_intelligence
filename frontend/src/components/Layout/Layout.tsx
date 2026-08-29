import React from 'react';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';

interface LayoutProps {
  currentPath: string;
  onNavigate: (path: string) => void;
  title: string;
  planningWeek: number;
  onWeekChange: (week: number) => void;
  onRefresh: () => void;
  apiConnected: boolean;
  loading: boolean;
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({
  currentPath,
  onNavigate,
  title,
  planningWeek,
  onWeekChange,
  onRefresh,
  apiConnected,
  loading,
  children,
}) => {
  return (
    <div className="app-container">
      <Sidebar currentPath={currentPath} onNavigate={onNavigate} apiConnected={apiConnected} />
      <div className="main-wrapper" style={{ marginLeft: '260px' }}>
        <Topbar
          title={title}
          planningWeek={planningWeek}
          onWeekChange={onWeekChange}
          onRefresh={onRefresh}
          apiConnected={apiConnected}
          loading={loading}
        />
        <main className="content-area">{children}</main>
      </div>
    </div>
  );
};
