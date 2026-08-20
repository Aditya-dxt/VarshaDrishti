/**
 * LoadingState.jsx — Light theme skeleton loader.
 */
export default function LoadingState({ label = 'Loading…', compact = false, lines = 3 }) {
  if (compact) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 0' }}>
        <span
          className="animate-spin-slow"
          style={{
            display: 'inline-block',
            width: 13,
            height: 13,
            borderRadius: '50%',
            border: '2px solid var(--border-mid)',
            borderTopColor: 'var(--accent)',
          }}
          aria-hidden="true"
        />
        <span style={{ color: 'var(--text-muted)', fontSize: '12px' }}>{label}</span>
      </div>
    );
  }

  return (
    <div role="status" aria-label={label} style={{ width: '100%' }}>
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="skeleton"
          style={{
            height: 14,
            marginBottom: 10,
            width: i === lines - 1 ? '55%' : '100%',
          }}
        />
      ))}
      <p style={{ color: 'var(--text-muted)', fontSize: '11px', marginTop: 14, letterSpacing: '0.04em' }}>
        {label}
      </p>
    </div>
  );
}
