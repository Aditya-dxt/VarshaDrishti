/**
 * EvidenceViewer.jsx
 * Unified satellite evidence panel: Satellite | Grad-CAM | Overlay
 * Single tabbed viewer. Tabs use bottom-border active state.
 * Section header above tabs. Smooth opacity transition between views.
 *
 * Props:
 *   gradcam     — gradcam data object from API
 *   metadata    — prediction metadata (timestamp, channel_label)
 *   loading     — boolean
 *
 * Contract:
 *   gradcam.original_url — satellite image
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
    desc:  'Class activation map (Grad-CAM). Spatial regions weighted by gradient contribution to final classification.',
    note:  'Warmer colour = stronger model attention.',
    showScale: true,
  },
  {
    id:    'overlay',
    label: 'Overlay',
    key:   'overlay_url',
    desc:  'Grad-CAM attention superimposed on the original satellite observation (α = 0.55).',
    note:  'Warmer colour = stronger model attention.',
    showScale: true,
  },
];

/* ── Thermal scale legend ───────────────────────────────────── */
function GradCAMScale() {
  return (
    <div
      style={{
        padding: '7px 16px',
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        flexDirection: 'column',
        gap: '4px',
        background: 'var(--bg-surface)',
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          marginBottom: '3px',
        }}
      >
        <span style={{ fontSize: '9px', color: 'var(--text-dim)', letterSpacing: '0.06em', textTransform: 'uppercase' }}>
          Low attention
        </span>
        <span style={{ fontSize: '9px', color: 'var(--text-dim)', letterSpacing: '0.06em', textTransform: 'uppercase' }}>
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
  const [imgVisible, setImgVisible] = useState(true);

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

  const handleTabChange = (id) => {
    setImgVisible(false);
    setImgError(false);
    setTimeout(() => {
      setMode(id);
      setImgVisible(true);
    }, 80);
  };

  return (
    <div className="animate-fade-in">
      {/* ── Tab bar ─────────────────────────────────────────── */}
      <div
        role="tablist"
        aria-label="Evidence display mode"
        style={{
          display: 'flex',
          background: 'var(--bg-surface)',
          borderBottom: '1px solid var(--border)',
          paddingLeft: '4px',
        }}
      >
        {MODES.map(({ id, label }) => (
          <button
            key={id}
            role="tab"
            aria-selected={mode === id}
            onClick={() => handleTabChange(id)}
            className={`ev-tab ${mode === id ? 'active' : ''}`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* ── Grad-CAM color scale ─────────────────────────────── */}
      {currentMode.showScale && <GradCAMScale />}

      {/* ── Image panel ─────────────────────────────────────── */}
      <div
        role="tabpanel"
        style={{
          position: 'relative',
          background: '#030810',
          lineHeight: 0,
          minHeight: '280px',
        }}
      >
        {imgUrl && !imgError ? (
          <img
            key={mode}
            src={imgUrl}
            alt={currentMode.desc}
            style={{
              width: '100%',
              maxHeight: 420,
              minHeight: '220px',
              objectFit: 'contain',
              display: 'block',
              opacity: imgVisible ? 1 : 0,
              transition: 'opacity 0.15s ease',
            }}
            onError={() => setImgError(true)}
            onLoad={() => setImgVisible(true)}
          />
        ) : (
          <div
            style={{
              height: 280,
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

        {/* ── Image metadata overlay ─────────────────────────── */}
        <div
          style={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            padding: '6px 12px',
            background: 'rgba(3,8,16,0.82)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            lineHeight: 1,
          }}
        >
          <span
            className="mono"
            style={{ fontSize: '10px', color: 'rgba(255,255,255,0.38)', letterSpacing: '0.06em' }}
          >
            {metadata?.channel_label || 'INSAT-3DR'}
          </span>
          {metadata?.timestamp && (
            <span
              className="mono"
              style={{ fontSize: '10px', color: 'rgba(255,255,255,0.26)', letterSpacing: '0.04em' }}
            >
              {new Date(metadata.timestamp).toISOString().replace('T', ' ').slice(0, 16)} UTC
            </span>
          )}
        </div>
      </div>

      {/* ── Caption ─────────────────────────────────────────── */}
      <div
        style={{
          borderTop: '1px solid var(--border)',
          padding: '9px 16px',
          display: 'flex',
          flexDirection: 'column',
          gap: '3px',
          background: 'var(--bg-surface)',
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
