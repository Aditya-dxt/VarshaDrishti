/**
 * ModelStatus.jsx — Light theme. Status indicator dot + label.
 */
const STATUS_META = {
  ready:       { label: 'System Ready',        dotColor: '#16A34A' },  /* green-600  */
  processing:  { label: 'Processing',          dotColor: '#D97706' },  /* amber-600  */
  waiting:     { label: 'Awaiting data',       dotColor: '#D97706' },  /* amber-600  */
  unavailable: { label: 'System unavailable',  dotColor: '#DC2626' },  /* red-600    */
};

export default function ModelStatus({ status }) {
  const meta = STATUS_META[status] || STATUS_META['unavailable'];

  return (
    <div
      style={{ display: 'flex', alignItems: 'center', gap: '7px' }}
      aria-live="polite"
      aria-label={`System status: ${meta.label}`}
    >
      <span
        style={{
          display: 'inline-block',
          width: 7,
          height: 7,
          borderRadius: '50%',
          background: meta.dotColor,
          flexShrink: 0,
        }}
      />
      <span
        style={{
          fontSize: '11px',
          color: 'var(--text-secondary)',
          letterSpacing: '0.03em',
          fontWeight: 500,
        }}
      >
        {meta.label}
      </span>
    </div>
  );
}
