/**
 * GradCAMViewer.jsx
 * Used on the Historical page. Flat tab strip, no rounded containers.
 * Same three modes: Original | Heatmap | Overlay
 */
import { useState } from 'react';
import LoadingState from './LoadingState.jsx';
import EmptyState   from './EmptyState.jsx';

const MODES = [
  { id: 'original', label: 'Satellite',  key: 'original_url' },
  { id: 'heatmap',  label: 'Grad-CAM',   key: 'heatmap_url'  },
  { id: 'overlay',  label: 'Overlay',    key: 'overlay_url'  },
];

const CAPTIONS = {
  original: 'Original INSAT-3DR observation used as model input.',
  heatmap:  'Regions of highest model attention. Warmer colour = stronger influence.',
  overlay:  'Grad-CAM attention overlaid on the satellite image.',
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
        style={{ display: 'flex', borderBottom: '1px solid var(--border)', marginBottom: 0 }}
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

      {/* Image */}
      <div
        role="tabpanel"
        style={{ position: 'relative', background: '#040b14', lineHeight: 0 }}
      >
        {imgUrl && !imgError ? (
          <img
            key={mode}
            src={imgUrl}
            alt={CAPTIONS[mode]}
            style={{ width: '100%', maxHeight: 300, objectFit: 'cover', display: 'block' }}
            onError={() => setImgError(true)}
          />
        ) : (
          <div
            style={{
              height: 220,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--text-muted)',
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
          lineHeight: 1.5,
          padding: '8px 0 0',
          borderTop: '1px solid var(--border)',
          marginTop: 0,
        }}
      >
        {CAPTIONS[mode]}
      </p>
    </div>
  );
}
