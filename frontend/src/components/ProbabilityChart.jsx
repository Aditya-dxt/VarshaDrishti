/**
 * ProbabilityChart.jsx — Light theme
 * Clean pure-CSS horizontal bar chart.
 * Semantic color only on the highest-risk class.
 * Other classes use a neutral light gray bar.
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

  const maxKey = data.reduce((a, b) => (b.value > a.value ? b : a)).key;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {data.map(({ key, label, value, meta }) => {
        const pct = (value * 100).toFixed(1);
        const isMax = key === maxKey;
        const barColor = isMax ? meta.dotColor : '#CBD5E1';
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
                  fontWeight: isMax ? 600 : 400,
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
                  fontWeight: isMax ? 700 : 400,
                  letterSpacing: '0.02em',
                }}
              >
                {pct}%
              </span>
            </div>
            {/* Bar track */}
            <div
              style={{
                height: '4px',
                background: '#F1F5F9',
                width: '100%',
                borderRadius: 0,
              }}
            >
              <div
                style={{
                  height: '100%',
                  width: `${value * 100}%`,
                  background: barColor,
                  transition: 'width 0.5s ease',
                }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
