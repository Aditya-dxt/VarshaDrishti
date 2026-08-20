/**
 * ProbabilityChart.jsx
 * Clean pure-CSS horizontal bar chart. No Recharts dependency.
 * Semantic color only on the highest-risk class.
 * All other classes remain neutral.
 *
 * Props:
 *   probabilities — { no_rain, moderate, heavy, high_impact } (0–1 values)
 */
import { getRiskMeta } from '../utils/riskHelpers.js';

const CLASS_ORDER = ['no_rain', 'moderate', 'heavy', 'high_impact'];

export default function ProbabilityChart({ probabilities }) {
  if (!probabilities) return null;

  const data = CLASS_ORDER.map((key) => ({
    key,
    label: getRiskMeta(key).shortLabel,
    value: probabilities[key] ?? 0,
    meta: getRiskMeta(key),
  }));

  // Find the highest probability class to highlight
  const maxKey = data.reduce((a, b) => (b.value > a.value ? b : a)).key;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
      {data.map(({ key, label, value, meta }) => {
        const pct = (value * 100).toFixed(1);
        const isMax = key === maxKey;
        const barColor = isMax ? meta.dotColor : 'rgba(255,255,255,0.08)';
        const labelColor = isMax ? meta.dotColor : 'var(--text-secondary)';
        const pctColor = isMax ? 'var(--text-primary)' : 'var(--text-muted)';

        return (
          <div key={key} title={`${label}: ${pct}%`}>
            {/* Label row */}
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'baseline',
                marginBottom: '5px',
              }}
            >
              <span
                style={{
                  fontSize: '12px',
                  color: labelColor,
                  fontWeight: isMax ? 500 : 400,
                  transition: 'color 0.2s',
                }}
              >
                {label}
              </span>
              <span
                style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: '12px',
                  color: pctColor,
                  fontWeight: isMax ? 600 : 400,
                  letterSpacing: '0.02em',
                }}
              >
                {pct}%
              </span>
            </div>
            {/* Bar track */}
            <div
              style={{
                height: '3px',
                background: 'var(--bg-overlay)',
                width: '100%',
                borderRadius: 0,
              }}
            >
              <div
                style={{
                  height: '100%',
                  width: `${value * 100}%`,
                  background: barColor,
                  transition: 'width 0.5s ease, background 0.3s',
                }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
