/**
 * SHAPChart.jsx
 * Feature contribution chart. Flat bars, no rounded caps, no cyan.
 * Positive contributions in a restrained blue-gray.
 * Negative contributions in a muted orange (distinct from risk colours).
 * Only renders features supplied by the API pipeline.
 */
import EmptyState   from './EmptyState.jsx';
import LoadingState from './LoadingState.jsx';

/* Positive: muted cool blue. Negative: muted orange. Neither matches risk semantics. */
const POS_COLOR = '#5d8aa8';
const NEG_COLOR = '#c07048';

export default function SHAPChart({ shap, loading }) {
  if (loading) return <LoadingState label="Computing feature contributions…" lines={4} />;

  if (!shap?.available || !shap.features?.length) {
    return (
      <EmptyState
        title="Feature explanation unavailable"
        body="SHAP values have not been provided by the model pipeline for this prediction."
      />
    );
  }

  const sorted  = [...shap.features].sort((a, b) => Math.abs(b.contribution) - Math.abs(a.contribution));
  const maxAbs  = Math.max(...sorted.map((f) => Math.abs(f.contribution)));

  return (
    <div className="animate-fade-in">
      {sorted.map((feature, i) => {
        const isPositive = feature.contribution >= 0;
        const barPct     = Math.abs(feature.contribution) / maxAbs;
        const color      = isPositive ? POS_COLOR : NEG_COLOR;

        return (
          <div
            key={feature.name}
            style={{
              borderBottom: i < sorted.length - 1 ? '1px solid var(--border)' : 'none',
              padding: '10px 0',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
              <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                {feature.name}
              </span>
              <span
                className="mono"
                style={{ fontSize: '11px', color, letterSpacing: '0.04em' }}
              >
                {isPositive ? '+' : ''}{feature.contribution.toFixed(2)}
              </span>
            </div>
            {/* Flat bar — no radius */}
            <div
              style={{ height: 3, background: 'var(--bg-raised)', width: '100%' }}
            >
              <div
                style={{
                  height: '100%',
                  width: `${barPct * 100}%`,
                  background: color,
                  transition: 'width 0.4s ease',
                }}
              />
            </div>
          </div>
        );
      })}

      {/* Legend */}
      <div
        style={{
          display: 'flex',
          gap: 20,
          marginTop: 12,
          paddingTop: 10,
          borderTop: '1px solid var(--border)',
        }}
      >
        {[
          { color: POS_COLOR, label: 'Increases predicted risk' },
          { color: NEG_COLOR, label: 'Decreases predicted risk' },
        ].map(({ color, label }) => (
          <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ display: 'inline-block', width: 10, height: 2, background: color }} />
            <span style={{ fontSize: '10px', color: 'var(--text-muted)', letterSpacing: '0.04em' }}>
              {label}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
