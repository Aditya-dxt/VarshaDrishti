/**
 * EvidenceViewer.jsx
 * Unified visual evidence centerpiece: Satellite | Heatmap | Overlay
 * Consolidates satellite imagery and Grad-CAM into a single tabbed
 * image panel that dominates the right column of the Dashboard.
 *
 * Props:
 *   gradcam     — gradcam data object from API
 *   metadata    — prediction metadata (timestamp, location, channel_label)
 *   loading     — boolean
 *
 * Contract:
 *   gradcam.original_url — satellite image (same source as SatelliteViewer)
 *   gradcam.heatmap_url  — Grad-CAM heatmap
 *   gradcam.overlay_url  — heatmap overlaid on satellite
 *   gradcam.available    — boolean
 */
import { useState } from 'react';
import LoadingState from './LoadingState.jsx';
import EmptyState from './EmptyState.jsx';

const MODES = [
  {
    id:    'original',
    label: 'Satellite',
    key:   'original_url',
    desc:  'Original INSAT-3DR observation. Displayed as ingested by the 3D-CNN — no post-processing.',
    note:  null,
    showScale: false,
  },
  {
    id:    'heatmap',
    label: 'Grad-CAM',
    key:   'heatmap_url',
    desc:  'Class activation map (Grad-CAM). Spatial regions weighted by their gradient contribution to the final classification.',
    note:  'Warmer colour indicates stronger model attention.',
    showScale: true,
  },
  {
    id:    'overlay',
    label: 'Overlay',
    key:   'overlay_url',
    desc:  'Grad-CAM attention superimposed on the original satellite observation. α = 0.55.',
    note:  'Warmer colour indicates stronger model attention.',
    showScale: true,
  },
];

/* ── Thermal scale legend — rendered only for heatmap/overlay ── */
function GradCAMScale() {
  return (
    <div
      style={{
        padding: '8px 12px 7px',
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        flexDirection: 'column',
        gap: 4,
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          marginBottom: 3,
        }}
      >
        <span style={{ fontSize: '9px', color: 'var(--text-muted)', letterSpacing: '0.06em', textTransform: 'uppercase' }}>
          Low attention
        </span>
        <span style={{ fontSize: '9px', color: 'var(--text-muted)', letterSpacing: '0.06em', textTransform: 'uppercase' }}>
          High attention
        </span>
      </div>
      <div className="gradcam-scale" />
    </div>
  );
}

export default function EvidenceViewer({ gradcam, metadata, loading }) {
  const [mode, setMode]         = useState('overlay');
  const [imgError, setImgError] = useState(false);

  if (loading) {
    return (
      <div style={{ padding: '32px 0' }}>
        <LoadingState label="Loading satellite evidence…" lines={5} />
      </div>
    );
  }

  if (!gradcam?.available) {
    return (
      <EmptyState
        title="Satellite evidence unavailable"
        body="Imagery and Grad-CAM have not been generated for this prediction."
      />
    );
  }

  const currentMode = MODES.find((m) => m.id === mode);
  const imgUrl = gradcam[currentMode.key];

  return (
    <div className="animate-fade-in">
      {/* ── Tab bar ─────────────────────────────────────────── */}
      <div
        role="tablist"
        aria-label="Evidence display mode"
        style={{
          display: 'flex',
          background: 'var(--bg-raised)',
          borderBottom: '1px solid var(--border)',
        }}
      >
        {MODES.map(({ id, label }) => (
          <button
            key={id}
            role="tab"
            aria-selected={mode === id}
            onClick={() => { setMode(id); setImgError(false); }}
            className={`ev-tab ${mode === id ? 'active' : ''}`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* ── Grad-CAM color scale (heatmap + overlay only) ──── */}
      {currentMode.showScale && <GradCAMScale />}

      {/* ── Image panel ─────────────────────────────────────── */}
      <div
        role="tabpanel"
        style={{
          position: 'relative',
          background: '#030810',
          lineHeight: 0,
        }}
      >
        {imgUrl && !imgError ? (
          <img
            key={mode}
            src={imgUrl}
            alt={currentMode.desc}
            style={{
              width: '100%',
              maxHeight: 480,
              minHeight: 200,
              objectFit: 'cover',
              display: 'block',
            }}
            onError={() => setImgError(true)}
          />
        ) : (
          <div
            style={{
              height: 320,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--text-muted)',
              fontSize: '12px',
              letterSpacing: '0.04em',
            }}
          >
            {imgError ? 'Image could not be loaded' : 'No image available'}
          </div>
        )}

        {/* ── Image metadata strip ─────────────────────────── */}
        <div
          style={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            padding: '5px 10px',
            background: 'rgba(3,8,16,0.85)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <span
            className="mono"
            style={{ fontSize: '10px', color: 'rgba(255,255,255,0.40)', letterSpacing: '0.06em' }}
          >
            {metadata?.channel_label || 'INSAT-3DR'}
          </span>
          {metadata?.timestamp && (
            <span
              className="mono"
              style={{ fontSize: '10px', color: 'rgba(255,255,255,0.28)', letterSpacing: '0.04em' }}
            >
              {new Date(metadata.timestamp).toISOString().replace('T', ' ').slice(0, 16)} UTC
            </span>
          )}
        </div>
      </div>

      {/* ── Caption + methodology note ───────────────────────── */}
      <div
        style={{
          borderTop: '1px solid var(--border)',
          padding: '8px 12px',
          display: 'flex',
          flexDirection: 'column',
          gap: 2,
        }}
      >
        <p
          style={{
            fontSize: '11px',
            color: 'var(--text-muted)',
            lineHeight: 1.55,
            margin: 0,
          }}
        >
          {currentMode.desc}
        </p>
        {currentMode.note && (
          <p
            style={{
              fontSize: '10px',
              color: 'var(--text-dim)',
              letterSpacing: '0.02em',
              margin: 0,
            }}
          >
            {currentMode.note}
          </p>
        )}
      </div>
    </div>
  );
}
