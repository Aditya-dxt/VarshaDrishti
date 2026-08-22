/**
 * Metrics.jsx — Model Performance page
 *
 * Layout:
 * ┌──────────────────────────────────────────────────────┐
 * │ PAGE HEADER                                          │
 * ├──────────────────────────────────────────────────────┤
 * │ OVERALL METRICS (5-metric strip, full width)        │
 * ├────────────────────────┬─────────────────────────────┤
 * │ PERFORMANCE PROFILE    │ PER-CLASS BREAKDOWN          │
 * │ (Radar chart)          │ (data table)                 │
 * ├────────────────────────┴─────────────────────────────┤
 * │ CONFUSION MATRIX (full width, large)                 │
 * └──────────────────────────────────────────────────────┘
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
import PageHeader           from '../components/PageHeader.jsx';

/* ── Overall metrics strip ───────────────────────────────── */
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
        const numStr = val != null ? (val * 100).toFixed(1) + '%' : '—';
        return (
          <div
            key={key}
            style={{
              flex: 1,
              padding: '24px 24px 22px',
              borderRight: i < items.length - 1 ? '1px solid var(--border)' : 'none',
            }}
          >
            <p className="metric-label">{label}</p>
            <span
              className="metric-value"
              style={{
                color: val != null ? 'var(--text-primary)' : 'var(--text-dim)',
              }}
            >
              {numStr}
            </span>
          </div>
        );
      })}
    </div>
  );
}

/* ── Per-class breakdown table ──────────────────────────── */
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

/* ── Radar chart ───────────────────────────────────────── */
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
    <div style={{ width: '100%', height: 240 }}>
      <ResponsiveContainer>
        <RadarChart data={radarData} margin={{ top: 12, right: 32, bottom: 12, left: 32 }}>
          <PolarGrid stroke="rgba(0,0,0,0.08)" />
          <PolarAngleAxis
            dataKey="metric"
            tick={{
              fill: 'var(--text-muted)',
              fontSize: 10,
              fontFamily: 'var(--font-mono)',
              letterSpacing: '0.04em',
            }}
          />
          <Radar
            name="Score"
            dataKey="value"
            stroke="var(--accent)"
            fill="var(--accent)"
            fillOpacity={0.10}
            dot={{ r: 2, fill: 'var(--accent)' }}
          />
          <ReTooltip
            formatter={(v) => [(v * 100).toFixed(1) + '%', 'Score']}
            contentStyle={{
              background: 'var(--bg-overlay)',
              border: '1px solid var(--border-mid)',
              fontSize: 12,
              borderRadius: 2,
              fontFamily: 'var(--font-sans)',
            }}
            labelStyle={{ color: 'var(--text-primary)' }}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}

/* ── Section label ──────────────────────────────────────── */
function SectionLabel({ children, right }) {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '11px 28px',
        borderBottom: '1px solid var(--border)',
      }}
    >
      <span className="label">{children}</span>
      {right && (
        <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{right}</span>
      )}
    </div>
  );
}

/* ── Page ─────────────────────────────────────────────────── */
export default function Metrics() {
  const { data, loading, error } = useMetrics();

  /* Evaluation context string for subtitle */
  const subText = data?.evaluated_at
    ? `Evaluated ${new Date(data.evaluated_at).toLocaleDateString('en-IN', {
        day: '2-digit', month: 'short', year: 'numeric',
      })}${data.evaluation_set ? ` · ${data.evaluation_set}` : ''}`
    : 'Evaluation results from the trained 3D-CNN';

  return (
    <main className="animate-fade-in">

      {/* Page header */}
      <PageHeader
        page="Model Performance"
        sub={subText}
      />

      <div style={{ padding: '12px 28px', background: '#FEF3C7', color: '#92400E', fontSize: '13px', borderBottom: '1px solid #FCD34D' }}>
        <strong>DEVELOPMENT / PROOF-OF-CONCEPT TRAINING ONLY:</strong> Only two independent weather events were available for this evaluation. Results must NOT be interpreted as scientifically generalizable model performance.
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

      {!loading && !error && !data && (
        <div style={{ padding: '40px 28px' }}>
          <EmptyState
            title="Metrics unavailable"
            body="Evaluation results have not been provided by the model pipeline yet. Run evaluation on the test set to populate this page."
          />
        </div>
      )}

      {!!data && (
        <div className="animate-fade-in">

          {/* ── Overall metrics strip ─── */}
          <div style={{ borderBottom: '1px solid var(--border)' }}>
            <SectionLabel>Overall Performance</SectionLabel>
            <OverallStrip overall={data.overall} />
          </div>

          {/* ── Radar + Per-class side by side ─── */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              borderBottom: '1px solid var(--border)',
            }}
          >
            <div style={{ borderRight: '1px solid var(--border)' }}>
              <SectionLabel>Performance Profile</SectionLabel>
              <div style={{ padding: '16px 24px 24px' }}>
                <PerformanceRadar overall={data.overall} />
              </div>
            </div>
            <div>
              <SectionLabel>Per-Class Breakdown</SectionLabel>
              <div style={{ padding: '0 0 24px' }}>
                <PerClassTable perClass={data.per_class} />
              </div>
            </div>
          </div>

          {/* ── Confusion matrix full-width ─── */}
          <div style={{ borderBottom: '1px solid var(--border)' }}>
            <SectionLabel
              right="Rows = actual class · Columns = predicted class"
            >
              Confusion Matrix
            </SectionLabel>
            <div style={{ padding: '24px 28px 40px' }}>
              {data.confusion_matrix ? (
                <ConfusionMatrix
                  matrix={data.confusion_matrix.matrix}
                  labels={data.confusion_matrix.labels}
                />
              ) : (
                <EmptyState
                  title="Confusion matrix unavailable"
                  body="Not provided by the evaluation pipeline."
                />
              )}
            </div>
          </div>

        </div>
      )}
    </main>
  );
}
