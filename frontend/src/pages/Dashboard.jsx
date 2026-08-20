/**
 * Dashboard.jsx — Scientific monitoring console.
 *
 * Layout at 1280px+:
 * ┌─────────────────────────────────────────────────────────────────┐
 * │ [meta bar: last observation · IST clock · refresh]              │
 * ├───────────────────────────────┬─────────────────────────────────┤
 * │ LEFT COLUMN                   │ RIGHT COLUMN (geographic center) │
 * │  ① Risk label + confidence    │  Section: Impact Location        │
 * │  ─────────────────────────── │    Map — dominant (360px)        │
 * │  Section: Probability         │  ─────────────────────────────  │
 * │    Distribution bars          │  Section: Satellite Evidence     │
 * │  ─────────────────────────── │    EvidenceViewer tabs           │
 * │  Section: Feature             │                                  │
 * │    Contributions (SHAP)       │                                  │
 * └───────────────────────────────┴─────────────────────────────────┘
 *
 * Information flow: WHERE → WHAT → HOW CONFIDENT → WHY → EVIDENCE
 *
 * API + hook contracts: unchanged.
 */
import { useState, useEffect } from 'react';
import { RefreshCw } from 'lucide-react';
import { useLatestPrediction }  from '../hooks/useLatestPrediction.js';
import { getGradCAM }           from '../services/api.js';

import RiskCard         from '../components/RiskCard.jsx';
import ProbabilityChart from '../components/ProbabilityChart.jsx';
import EvidenceViewer   from '../components/EvidenceViewer.jsx';
import SHAPChart        from '../components/SHAPChart.jsx';
import RiskMap          from '../components/RiskMap.jsx';
import DataStatus       from '../components/DataStatus.jsx';
import LoadingState     from '../components/LoadingState.jsx';
import ErrorState       from '../components/ErrorState.jsx';

/* ── Consistent section head ────────────────────────────────
   Renders an uppercase overline label with optional right slot.
   Uses .section-head CSS class for padding + border-bottom. */
function SectionHead({ label, right, flush = false }) {
  return (
    <div className={flush ? 'section-head section-head--flush' : 'section-head'}>
      <span className="label">{label}</span>
      {right && (
        <span style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
          {right}
        </span>
      )}
    </div>
  );
}

/* ── Empty / no prediction yet ─────────────────────────────── */
function NoDataState({ onAnalyze, loading }) {
  return (
    <div
      className="animate-fade-in"
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '65vh',
        textAlign: 'center',
        padding: '40px 32px',
      }}
    >
      <p className="label" style={{ marginBottom: 16 }}>BHOOMIDRISHTI</p>
      <h1
        style={{
          fontSize: '22px',
          fontWeight: 600,
          color: 'var(--text-primary)',
          marginBottom: 10,
          letterSpacing: '-0.01em',
        }}
      >
        No prediction available
      </h1>
      <p
        style={{
          color: 'var(--text-secondary)',
          fontSize: '14px',
          maxWidth: 380,
          lineHeight: 1.7,
          marginBottom: 32,
        }}
      >
        The latest INSAT-3DR satellite observation has not been processed yet.
        Trigger an analysis to view the current rainfall risk assessment.
      </p>
      <button
        onClick={onAnalyze}
        disabled={loading}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          padding: '10px 24px',
          background: 'var(--bg-raised)',
          border: '1px solid var(--border-mid)',
          color: 'var(--text-primary)',
          fontSize: '11px',
          fontWeight: 600,
          letterSpacing: '0.08em',
          textTransform: 'uppercase',
          cursor: loading ? 'not-allowed' : 'pointer',
          opacity: loading ? 0.5 : 1,
          transition: 'border-color 0.15s',
        }}
      >
        {loading ? (
          <span
            className="animate-spin-slow"
            style={{
              display: 'inline-block',
              width: 13,
              height: 13,
              borderRadius: '50%',
              border: '1px solid var(--text-muted)',
              borderTopColor: 'var(--text-primary)',
            }}
          />
        ) : (
          <RefreshCw size={13} />
        )}
        {loading ? 'Analysing…' : 'Analyse Latest Observation'}
      </button>
    </div>
  );
}

/* ── Main dashboard ─────────────────────────────────────────── */
export default function Dashboard() {
  const { data, loading, error, refetch } = useLatestPrediction();

  const [gradcamData, setGradcamData] = useState(null);
  const [gcLoading,   setGcLoading]   = useState(true);

  useEffect(() => {
    getGradCAM()
      .then(setGradcamData)
      .catch(() => setGradcamData({ available: false }))
      .finally(() => setGcLoading(false));
  }, []);

  /* ── Loading ── */
  if (loading && !data) {
    return (
      <div style={{ maxWidth: 1400, margin: '0 auto', padding: '40px 28px' }}>
        <LoadingState label="Loading latest satellite prediction…" lines={6} />
      </div>
    );
  }

  /* ── Error ── */
  if (error) {
    return (
      <div style={{
        maxWidth: 1400, margin: '0 auto', padding: '40px 28px',
        display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh',
      }}>
        <ErrorState message={error} onRetry={refetch} />
      </div>
    );
  }

  /* ── No data ── */
  if (!data) {
    return (
      <div style={{ maxWidth: 1400, margin: '0 auto' }}>
        <NoDataState onAnalyze={refetch} loading={loading} />
      </div>
    );
  }

  const { prediction, probabilities, xai, metadata, system } = data;

  /* Evidence viewer: prefer standalone gradcam fetch; fall back to xai.gradcam */
  const evidenceData = gradcamData || xai?.gradcam;

  return (
    <main
      className="animate-fade-in"
      style={{ maxWidth: 1400, margin: '0 auto' }}
    >
      {/* ── Meta bar ──────────────────────────────────────────── */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '9px 28px',
          borderBottom: '1px solid var(--border)',
          gap: 16,
        }}
      >
        <DataStatus system={system} />

        <button
          onClick={refetch}
          disabled={loading}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 5,
            padding: '4px 10px',
            background: 'transparent',
            border: '1px solid var(--border)',
            color: 'var(--text-muted)',
            fontSize: '10px',
            fontWeight: 600,
            letterSpacing: '0.08em',
            textTransform: 'uppercase',
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.5 : 1,
            transition: 'border-color 0.15s, color 0.15s',
          }}
          aria-label="Refresh prediction"
        >
          <RefreshCw
            size={10}
            style={{ animation: loading ? 'spin 1.2s linear infinite' : 'none' }}
          />
          Refresh
        </button>
      </div>

      {/* ── Two-column layout ────────────────────────────────── */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'minmax(0,1fr) minmax(0,1.5fr)',
          borderBottom: '1px solid var(--border)',
        }}
      >
        {/* ══ LEFT COLUMN — Analysis ═══════════════════════════ */}
        <div
          style={{
            borderRight: '1px solid var(--border)',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          {/* ① Risk (WHAT + HOW CONFIDENT + provenance) */}
          <RiskCard prediction={prediction} metadata={metadata} />

          {/* ② Probability distribution */}
          <div style={{ borderTop: '1px solid var(--border)' }}>
            <SectionHead label="Probability Distribution" />
            <div style={{ padding: '4px 28px 20px' }}>
              <ProbabilityChart probabilities={probabilities} />
            </div>
          </div>

          {/* ③ Feature contributions — WHY */}
          <div style={{ borderTop: '1px solid var(--border)', flex: 1 }}>
            <SectionHead label="Feature Contributions" />
            <div style={{ padding: '4px 28px 24px' }}>
              <SHAPChart shap={xai?.shap} loading={false} />
            </div>
          </div>
        </div>

        {/* ══ RIGHT COLUMN — Geographic Evidence ═══════════════ */}
        <div style={{ display: 'flex', flexDirection: 'column' }}>

          {/* Map — dominant (WHERE) */}
          <div>
            <SectionHead
              label="Impact Location"
              right={metadata?.location}
              flush
            />
            {/* 360px height for genuine map dominance */}
            <RiskMap metadata={metadata} prediction={prediction} height={360} zoom={6} />
          </div>

          {/* Divider */}
          <div style={{ borderTop: '1px solid var(--border)' }} />

          {/* EvidenceViewer — Satellite / Grad-CAM / Overlay (EVIDENCE) */}
          <div style={{ flex: 1 }}>
            <EvidenceViewer
              gradcam={evidenceData}
              metadata={{
                timestamp:     metadata?.timestamp,
                channel_label: metadata?.source,
              }}
              loading={gcLoading}
            />
          </div>

        </div>
      </div>
    </main>
  );
}
