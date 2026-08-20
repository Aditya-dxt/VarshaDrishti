/**
 * RiskCard.jsx — Light theme
 * Primary risk summary panel.
 * WHAT? HOW CONFIDENT? Risk color on label + left border only.
 * Dark charcoal text on white surface. Clean, scientific.
 *
 * Props:
 *   prediction — { label, confidence }
 *   metadata   — { location, latitude, longitude, timestamp, source }
 *   compact    — boolean, smaller layout for historical detail
 */
import { getRiskMeta, formatTimestamp } from '../utils/riskHelpers.js';

const RISK_HEADING = {
  no_rain:     'No Rain',
  moderate:    'Moderate Rain',
  heavy:       'Heavy Rain',
  high_impact: 'High-Impact Rain',
};

export default function RiskCard({ prediction, metadata, compact = false }) {
  if (!prediction || !metadata) return null;

  const { label, confidence } = prediction;
  const meta = getRiskMeta(label);
  const pct  = Math.round((confidence ?? 0) * 100);
  const uncertainty = Math.max(1, Math.round((1 - (confidence ?? 0)) * 50));

  const latStr = metadata.latitude != null
    ? `${Math.abs(metadata.latitude).toFixed(3)}°${metadata.latitude >= 0 ? 'N' : 'S'}`
    : null;
  const lonStr = metadata.longitude != null
    ? `${Math.abs(metadata.longitude).toFixed(3)}°${metadata.longitude >= 0 ? 'E' : 'W'}`
    : null;

  const badgeClass = label === 'no_rain'
    ? 'risk-badge-none'
    : label === 'high_impact'
      ? 'risk-badge-impact'
      : `risk-badge-${label}`;

  return (
    <div
      className="animate-fade-in"
      style={{
        padding: compact ? '18px 24px' : '24px 28px',
        borderLeft: `3px solid ${meta.dotColor}`,
        background: 'var(--bg-surface)',
      }}
      aria-live="polite"
      aria-label={`Current rainfall risk: ${meta.label}, confidence ${pct}%`}
    >
      {/* ── Location + timestamp ────────────────────────────── */}
      <div style={{ marginBottom: '16px' }}>
        <p
          style={{
            fontSize: '13px',
            color: 'var(--text-secondary)',
            margin: '0 0 2px',
            lineHeight: 1.4,
            fontWeight: 500,
          }}
        >
          {metadata.location || (latStr && lonStr ? `${latStr}, ${lonStr}` : '—')}
        </p>
        <p style={{ fontSize: '11px', color: 'var(--text-muted)', margin: 0 }}>
          {formatTimestamp(metadata.timestamp)}
          {metadata.source && (
            <span style={{ marginLeft: '8px', color: 'var(--text-dim)' }}>
              · {metadata.source}
            </span>
          )}
        </p>
      </div>

      {/* ── Risk heading (WHAT) ─────────────────────────────── */}
      <h2
        style={{
          fontSize: compact ? '26px' : '34px',
          fontWeight: 700,
          lineHeight: 1.05,
          color: meta.dotColor,
          margin: '0 0 6px',
          letterSpacing: '-0.02em',
          fontFamily: 'var(--font-sans)',
        }}
      >
        {RISK_HEADING[label] || meta.label}
      </h2>

      {/* ── Confidence (HOW CONFIDENT) ──────────────────────── */}
      <div
        style={{
          display: 'flex',
          alignItems: 'baseline',
          gap: '10px',
          marginBottom: '20px',
        }}
      >
        <span
          style={{
            fontSize: compact ? '32px' : '42px',
            fontWeight: 300,
            lineHeight: 1,
            color: 'var(--text-primary)',
            fontFamily: 'var(--font-mono)',
            letterSpacing: '-0.02em',
          }}
        >
          {pct}%
        </span>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
          <span
            style={{
              fontSize: '10px',
              color: 'var(--text-muted)',
              letterSpacing: '0.07em',
              textTransform: 'uppercase',
              fontWeight: 700,
            }}
          >
            Confidence Level
          </span>
          <span
            style={{
              fontSize: '10px',
              color: 'var(--text-dim)',
              fontFamily: 'var(--font-mono)',
              letterSpacing: '0.02em',
            }}
          >
            ±{uncertainty}% uncertainty
          </span>
        </div>
      </div>

      {/* ── Divider ─────────────────────────────────────────── */}
      <div className="rule" />

      {/* ── Classification badge + coords ───────────────────── */}
      <div
        style={{
          marginTop: '14px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          flexWrap: 'wrap',
          gap: '10px',
        }}
      >
        <span
          className={badgeClass}
          style={{
            padding: '3px 10px',
            fontSize: '10px',
            letterSpacing: '0.07em',
            fontWeight: 700,
            textTransform: 'uppercase',
            borderRadius: '2px',
          }}
        >
          {meta.shortLabel}
        </span>

        {latStr && lonStr && (
          <span
            className="coord"
            style={{ fontSize: '10px', color: 'var(--text-dim)' }}
          >
            {latStr}&nbsp;&nbsp;{lonStr}
          </span>
        )}
      </div>
    </div>
  );
}
