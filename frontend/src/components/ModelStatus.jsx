/**
 * ModelStatus.jsx
 * Minimal status indicator — dot + label only.
 * No background pill, no glow. Colour is strictly for status semantics.
 */

const STATUS_META = {
  ready:       { label: 'System ready',        dotColor: '#22c55e' },  /* green-500  */
  processing:  { label: 'Processing',          dotColor: '#d97706' },  /* amber-600  */
  waiting:     { label: 'Awaiting data',       dotColor: '#d97706' },  /* amber-600  */
  unavailable: { label: 'System unavailable',  dotColor: '#dc2626' },  /* red-600    */
};

export default function ModelStatus({ status }) {
  const meta = STATUS_META[status] || STATUS_META['unavailable'];

  return (
    <div
      className="flex items-center gap-2"
      aria-live="polite"
      aria-label={`System status: ${meta.label}`}
    >
      <span
        className="inline-block rounded-full flex-shrink-0"
        style={{ width: 6, height: 6, background: meta.dotColor }}
      />
      <span style={{ fontSize: '11px', color: 'var(--text-secondary)', letterSpacing: '0.04em' }}>
        {meta.label}
      </span>
    </div>
  );
}
