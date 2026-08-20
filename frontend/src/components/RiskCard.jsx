/**
 * RiskCard.jsx
 * The dominant visual element. Communicates risk through stark, large typography.
 * No gradient backgrounds. No progress bars. No decorative elements.
 * Risk colour appears only on the severity label and the left border accent.
 *
 * Props:
 *   prediction — { label, confidence }
 *   metadata   — { location, latitude, longitude, timestamp, source }
 */
import { getRiskMeta, formatTimestamp } from '../utils/riskHelpers.js';

const RISK_HEADING = {
  no_rain:     'No Rain',
  moderate:    'Moderate Rain',
  heavy:       'Heavy Rain',
  high_impact: 'High-Impact Rain',
};

export default function RiskCard({ prediction, metadata }) {
  if (!prediction || !metadata) return null;

  const { label, confidence } = prediction;
  const meta = getRiskMeta(label);
  const pct  = Math.round((confidence ?? 0) * 100);
  /* Uncertainty band — visual affordance only, derived from 1-confidence */
  const uncertainty = Math.max(1, Math.round((1 - (confidence ?? 0)) * 50));

  const latStr = metadata.latitude != null
    ? `${Math.abs(metadata.latitude).toFixed(3)}°${metadata.latitude >= 0 ? 'N' : 'S'}`
    : null;
  const lonStr = metadata.longitude != null
    ? `${Math.abs(metadata.longitude).toFixed(3)}°${metadata.longitude >= 0 ? 'E' : 'W'}`
    : null;

  return (
    <div
      className="animate-fade-in"
      style={{
        background: 'var(--bg-surface)',
        borderLeft: `3px solid ${meta.dotColor}`,
        padding: '22px 28px 20px',
      }}
      aria-live="polite"
      aria-label={`Current rainfall risk: ${meta.label}, confidence ${pct}%`}
    >
      {/* ── WHERE — observation context ────────────────────── */}
      <p className="label" style={{ marginBottom: 3 }}>Current Observation</p>
      <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: 18, lineHeight: 1.4 }}>
        {metadata.location || (latStr && lonStr ? `${latStr}, ${lonStr}` : '—')}
        <span style={{ color: 'var(--text-muted)', margin: '0 6px' }}>·</span>
        {formatTimestamp(metadata.timestamp)}
      </p>

      {/* ── WHAT — risk heading ────────────────────────────── */}
      <h1
        style={{
          fontSize: '34px',
          fontWeight: 700,
          lineHeight: 1.05,
          color: meta.dotColor,
          margin: '0 0 4px',
          letterSpacing: '-0.01em',
        }}
      >
        {RISK_HEADING[label] || meta.label}
      </h1>

      {/* ── HOW CONFIDENT — number + uncertainty ──────────── */}
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, marginBottom: 18 }}>
        <span
          style={{
            fontSize: '40px',
            fontWeight: 300,
            lineHeight: 1,
            color: 'var(--text-primary)',
            fontFamily: 'var(--font-mono)',
            letterSpacing: '-0.02em',
          }}
        >
          {pct}%
        </span>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
          <span style={{ fontSize: '10px', color: 'var(--text-muted)', letterSpacing: '0.06em', textTransform: 'uppercase' }}>
            Model Confidence
          </span>
          <span style={{ fontSize: '10px', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)', letterSpacing: '0.04em' }}>
            ±{uncertainty}% est. uncertainty
          </span>
        </div>
      </div>

      {/* ── Divider ───────────────────────────────────────── */}
      <div className="rule" />

      {/* ── Classification badge + provenance ─────────────── */}
      <div style={{ marginTop: 14, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 10 }}>
        <span
          className={`risk-badge-${label === 'no_rain' ? 'none' : label === 'high_impact' ? 'impact' : label} text-xs font-medium`}
          style={{ padding: '3px 10px', fontSize: '11px', letterSpacing: '0.05em' }}
        >
          {meta.shortLabel}
        </span>

        {/* Provenance — source instrument + coordinates */}
        {(metadata.source || (latStr && lonStr)) && (
          <dl
            style={{
              display: 'flex',
              flexDirection: 'column',
              gap: 2,
              margin: 0,
              textAlign: 'right',
            }}
          >
            {metadata.source && (
              <dd
                className="coord"
                style={{ margin: 0, fontSize: '10px', color: 'var(--text-muted)' }}
              >
                {metadata.source}
              </dd>
            )}
            {latStr && lonStr && (
              <dd
                className="coord"
                style={{ margin: 0, fontSize: '10px', color: 'var(--text-muted)' }}
              >
                {latStr} &nbsp; {lonStr}
              </dd>
            )}
          </dl>
        )}
      </div>
    </div>
  );
}
