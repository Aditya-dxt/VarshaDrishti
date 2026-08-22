/**
 * Historical.jsx — Historical Replay page
 *
 * Master-detail layout:
 * ┌──────────────────┬─────────────────────────────────────┐
 * │ EVENT LIST       │ EVENT DETAIL                        │
 * │                  │                                     │
 * │ ● Dev Event      │   Risk / Map / Evidence / Explain   │
 * │   17 Aug 2026    │                                     │
 * │   18 Aug 2026    │   or: empty state                   │
 * └──────────────────┴─────────────────────────────────────┘
 *
 * Clicking an event highlights it and triggers replay automatically.
 * Geographic coordinates are unavailable in the source dataset.
 */
import { useState } from 'react';
import { Play, MapPin, Calendar, Activity } from 'lucide-react';
import { useHistoricalList, useHistoricalEvent } from '../hooks/useHistorical.js';
import { getRiskMeta, formatTimestamp } from '../utils/riskHelpers.js';

import PageHeader       from '../components/PageHeader.jsx';
import RiskCard         from '../components/RiskCard.jsx';
import ProbabilityChart from '../components/ProbabilityChart.jsx';
import GradCAMViewer    from '../components/GradCAMViewer.jsx';
import SHAPChart        from '../components/SHAPChart.jsx';
import RiskMap          from '../components/RiskMap.jsx';
import LoadingState     from '../components/LoadingState.jsx';
import ErrorState       from '../components/ErrorState.jsx';
import EmptyState       from '../components/EmptyState.jsx';

/* ── Event row in sidebar list ──────────────────────────────── */
function EventRow({ event, selected, onSelect }) {
  const meta = getRiskMeta(event.type);
  const badgeClass =
    event.type === 'no_rain'
      ? 'risk-badge-none'
      : event.type === 'high_impact'
        ? 'risk-badge-impact'
        : `risk-badge-${event.type}`;

  return (
    <button
      onClick={() => onSelect(event)}
      aria-pressed={selected}
      style={{
        display: 'block',
        width: '100%',
        textAlign: 'left',
        padding: '14px 16px',
        background: selected ? 'var(--nav-active-bg)' : 'transparent',
        boxShadow: selected ? `inset 2px 0 0 ${meta.dotColor}` : 'none',
        border: 'none',
        borderBottom: '1px solid var(--border)',
        cursor: 'pointer',
        transition: 'background 0.15s, border-color 0.15s',
      }}
    >
      {/* Name + badge */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          gap: '8px',
          marginBottom: '6px',
        }}
      >
        <span
          style={{
            fontSize: '13px',
            fontWeight: selected ? 600 : 500,
            color: selected ? 'var(--text-primary)' : 'var(--text-secondary)',
            lineHeight: 1.3,
            transition: 'color 0.15s',
          }}
        >
          {event.name}
        </span>
        <span
          className={badgeClass}
          style={{
            fontSize: '9px',
            padding: '2px 7px',
            letterSpacing: '0.05em',
            whiteSpace: 'nowrap',
            flexShrink: 0,
            fontWeight: 600,
            textTransform: 'uppercase',
          }}
        >
          {meta.shortLabel}
        </span>
      </div>

      {/* Date + location */}
      <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
        <span
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            fontSize: '11px',
            color: 'var(--text-muted)',
          }}
        >
          <Calendar size={10} />
          {event.date}
        </span>
        {event.location ? (
          <span
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              fontSize: '11px',
              color: 'var(--text-muted)',
            }}
          >
            <MapPin size={10} />
            {event.location}
          </span>
        ) : (
          <span
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              fontSize: '11px',
              color: 'var(--text-muted)',
            }}
          >
            <MapPin size={10} />
            Coordinates unavailable
          </span>
        )}
      </div>

      {/* Description preview */}
      {event.description && (
        <p
          style={{
            fontSize: '11px',
            color: selected ? 'var(--text-secondary)' : 'var(--text-muted)',
            marginTop: '6px',
            marginBottom: 0,
            lineHeight: 1.5,
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
          }}
        >
          {event.description}
        </p>
      )}
    </button>
  );
}

/* ── Event detail panel ────────────────────────────────────── */
function DetailPanel({ event, result, loading, error, onReplay, replayLoading }) {
  /* Nothing selected */
  if (!event) {
    return (
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100%',
          minHeight: '60vh',
          padding: '40px 24px',
          textAlign: 'center',
        }}
      >
        <Activity
          size={32}
          style={{ color: 'var(--text-dim)', marginBottom: '16px' }}
        />
        <p
          style={{
            fontSize: '14px',
            fontWeight: 500,
            color: 'var(--text-secondary)',
            margin: '0 0 8px',
          }}
        >
          Select an event
        </p>
        <p
          style={{
            fontSize: '12px',
            color: 'var(--text-muted)',
            maxWidth: 300,
            lineHeight: 1.6,
            margin: 0,
          }}
        >
          Choose a historical event from the list to inspect its prediction and explanation.
        </p>
      </div>
    );
  }

  /* Loading replay */
  if (loading) {
    return (
      <div style={{ padding: '40px 28px' }}>
        <LoadingState label="Running model prediction on historical observation…" lines={7} />
      </div>
    );
  }

  /* Replay error */
  if (error) {
    return (
      <div style={{ padding: '28px' }}>
        <ErrorState message={error} onRetry={() => onReplay(event.id)} />
      </div>
    );
  }

  /* Event selected, no replay yet */
  if (!result) {
    const meta = getRiskMeta(event.type);
    return (
      <div className="animate-fade-in">
        {/* Event overview */}
        <div
          style={{
            padding: '24px 28px',
            borderBottom: '1px solid var(--border)',
            boxShadow: `inset 2px 0 0 ${meta.dotColor}`,
          }}
        >
          <div style={{ marginBottom: '12px' }}>
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                fontSize: '11px',
                color: 'var(--text-muted)',
                marginBottom: '8px',
              }}
            >
              <Calendar size={11} /> {event.date}
              &nbsp;&nbsp;<MapPin size={11} /> {event.location || 'Coordinates unavailable'}
            </span>
            <h2
              style={{
                fontSize: '22px',
                fontWeight: 700,
                color: 'var(--text-primary)',
                margin: 0,
                letterSpacing: '-0.01em',
              }}
            >
              {event.name}
            </h2>
          </div>
          {event.description && (
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', margin: '0 0 20px', lineHeight: 1.6 }}>
              {event.description}
            </p>
          )}
          <button
            onClick={() => onReplay(event.id)}
            disabled={replayLoading}
            className="btn btn-primary"
          >
            {replayLoading ? (
              <span
                className="animate-spin-slow"
                style={{
                  display: 'inline-block',
                  width: 12,
                  height: 12,
                  borderRadius: '50%',
                  border: '1px solid var(--text-muted)',
                  borderTopColor: 'var(--accent)',
                }}
              />
            ) : (
              <Play size={11} />
            )}
            {replayLoading ? 'Running…' : 'Replay This Event'}
          </button>
        </div>

        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '40vh',
            padding: '40px 28px',
          }}
        >
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', textAlign: 'center' }}>
            Press "Replay This Event" to run the full prediction and explanation pipeline.
          </p>
        </div>
      </div>
    );
  }

  /* ── Full replay result ── */
  const { prediction, probabilities, xai, metadata } = result;

  const SectionLabel = ({ children }) => (
    <div
      style={{
        padding: '11px 28px',
        borderBottom: '1px solid var(--border)',
      }}
    >
      <span className="label">{children}</span>
    </div>
  );

  return (
    <div className="animate-fade-in">

      {/* Risk */}
      <div style={{ borderBottom: '1px solid var(--border)' }}>
        <SectionLabel>Prediction Result</SectionLabel>
        <RiskCard prediction={prediction} metadata={metadata} compact />
      </div>

      {/* Map */}
      <div style={{ borderBottom: '1px solid var(--border)' }}>
        <SectionLabel>Impact Location</SectionLabel>
        <RiskMap metadata={metadata} prediction={prediction} height={260} />
      </div>

      {/* Probability + SHAP side-by-side */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          borderBottom: '1px solid var(--border)',
        }}
      >
        <div style={{ borderRight: '1px solid var(--border)' }}>
          <SectionLabel>Probability Distribution</SectionLabel>
          <div style={{ padding: '20px 28px 24px' }}>
            <ProbabilityChart probabilities={probabilities} />
          </div>
        </div>
        <div>
          <SectionLabel>Feature Contributions</SectionLabel>
          <div style={{ padding: '16px 28px 24px' }}>
            <SHAPChart shap={xai?.shap} loading={false} />
          </div>
        </div>
      </div>

      {/* Grad-CAM */}
      <div>
        <SectionLabel>Model Attention — Grad-CAM</SectionLabel>
        <div style={{ padding: '0 28px 28px' }}>
          <GradCAMViewer gradcam={xai?.gradcam} loading={false} />
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

  const handleSelect = (event) => {
    setSelected(event);
    // Auto-replay on selection for immediate feedback
    replay(event.id);
  };

  const handleReplay = (id) => {
    replay(id);
  };

  const eventCount = listData?.events?.length;

  return (
    <main
      className="animate-fade-in"
      style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}
    >
      {/* Page header */}
      <PageHeader
        page="Historical Events"
        sub={
          eventCount != null
            ? `${eventCount} development dataset event${eventCount !== 1 ? 's' : ''} — Geographic coordinates unavailable in source dataset`
            : 'Development dataset events — prediction replay'
        }
      />

      {/* Master-detail body */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>

        {/* ── Event list sidebar ── */}
        <aside
          style={{
            width: '280px',
            flexShrink: 0,
            borderRight: '1px solid var(--border)',
            display: 'flex',
            flexDirection: 'column',
            overflowY: 'auto',
          }}
        >
          <div
            style={{
              padding: '11px 16px',
              borderBottom: '1px solid var(--border)',
              background: 'var(--bg-surface)',
              position: 'sticky',
              top: 0,
              zIndex: 5,
            }}
          >
            <span className="label">Available Events</span>
          </div>

          {listLoading && (
            <div style={{ padding: '20px 16px' }}>
              <LoadingState label="Loading events…" lines={4} />
            </div>
          )}
          {listError && (
            <div style={{ padding: '20px 16px' }}>
              <ErrorState message={listError} />
            </div>
          )}
          {!listLoading && !listError && !listData?.events?.length && (
            <EmptyState
              title="No events available"
              body="Historical events have not been provided by the backend."
            />
          )}

          {listData?.events?.map((event) => (
            <EventRow
              key={event.id}
              event={event}
              selected={selected?.id === event.id}
              onSelect={handleSelect}
            />
          ))}
        </aside>

        {/* ── Detail panel ── */}
        <div
          style={{
            flex: 1,
            minWidth: 0,
            overflowY: 'auto',
          }}
        >
          <DetailPanel
            event={selected}
            result={result}
            loading={replayLoading}
            error={replayError}
            onReplay={handleReplay}
            replayLoading={replayLoading}
          />
        </div>
      </div>
    </main>
  );
}
