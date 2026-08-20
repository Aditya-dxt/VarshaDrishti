/**
 * SectionPanel.jsx — Reusable panel with consistent section header
 *
 * Props:
 *   label    — overline label text (uppercase)
 *   right    — optional right-side slot in header
 *   children — panel content
 *   noBorder — if true, skip bottom border on the panel itself
 *   padding  — inner content padding (default: '0 28px 24px')
 *   headerPad — header horizontal padding (default: '28px')
 */
export default function SectionPanel({
  label,
  right,
  children,
  noBorder = false,
  padding = '0 28px 24px',
  headerPad = '28px',
}) {
  return (
    <section
      style={{
        borderBottom: noBorder ? 'none' : '1px solid var(--border)',
      }}
    >
      {/* Section header */}
      {label && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: `12px ${headerPad}`,
            borderBottom: '1px solid var(--border)',
          }}
        >
          <span className="label">{label}</span>
          {right && (
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              {right}
            </span>
          )}
        </div>
      )}
      {/* Content */}
      <div style={{ padding }}>{children}</div>
    </section>
  );
}
