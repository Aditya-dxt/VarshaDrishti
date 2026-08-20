/**
 * Metrics.jsx — Redesigned as a clean data report.
 * No card tiles. Overall metrics in a flat table row.
 * Per-class as a proper data table. Confusion matrix full-width.
 * Radar chart retained — it communicates multi-dimensional profile efficiently.
 */
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis,
  ResponsiveContainer, Tooltip as ReTooltip,
} from 'recharts';
import { useMetrics }       from '../hooks/useMetrics.js';
import { formatMetric }     from '../utils/riskHelpers.js';
import ConfusionMatrix      from '../components/ConfusionMatrix.jsx';
import LoadingState         from '../components/LoadingState.jsx';
import ErrorState           from '../components/ErrorState.jsx';
import EmptyState           from '../components/EmptyState.jsx';

/* ── Overall metrics — flat inline strip ─────────────────── */
function OverallStrip({ overall }) {
  if (!overall) return null;
  const items = [
    { key: 'accuracy',  label: 'Accuracy'  },
    { key: 'precision', label: 'Precision' },
    { key: 'recall',    label: 'Recall'    },
    { key: 'f1',        label: 'F1 Score'  },
    { key: 'roc_auc',   label: 'ROC-AUC'  },
  ];

  return (
    <div
      style={{
        display: 'flex',
        borderBottom: '1px solid var(--border)',
      }}
    >
      {items.map(({ key, label }, i) => {
        const val = overall[key];
        return (
          <div
            key={key}
            style={{
              flex: 1,
              padding: '20px 24px',
              borderRight: i < items.length - 1 ? '1px solid var(--border)' : 'none',
            }}
          >
            <p className="label" style={{ marginBottom: 6 }}>{label}</p>
            <span
              className="mono"
              style={{
                fontSize: '28px',
                fontWeight: 300,
                color: val != null ? 'var(--text-primary)' : 'var(--text-dim)',
                letterSpacing: '-0.02em',
              }}
            >
              {val != null ? (val * 100).toFixed(1) + '%' : '—'}
            </span>
          </div>
        );
      })}
    </div>
  );
}

/* ── Per-class breakdown table ───────────────────────────── */
function PerClassTable({ perClass }) {
  if (!perClass) return null;
  const rows = [
    { key: 'no_rain',     label: 'No Rain'      },
    { key: 'moderate',    label: 'Moderate Rain' },
    { key: 'heavy',       label: 'Heavy Rain'    },
    { key: 'high_impact', label: 'High Impact'   },
  ];

  return (
    <table className="data-table">
      <thead>
        <tr>
          {['Class', 'Precision', 'Recall', 'F1', 'Support'].map((h) => (
            <th key={h}>{h}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map(({ key, label }) => {
          const d = perClass[key];
          return (
            <tr key={key}>
              <td style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{label}</td>
              <td className="mono">{formatMetric(d?.precision)}</td>
              <td className="mono">{formatMetric(d?.recall)}</td>
              <td className="mono" style={{ color: 'var(--text-primary)' }}>{formatMetric(d?.f1)}</td>
              <td className="mono" style={{ color: 'var(--text-muted)' }}>{d?.support ?? '—'}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

/* ── Radar ───────────────────────────────────────────────── */
function PerformanceRadar({ overall }) {
  if (!overall) return null;
  const radarData = [
    { metric: 'Accuracy',  value: overall.accuracy  },
    { metric: 'Precision', value: overall.precision },
    { metric: 'Recall',    value: overall.recall    },
    { metric: 'F1 Score',  value: overall.f1        },
    { metric: 'ROC-AUC',   value: overall.roc_auc   },
  ].filter((d) => d.value != null);

  return (
    <div style={{ width: '100%', height: 220 }}>
      <ResponsiveContainer>
        <RadarChart data={radarData} margin={{ top: 10, right: 28, bottom: 10, left: 28 }}>
          <PolarGrid stroke="rgba(255,255,255,0.06)" />
          <PolarAngleAxis
            dataKey="metric"
            tick={{ fill: 'var(--text-muted)', fontSize: 10, fontFamily: 'var(--font-mono)' }}
          />
          <Radar
            name="Score"
            dataKey="value"
            stroke="var(--accent)"
            fill="var(--accent)"
            fillOpacity={0.12}
            dot={{ r: 2, fill: 'var(--accent)' }}
          />
          <ReTooltip
            formatter={(v) => [(v * 100).toFixed(1) + '%', 'Score']}
            contentStyle={{
              background: 'var(--bg-raised)',
              border: '1px solid var(--border-mid)',
              fontSize: 12,
              borderRadius: 2,
            }}
            labelStyle={{ color: 'var(--text-primary)' }}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}

/* ── Section heading inside the page ─────────────────────── */
function SecHead({ children }) {
  return (
    <p
      className="label"
      style={{
        padding: '16px 28px 12px',
        borderBottom: '1px solid var(--border)',
        margin: 0,
      }}
    >
      {children}
    </p>
  );
}

/* ── Page ─────────────────────────────────────────────────── */
export default function Metrics() {
  const { data, loading, error } = useMetrics();

  return (
    <main
      className="animate-fade-in"
      style={{ maxWidth: 1400, margin: '0 auto' }}
    >
      {/* Page heading */}
      <div style={{ padding: '20px 28px 14px', borderBottom: '1px solid var(--border)' }}>
        <h1
          style={{
            fontSize: '18px',
            fontWeight: 600,
            color: 'var(--text-primary)',
            margin: '0 0 4px',
            letterSpacing: '-0.01em',
          }}
        >
          Model Performance
        </h1>
        <p style={{ fontSize: '13px', color: 'var(--text-secondary)', margin: 0 }}>
          Evaluation results from the trained 3D-CNN on the held-out test set.
          All figures are provided directly by the ML pipeline — no fabricated values.
        </p>
      </div>

      {loading && (
        <div style={{ padding: '40px 28px' }}>
          <LoadingState label="Loading model performance…" lines={8} />
        </div>
      )}
      {error && (
        <div style={{ padding: '40px 28px' }}>
          <ErrorState message={error} />
        </div>
      )}

      {!loading && !error && !data?.available && (
        <div style={{ padding: '40px 28px' }}>
          <EmptyState
            title="Metrics unavailable"
            body="Evaluation results have not been provided by the model pipeline yet. Run evaluation on the test set to populate this page."
          />
        </div>
      )}

      {data?.available && (
        <div className="animate-fade-in">
          {/* Context */}
          {(data.evaluation_set || data.evaluated_at) && (
            <div style={{ padding: '8px 28px', borderBottom: '1px solid var(--border)' }}>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)', letterSpacing: '0.04em' }}>
                {data.evaluation_set}
                {data.evaluated_at && (
                  <> · Evaluated {new Date(data.evaluated_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}</>
                )}
              </span>
            </div>
          )}

          {/* Overall strip */}
          <OverallStrip overall={data.overall} />

          {/* Radar + per-class side by side */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', borderBottom: '1px solid var(--border)' }}>
            <div style={{ borderRight: '1px solid var(--border)' }}>
              <SecHead>Performance Profile</SecHead>
              <div style={{ padding: '0 24px 24px' }}>
                <PerformanceRadar overall={data.overall} />
              </div>
            </div>
            <div>
              <SecHead>Per-Class Breakdown</SecHead>
              <div style={{ padding: '0 0 24px' }}>
                <PerClassTable perClass={data.per_class} />
              </div>
            </div>
          </div>

          {/* Confusion matrix */}
          <SecHead>Confusion Matrix</SecHead>
          <div style={{ padding: '0 28px 40px' }}>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: 20, marginTop: 12 }}>
              Rows = actual class · Columns = predicted class
            </p>
            {data.confusion_matrix ? (
              <ConfusionMatrix
                matrix={data.confusion_matrix.matrix}
                labels={data.confusion_matrix.labels}
              />
            ) : (
              <EmptyState title="Confusion matrix unavailable" body="Not provided by the evaluation pipeline." />
            )}
          </div>
        </div>
      )}
    </main>
  );
}
