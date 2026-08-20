/**
 * SHAPChart.jsx
 * Scientific feature contribution visualization.
 * Ranked bars with directional arrow indicator.
 * Positive contributions → increases risk (muted blue).
 * Negative contributions → decreases risk (muted amber).
 * No decorative effects. No rounded caps.
 */
import EmptyState   from './EmptyState.jsx';
import LoadingState from './LoadingState.jsx';

/* Positive: cool blue-slate. Negative: muted amber-orange. */
const POS_COLOR = '#5d8aa8';
const NEG_COLOR = '#b07840';

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

  const sorted = [...shap.features].sort(
    (a, b) => Math.abs(b.contribution) - Math.abs(a.contribution)
  );
  const maxAbs = Math.max(...sorted.map((f) => Math.abs(f.contribution)));

  return (
    <div className="animate-fade-in">
      {/* Rank list */}
      {sorted.map((feature, i) => {
        const isPositive = feature.contribution >= 0;
        const barPct     = maxAbs > 0 ? Math.abs(feature.contribution) / maxAbs : 0;
        const color      = isPositive ? POS_COLOR : NEG_COLOR;
        const sign       = isPositive ? '+' : '';

        return (
          <div
            key={feature.name}
            style={{
              borderBottom: i < sorted.length - 1 ? '1px solid var(--border)' : 'none',
              padding: '11px 0',
            }}
          >
            {/* Label row */}
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '7px',
              }}
            >
              <span
                style={{
                  fontSize: '12px',
                  color: 'var(--text-secondary)',
                  fontWeight: 400,
                }}
              >
                {feature.name}
              </span>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                {/* Direction arrow */}
                <span
                  style={{
                    fontSize: '10px',
                    color,
                    lineHeight: 1,
                  }}
                >
                  {isPositive ? '↑' : '↓'}
                </span>
                <span
                  className="mono"
                  style={{
                    fontSize: '11px',
                    color,
                    letterSpacing: '0.03em',
                    fontWeight: 500,
                  }}
                >
                  {sign}{feature.contribution.toFixed(2)}
                </span>
              </div>
            </div>

            {/* Bar track */}
            <div
              style={{
                height: '3px',
                background: 'var(--bg-overlay)',
                width: '100%',
              }}
            >
              <div
                style={{
                  height: '100%',
                  width: `${barPct * 100}%`,
                  background: color,
                  transition: 'width 0.45s ease',
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
          gap: '20px',
          marginTop: '14px',
          paddingTop: '12px',
          borderTop: '1px solid var(--border)',
        }}
      >
        {[
          { color: POS_COLOR, arrow: '↑', label: 'Increases predicted risk' },
          { color: NEG_COLOR, arrow: '↓', label: 'Decreases predicted risk' },
        ].map(({ color, arrow, label }) => (
          <div key={label} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ fontSize: '12px', color, lineHeight: 1 }}>{arrow}</span>
            <span
              style={{
                display: 'inline-block',
                width: '10px',
                height: '2px',
                background: color,
              }}
            />
            <span
              style={{
                fontSize: '10px',
                color: 'var(--text-muted)',
                letterSpacing: '0.03em',
              }}
            >
              {label}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
