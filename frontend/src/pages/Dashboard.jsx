/**
 * Dashboard.jsx — Overview page
 *
 * Information hierarchy follows: WHERE → WHAT → HOW CONFIDENT → WHY → EVIDENCE
 *
 * Layout (single scrolling column, full content width):
 * ┌──────────────────────────────────────────────────────┐
 * │ PAGE HEADER                                          │
 * ├──────────────────────────────────────────────────────┤
 * │ MAP (full width, 400px)           ← WHERE            │
 * ├─────────────────────┬────────────────────────────────┤
 * │ RISK SUMMARY        │ PROBABILITY DISTRIBUTION       │
 * │ (WHAT + CONFIDENT)  │                                │
 * ├─────────────────────┴────────────────────────────────┤
 * │ FEATURE CONTRIBUTIONS                 ← WHY          │
 * ├──────────────────────────────────────────────────────┤
 * │ MODEL EVIDENCE (satellite tabs)       ← EVIDENCE     │
 * └──────────────────────────────────────────────────────┘
 *
 * API + hook contracts: unchanged.
 */
import { RefreshCw } from 'lucide-react';
import { useLatestPrediction }  from '../hooks/useLatestPrediction.js';

import PageHeader       from '../components/PageHeader.jsx';
import RiskCard         from '../components/RiskCard.jsx';
import ProbabilityChart from '../components/ProbabilityChart.jsx';
import EvidenceViewer   from '../components/EvidenceViewer.jsx';
import SHAPChart        from '../components/SHAPChart.jsx';
import RiskMap          from '../components/RiskMap.jsx';
import DataStatus       from '../components/DataStatus.jsx';
import LoadingState     from '../components/LoadingState.jsx';
import ErrorState       from '../components/ErrorState.jsx';

/* ── Section wrapper ─────────────────────────────────────────
   Thin label header + content area. Used throughout page. */
function Section({ label, right, children, noPadding = false }) {
  return (
    <div style={{ borderBottom: '1px solid var(--border)' }}>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '11px 28px',
          borderBottom: '1px solid var(--border)',
        }}
      >
        <span className="label">{label}</span>
        {right && (
          <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{right}</span>
        )}
      </div>
      {noPadding ? children : (
        <div style={{ padding: '0 28px 24px' }}>{children}</div>
      )}
    </div>
  );
}

/* ── No data / empty state ────────────────────────────────── */
function NoDataState({ onAnalyze, loading }) {
  return (
    <div
      className="animate-fade-in"
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '70vh',
        textAlign: 'center',
        padding: '40px 32px',
      }}
    >
      <p
        className="label"
        style={{ marginBottom: '16px', letterSpacing: '0.14em' }}
      >
        BHOOMIDRISHTI
      </p>
      <h1
        style={{
          fontSize: '20px',
          fontWeight: 600,
          color: 'var(--text-primary)',
          marginBottom: '10px',
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
          marginBottom: '32px',
        }}
      >
        The latest INSAT-3DR satellite observation has not been processed yet.
        Trigger an analysis to view the current rainfall risk assessment.
      </p>
      <button
        onClick={onAnalyze}
        disabled={loading}
        className="btn btn-primary"
      >
        {loading ? (
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
          <RefreshCw size={12} />
        )}
        {loading ? 'Analysing…' : 'Analyse Latest Observation'}
      </button>
    </div>
  );
}

/* ── Main dashboard ─────────────────────────────────────────── */
export default function Dashboard() {
  const { data, loading, error, refetch } = useLatestPrediction();

  /* ── Loading ── */
  if (loading && !data) {
    return (
      <div>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '14px 28px',
            borderBottom: '1px solid var(--border)',
            background: 'var(--bg-surface)',
          }}
        >
          <span className="label" style={{ letterSpacing: '0.14em' }}>BHOOMIDRISHTI / OVERVIEW</span>
        </div>
        <div style={{ padding: '40px 28px' }}>
          <LoadingState label="Loading latest satellite prediction…" lines={6} />
        </div>
      </div>
    );
  }

  /* ── Error ── */
  if (error) {
    return (
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '60vh',
          padding: '40px 28px',
        }}
      >
        <ErrorState message={error} onRetry={refetch} />
      </div>
    );
  }

  /* ── No data ── */
  if (!data) {
    return <NoDataState onAnalyze={refetch} loading={loading} />;
  }

  const { prediction, probabilities, xai, metadata, system } = data;

  /* ── Refresh button (used in page header) ── */
  const RefreshBtn = (
    <button
      onClick={refetch}
      disabled={loading}
      className="btn"
      aria-label="Refresh prediction"
    >
      <RefreshCw
        size={11}
        style={{ animation: loading ? 'spin 1.2s linear infinite' : 'none' }}
      />
      Refresh
    </button>
  );

  return (
    <main className="animate-fade-in">

      {/* ── Page header ──────────────────────────────────────── */}
      <PageHeader
        page="Overview"
        sub={<DataStatus system={system} />}
        right={RefreshBtn}
      />

      {/* ── 1. MAP — WHERE ──────────────────────────────────── */}
      <Section
        label="Impact Location"
        right={metadata?.location}
        noPadding
      >
        <RiskMap
          metadata={metadata}
          prediction={prediction}
          height={400}
          zoom={6}
        />
      </Section>

      {/* ── 2. Risk summary + Probability side by side ───────── */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)',
          borderBottom: '1px solid var(--border)',
        }}
      >
        {/* WHAT + HOW CONFIDENT */}
        <div
          style={{
            borderRight: '1px solid var(--border)',
          }}
        >
          <div
            style={{
              padding: '11px 28px',
              borderBottom: '1px solid var(--border)',
            }}
          >
            <span className="label">Current Risk</span>
          </div>
          <RiskCard prediction={prediction} metadata={metadata} />
        </div>

        {/* PROBABILITY DISTRIBUTION */}
        <div>
          <div
            style={{
              padding: '11px 28px',
              borderBottom: '1px solid var(--border)',
            }}
          >
            <span className="label">Probability Distribution</span>
          </div>
          <div style={{ padding: '20px 28px 24px' }}>
            <ProbabilityChart probabilities={probabilities} />
          </div>
        </div>
      </div>

      {/* ── 3. FEATURE CONTRIBUTIONS — WHY ──────────────────── */}
      <Section label="Why This Prediction?">
        <div style={{ paddingTop: '16px' }}>
          <SHAPChart shap={xai?.shap} loading={false} />
        </div>
      </Section>

      {/* ── 4. MODEL EVIDENCE — SATELLITE + GRAD-CAM ────────── */}
      <div style={{ borderBottom: '1px solid var(--border)' }}>
        <div
          style={{
            padding: '11px 28px',
            borderBottom: '1px solid var(--border)',
          }}
        >
          <span className="label">Model Evidence</span>
        </div>
        <EvidenceViewer
          gradcam={xai?.gradcam}
          metadata={{
            timestamp:     metadata?.timestamp,
            channel_label: metadata?.source,
          }}
          loading={false}
        />
      </div>

    </main>
  );
}
