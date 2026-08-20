/**
 * EvidenceViewer.jsx — Light theme
 * Unified satellite evidence panel with tabs: Satellite | Grad-CAM | Overlay
 * Clean white surface, dark tab labels, blue active state.
 */
import { useState } from 'react';
import LoadingState from './LoadingState.jsx';
import EmptyState from './EmptyState.jsx';

const MODES = [
  {
    id:    'original',
    label: 'Raw Satellite',
    key:   'original_url',
    desc:  'Original INSAT-3DR observation as ingested by the 3D-CNN — no post-processing.',
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
    desc:  'Grad-CAM attention superimposed on original satellite observation (α = 0.55).',
    note:  'Warmer colour = stronger model attention.',
    showScale: true,
  },
];

/* ── Thermal scale legend ───────────────────────────────────── */
function GradCAMScale() {
  return (
    <div
      style={{
        padding: '6px 16px',
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        flexDirection: 'column',
        gap: '4px',
        background: 'var(--bg-raised)',
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          marginBottom: '3px',
        }}
      >
        <span style={{ fontSize: '9px', color: 'var(--text-muted)', letterSpacing: '0.06em', textTransform: 'uppercase', fontWeight: 600 }}>
          Low attention
        </span>
        <span style={{ fontSize: '9px', color: 'var(--text-muted)', letterSpacing: '0.06em', textTransform: 'uppercase', fontWeight: 600 }}>
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
      <div style={{ padding: '32px 28px' }}>
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
          paddingLeft: '8px',
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
          background: '#1a2332',  /* dark panel for satellite imagery — intentional contrast */
          lineHeight: 0,
          minHeight: '260px',
        }}
      >
        {imgUrl && !imgError ? (
          <img
            key={mode}
            src={imgUrl}
            alt={currentMode.desc}
            style={{
              width: '100%',
              maxHeight: 400,
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
              height: 260,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#94A3B8',
              fontSize: '12px',
              letterSpacing: '0.04em',
            }}
          >
            {imgError ? 'Image could not be loaded' : 'No image available'}
          </div>
        )}

        {/* ── Metadata overlay on the image ─────────────────── */}
        <div
          style={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            padding: '6px 12px',
            background: 'rgba(15,23,42,0.75)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            lineHeight: 1,
          }}
        >
          <span
            className="mono"
            style={{ fontSize: '10px', color: 'rgba(255,255,255,0.55)', letterSpacing: '0.06em' }}
          >
            {metadata?.channel_label || 'INSAT-3DR'}
          </span>
          {metadata?.timestamp && (
            <span
              className="mono"
              style={{ fontSize: '10px', color: 'rgba(255,255,255,0.40)', letterSpacing: '0.04em' }}
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
          background: 'var(--bg-raised)',
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
