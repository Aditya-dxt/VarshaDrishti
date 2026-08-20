/**
 * ErrorState.jsx — flat error state. No icon circle, no coloured background.
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
      <p style={{ color: 'var(--text-primary)', fontWeight: 500, margin: '0 0 6px' }}>
        Unable to load data
      </p>
      <p style={{ color: 'var(--text-muted)', fontSize: '12px', maxWidth: 320, lineHeight: 1.6, margin: '0 0 20px' }}>
        {message || 'An unexpected error occurred. Check the prediction service and try again.'}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            padding: '8px 20px',
            background: 'transparent',
            border: '1px solid var(--risk-impact)',
            color: 'var(--risk-impact)',
            fontSize: '12px',
            letterSpacing: '0.05em',
            cursor: 'pointer',
          }}
        >
          <RefreshCw size={12} />
          Retry
        </button>
      )}
    </div>
  );
}
