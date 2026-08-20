/**
 * EmptyState.jsx — Light theme. Clean empty/placeholder state.
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
      <p style={{ color: 'var(--text-secondary)', fontWeight: 600, margin: '0 0 6px', fontSize: '14px' }}>
        {title}
      </p>
      {body && (
        <p style={{ color: 'var(--text-muted)', fontSize: '12px', maxWidth: 320, lineHeight: 1.6, margin: '0 0 20px' }}>
          {body}
        </p>
      )}
      {action && onAction && (
        <button onClick={onAction} className="btn">
          {action}
        </button>
      )}
    </div>
  );
}
