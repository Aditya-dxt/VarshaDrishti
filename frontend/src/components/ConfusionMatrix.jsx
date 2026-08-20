/**
 * ConfusionMatrix.jsx — flat, clinical rendering.
 * No decorative borders or card wrappers.
 * Diagonal (correct) → muted blue. Off-diagonal (errors) → muted amber.
 */
export default function ConfusionMatrix({ matrix, labels }) {
  if (!matrix || !labels) return null;

  const allValues = matrix.flat();
  const maxVal    = Math.max(...allValues);

  const cellStyle = (value, row, col) => {
    const isDiag  = row === col;
    const opacity = value / maxVal;
    const bg = isDiag
      ? `rgba(93,138,168,${0.08 + opacity * 0.45})`   /* blue for correct */
      : `rgba(192,112,72,${opacity * 0.40})`;          /* amber for errors */
    return {
      background:  bg,
      color:       isDiag
        ? (opacity > 0.45 ? '#c8dde8' : 'var(--text-secondary)')
        : (opacity > 0.3  ? '#e8c8a8' : 'var(--text-muted)'),
      fontWeight:  isDiag ? 600 : 400,
      fontSize:    '13px',
      fontFamily:  'var(--font-mono)',
      textAlign:   'center',
      padding:     '11px 8px',
    };
  };

  return (
    <div style={{ overflowX: 'auto' }}>
      <table
        role="table"
        aria-label="Confusion matrix"
        style={{ borderCollapse: 'collapse', minWidth: 360 }}
      >
        <thead>
          <tr>
            <th style={{ padding: '4px 12px 4px 0', fontFamily: 'var(--font-mono)', fontSize: '10px', color: 'var(--text-muted)', letterSpacing: '0.06em', textAlign: 'right', fontWeight: 400 }}>
              actual ↓ predicted →
            </th>
            {labels.map((l) => (
              <th
                key={`col-${l}`}
                style={{
                  padding: '4px 8px',
                  fontSize: '10px',
                  fontWeight: 600,
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
                  padding: '4px 12px 4px 0',
                  fontSize: '10px',
                  fontWeight: 600,
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
      <div style={{ display: 'flex', gap: 20, marginTop: 16 }}>
        {[
          { color: 'rgba(93,138,168,0.55)',   label: 'Correct prediction' },
          { color: 'rgba(192,112,72,0.45)',   label: 'Misclassification'  },
        ].map(({ color, label }) => (
          <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ display: 'inline-block', width: 12, height: 12, background: color }} />
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
