/**
 * PageHeader.jsx — Reusable page header component
 *
 * Sticky page header with breadcrumb, optional subtitle, and right slot.
 * Consistent across all three pages.
 *
 * Props:
 *   page    — current page name string
 *   sub     — subtitle / status line (node or string)
 *   right   — right-side slot (node)
 */
export default function PageHeader({ page, sub, right }) {
  return (
    <header className="page-header">
      <div>
        {/* Breadcrumb */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            marginBottom: sub ? '3px' : 0,
          }}
        >
          <span
            style={{
              fontSize: '11px',
              color: 'var(--text-dim)',
              fontWeight: 500,
              letterSpacing: '0.05em',
              textTransform: 'uppercase',
            }}
          >
            BHOOMIDRISHTI
          </span>
          <span style={{ color: 'var(--text-dim)', fontSize: '11px' }}>/</span>
          <span
            style={{
              fontSize: '11px',
              color: 'var(--text-muted)',
              fontWeight: 500,
              letterSpacing: '0.05em',
              textTransform: 'uppercase',
            }}
          >
            {page}
          </span>
        </div>
        {/* Subtitle */}
        {sub && (
          <div
            style={{
              fontSize: '12px',
              color: 'var(--text-muted)',
              lineHeight: 1.4,
            }}
          >
            {sub}
          </div>
        )}
      </div>

      {/* Right slot */}
      {right && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {right}
        </div>
      )}
    </header>
  );
}
