/**
 * ConfusionMatrix.jsx — Light theme
 * Diagonal (correct) → light blue fill.
 * Off-diagonal (errors) → light amber fill.
 * Dark text on light backgrounds.
 */
export default function ConfusionMatrix({ matrix, labels }) {
  if (!matrix || !labels) return null;

  const allValues = matrix.flat();
  const maxVal    = Math.max(...allValues);

  const cellStyle = (value, row, col) => {
    const isDiag  = row === col;
    const opacity = value / maxVal;
    const bg = isDiag
      ? `rgba(37,99,235,${0.05 + opacity * 0.18})`    /* blue for correct */
      : `rgba(220,38,38,${opacity * 0.14})`;           /* red for errors */
    return {
      background:  bg,
      color:       isDiag
        ? (opacity > 0.4 ? '#1D4ED8' : 'var(--text-secondary)')
        : (opacity > 0.3 ? '#B91C1C' : 'var(--text-muted)'),
      fontWeight:  isDiag ? 700 : 400,
      fontSize:    '14px',
      fontFamily:  'var(--font-mono)',
      textAlign:   'center',
      padding:     '13px 10px',
    };
  };

  return (
    <div style={{ overflowX: 'auto' }}>
      <table
        role="table"
        aria-label="Confusion matrix"
        style={{ borderCollapse: 'collapse', minWidth: 400 }}
      >
        <thead>
          <tr>
            <th
              style={{
                padding: '6px 14px 6px 0',
                fontFamily: 'var(--font-mono)',
                fontSize: '10px',
                color: 'var(--text-muted)',
                letterSpacing: '0.04em',
                textAlign: 'right',
                fontWeight: 400,
                borderRight: '1px solid var(--border)',
              }}
            >
              actual ↓ predicted →
            </th>
            {labels.map((l) => (
              <th
                key={`col-${l}`}
                style={{
                  padding: '6px 10px',
                  fontSize: '10px',
                  fontWeight: 700,
                  color: 'var(--text-muted)',
                  letterSpacing: '0.07em',
                  textAlign: 'center',
                  textTransform: 'uppercase',
                }}
              >
                {l}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {matrix.map((row, ri) => (
            <tr key={ri}>
              <td
                style={{
                  padding: '6px 14px 6px 0',
                  fontSize: '10px',
                  fontWeight: 700,
                  color: 'var(--text-muted)',
                  letterSpacing: '0.07em',
                  textAlign: 'right',
                  textTransform: 'uppercase',
                  whiteSpace: 'nowrap',
                  borderRight: '1px solid var(--border)',
                }}
              >
                {labels[ri]}
              </td>
              {row.map((val, ci) => (
                <td key={ci} style={cellStyle(val, ri, ci)}>
                  {val.toLocaleString()}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>

      {/* Legend */}
      <div style={{ display: 'flex', gap: '20px', marginTop: '16px' }}>
        {[
          { color: 'rgba(37,99,235,0.18)',  label: 'Correct prediction' },
          { color: 'rgba(220,38,38,0.14)',  label: 'Misclassification'  },
        ].map(({ color, label }) => (
          <div key={label} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span
              style={{
                display: 'inline-block',
                width: 12,
                height: 12,
                background: color,
                border: '1px solid var(--border-mid)',
              }}
            />
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
