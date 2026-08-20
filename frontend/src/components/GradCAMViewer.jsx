/**
 * GradCAMViewer.jsx — Light theme
 * Historical page Grad-CAM viewer. Same three modes as EvidenceViewer.
 */
import { useState } from 'react';
import LoadingState from './LoadingState.jsx';
import EmptyState   from './EmptyState.jsx';

const MODES = [
  { id: 'original', label: 'Raw Satellite', key: 'original_url' },
  { id: 'heatmap',  label: 'Grad-CAM',      key: 'heatmap_url'  },
  { id: 'overlay',  label: 'Overlay',        key: 'overlay_url'  },
];

const CAPTIONS = {
  original: 'Original INSAT-3DR observation used as model input.',
  heatmap:  'Regions of highest model attention. Warmer colour = stronger influence.',
  overlay:  'Grad-CAM attention overlaid on the satellite image (α = 0.55).',
};

export default function GradCAMViewer({ gradcam, loading }) {
  const [mode, setMode]       = useState('overlay');
  const [imgError, setImgError] = useState(false);

  if (loading) return <LoadingState label="Generating explanation…" lines={4} />;

  if (!gradcam?.available) {
    return (
      <EmptyState
        title="Explanation unavailable"
        body="Grad-CAM visualisation has not been generated for this prediction."
      />
    );
  }

  const currentMode = MODES.find((m) => m.id === mode);
  const imgUrl = gradcam[currentMode.key];

  return (
    <div className="animate-fade-in">
      {/* Tabs */}
      <div
        role="tablist"
        aria-label="Evidence mode"
        style={{
          display: 'flex',
          borderBottom: '1px solid var(--border)',
          marginBottom: 0,
          background: 'var(--bg-surface)',
          paddingLeft: '4px',
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

      {/* Image panel — dark background for satellite imagery */}
      <div
        role="tabpanel"
        style={{ position: 'relative', background: '#1a2332', lineHeight: 0 }}
      >
        {imgUrl && !imgError ? (
          <img
            key={mode}
            src={imgUrl}
            alt={CAPTIONS[mode]}
            style={{ width: '100%', maxHeight: 300, objectFit: 'contain', display: 'block' }}
            onError={() => setImgError(true)}
          />
        ) : (
          <div
            style={{
              height: 220,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#94A3B8',
              fontSize: '12px',
            }}
          >
            {imgError ? 'Image could not be loaded' : 'Image unavailable'}
          </div>
        )}
      </div>

      {/* Caption */}
      <p
        style={{
          fontSize: '11px',
          color: 'var(--text-muted)',
          lineHeight: 1.55,
          padding: '8px 0 0',
          borderTop: '1px solid var(--border)',
          marginTop: 0,
          background: 'var(--bg-raised)',
        }}
      >
        {CAPTIONS[mode]}
      </p>
    </div>
  );
}
