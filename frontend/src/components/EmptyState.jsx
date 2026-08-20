/**
 * EmptyState.jsx — flat, minimal, no icon circle or coloured containers.
 */
export default function EmptyState({ title, body, action, onAction }) {
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
      role="status"
    >
      <p style={{ color: 'var(--text-secondary)', fontWeight: 500, margin: '0 0 6px' }}>
        {title}
      </p>
      {body && (
        <p style={{ color: 'var(--text-muted)', fontSize: '12px', maxWidth: 320, lineHeight: 1.6, margin: '0 0 20px' }}>
          {body}
        </p>
      )}
      {action && onAction && (
        <button
          onClick={onAction}
          style={{
            padding: '8px 20px',
            background: 'transparent',
            border: '1px solid var(--border-mid)',
            color: 'var(--text-secondary)',
            fontSize: '12px',
            letterSpacing: '0.05em',
            cursor: 'pointer',
            transition: 'border-color 0.15s',
          }}
        >
          {action}
        </button>
      )}
    </div>
  );
}
