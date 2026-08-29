import React from 'react';
import { AlertOctagon, RefreshCw } from 'lucide-react';

interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  message = 'Unable to connect to MobiMart FastAPI backend.',
  onRetry,
}) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '300px', gap: '16px', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '10px', padding: '32px' }}>
      <AlertOctagon size={48} color="var(--accent-rose)" />
      <div style={{ textAlign: 'center' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '4px' }}>API Error Encountered</h3>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>{message}</p>
      </div>
      {onRetry && (
        <button onClick={onRetry} className="btn btn-primary">
          <RefreshCw size={14} />
          <span>Retry Connection</span>
        </button>
      )}
    </div>
  );
};
