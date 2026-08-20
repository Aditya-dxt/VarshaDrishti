/**
 * ErrorState.jsx — Light theme. Clean error presentation.
 */
import { RefreshCw } from 'lucide-react';

export default function ErrorState({ message, onRetry }) {
  return (
    <div
      className="animate-fade-in"
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
        padding: '40px 24px',
      }}
      role="alert"
    >
      <p style={{ color: 'var(--text-primary)', fontWeight: 600, margin: '0 0 6px', fontSize: '14px' }}>
        Unable to load data
      </p>
      <p style={{ color: 'var(--text-muted)', fontSize: '12px', maxWidth: 320, lineHeight: 1.6, margin: '0 0 20px' }}>
        {message || 'An unexpected error occurred. Check the prediction service and try again.'}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="btn"
          style={{ borderColor: 'var(--risk-impact)', color: 'var(--risk-impact)' }}
        >
          <RefreshCw size={11} />
          Retry
        </button>
      )}
    </div>
  );
}
