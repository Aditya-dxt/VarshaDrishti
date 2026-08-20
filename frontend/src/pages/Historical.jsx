/**
 * Historical.jsx — Redesigned as flat, editorial layout.
 * Sidebar: plain event list with dividers, not rounded cards.
 * Main panel: structured analysis results without card containers.
 */
import { useState } from 'react';
import { Play } from 'lucide-react';
import { useHistoricalList, useHistoricalEvent } from '../hooks/useHistorical.js';
import { getRiskMeta, formatTimestamp } from '../utils/riskHelpers.js';

import RiskCard         from '../components/RiskCard.jsx';
import ProbabilityChart from '../components/ProbabilityChart.jsx';
import GradCAMViewer    from '../components/GradCAMViewer.jsx';
import SHAPChart        from '../components/SHAPChart.jsx';
import RiskMap          from '../components/RiskMap.jsx';
import LoadingState     from '../components/LoadingState.jsx';
import ErrorState       from '../components/ErrorState.jsx';
import EmptyState       from '../components/EmptyState.jsx';

/* ── Event row in sidebar ─────────────────────────────────── */
function EventRow({ event, selected, onSelect }) {
  const meta = getRiskMeta(event.type);
  return (
    <button
      onClick={() => onSelect(event)}
      aria-pressed={selected}
      style={{
        display: 'block',
        width: '100%',
        textAlign: 'left',
        padding: '14px 20px',
        background: selected ? 'var(--bg-raised)' : 'transparent',
        borderLeft: `3px solid ${selected ? meta.dotColor : 'transparent'}`,
        border: 'none',
        borderBottom: '1px solid var(--border)',
        cursor: 'pointer',
        transition: 'background 0.12s',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 8, marginBottom: 4 }}>
        <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>
          {event.name}
        </span>
        <span className={`risk-badge-${event.type === 'no_rain' ? 'none' : event.type === 'high_impact' ? 'impact' : event.type}`}
          style={{ fontSize: '10px', padding: '2px 7px', letterSpacing: '0.04em', whiteSpace: 'nowrap' }}>
          {meta.shortLabel}
        </span>
      </div>
      <div style={{ display: 'flex', gap: 12 }}>
        <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{event.date}</span>
        <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{event.location?.split(',')[0]}</span>
      </div>
      {event.description && (
        <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: 5, lineHeight: 1.5, marginBottom: 0 }}>
          {event.description}
        </p>
      )}
    </button>
  );
}

/* ── Section label ─────────────────────────────────────────── */
function SLabel({ children }) {
  return (
    <p
      className="label"
      style={{
        padding: '14px 24px 10px',
        borderBottom: '1px solid var(--border)',
        margin: 0,
      }}
    >
      {children}
    </p>
  );
}

/* ── Replay results ───────────────────────────────────────── */
function ReplayPanel({ result, loading, error }) {
  if (loading) {
    return (
      <div style={{ padding: '40px 24px' }}>
        <LoadingState label="Running model prediction on historical observation…" lines={7} />
      </div>
    );
  }
  if (error) return <div style={{ padding: 24 }}><ErrorState message={error} /></div>;
  if (!result) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 400 }}>
        <EmptyState
          title="Select an event to begin"
          body="Choose a historical event from the panel on the left, then press Replay to run the model and view results."
        />
      </div>
    );
  }

  const { prediction, probabilities, xai, metadata } = result;

  return (
    <div className="animate-fade-in">
      {/* Risk */}
      <RiskCard prediction={prediction} metadata={metadata} />

      {/* Map + Evidence 2-col */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          borderTop: '1px solid var(--border)',
        }}
      >
        <div style={{ borderRight: '1px solid var(--border)' }}>
          <SLabel>Impact Location</SLabel>
          <RiskMap metadata={metadata} prediction={prediction} height={260} />
        </div>
        <div>
          <SLabel>Model Attention — Grad-CAM</SLabel>
          <div style={{ padding: '0 20px 20px' }}>
            <GradCAMViewer gradcam={xai?.gradcam} loading={false} />
          </div>
        </div>
      </div>

      {/* Probability + SHAP */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          borderTop: '1px solid var(--border)',
        }}
      >
        <div style={{ borderRight: '1px solid var(--border)', padding: '0 24px 24px' }}>
          <p className="label" style={{ padding: '14px 0 10px' }}>Probability Distribution</p>
          <ProbabilityChart probabilities={probabilities} />
        </div>
        <div style={{ padding: '0 24px 24px' }}>
          <p className="label" style={{ padding: '14px 0 10px' }}>Feature Contributions</p>
          <SHAPChart shap={xai?.shap} loading={false} />
        </div>
      </div>
    </div>
  );
}

/* ── Page ─────────────────────────────────────────────────── */
export default function Historical() {
  const { data: listData, loading: listLoading, error: listError } = useHistoricalList();
  const { data: result, loading: replayLoading, error: replayError, replay } = useHistoricalEvent();
  const [selected, setSelected] = useState(null);

  const handleReplay = () => { if (selected) replay(selected.id); };

  return (
    <main
      className="animate-fade-in"
      style={{ maxWidth: 1400, margin: '0 auto' }}
    >
      {/* Page heading */}
      <div style={{ padding: '20px 28px 16px', borderBottom: '1px solid var(--border)' }}>
        <h1 style={{ fontSize: '18px', fontWeight: 600, color: 'var(--text-primary)', margin: '0 0 4px', letterSpacing: '-0.01em' }}>
          Historical Replay
        </h1>
        <p style={{ fontSize: '13px', color: 'var(--text-secondary)', margin: 0 }}>
          Run the full prediction and explanation pipeline on documented extreme-rainfall events.
        </p>
      </div>

      <div style={{ display: 'flex', minHeight: '75vh' }}>
        {/* ── Sidebar ── */}
        <aside
          style={{
            width: 280,
            flexShrink: 0,
            borderRight: '1px solid var(--border)',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          <div style={{ padding: '12px 20px', borderBottom: '1px solid var(--border)' }}>
            <span className="label">Available Events</span>
          </div>

          <div style={{ flex: 1, overflowY: 'auto' }}>
            {listLoading && <div style={{ padding: 20 }}><LoadingState label="Loading events…" lines={4} /></div>}
            {listError   && <div style={{ padding: 20 }}><ErrorState message={listError} /></div>}
            {!listLoading && !listError && !listData?.events?.length && (
              <EmptyState title="No events available" body="Historical events have not been provided by the backend." />
            )}
            {listData?.events?.map((event) => (
              <EventRow
                key={event.id}
                event={event}
                selected={selected?.id === event.id}
                onSelect={setSelected}
              />
            ))}
          </div>

          {/* Replay CTA */}
          {selected && (
            <div style={{ padding: '16px 20px', borderTop: '1px solid var(--border)' }}>
              <button
                onClick={handleReplay}
                disabled={replayLoading}
                style={{
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 8,
                  padding: '10px 0',
                  background: 'var(--bg-raised)',
                  border: '1px solid var(--border-mid)',
                  color: 'var(--text-primary)',
                  fontSize: '12px',
                  fontWeight: 500,
                  letterSpacing: '0.06em',
                  cursor: replayLoading ? 'not-allowed' : 'pointer',
                  opacity: replayLoading ? 0.55 : 1,
                  transition: 'border-color 0.15s',
                }}
              >
                {replayLoading ? (
                  <span
                    className="animate-spin-slow"
                    style={{ display: 'inline-block', width: 13, height: 13, borderRadius: '50%', border: '1px solid var(--text-muted)', borderTopColor: 'var(--text-primary)' }}
                  />
                ) : <Play size={12} />}
                {replayLoading ? 'RUNNING…' : 'REPLAY EVENT'}
              </button>
            </div>
          )}
        </aside>

        {/* ── Main content ── */}
        <div style={{ flex: 1, minWidth: 0, overflowY: 'auto' }}>
          <ReplayPanel result={result} loading={replayLoading} error={replayError} />
        </div>
      </div>
    </main>
  );
}
