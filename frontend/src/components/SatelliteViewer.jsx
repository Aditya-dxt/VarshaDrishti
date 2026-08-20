/**
 * SatelliteViewer.jsx
 * Displays satellite imagery from the API.
 * Image URL, label, and metadata are all supplied via props.
 */
import { useState } from 'react';
import { ImageOff } from 'lucide-react';
import LoadingState from './LoadingState.jsx';

export default function SatelliteViewer({ imageData, loading }) {
  const [imgError, setImgError] = useState(false);

  if (loading) return <LoadingState label="Loading satellite observation…" lines={4} />;

  if (!imageData?.available || imgError) {
    return (
      <div
        className="flex flex-col items-center justify-center gap-3 rounded-xl"
        style={{ height: 200, background: 'var(--bg-elevated)', border: '1px dashed var(--border-mid)' }}
      >
        <ImageOff size={26} style={{ color: 'var(--text-muted)' }} />
        <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>
          {imgError ? 'Image could not be loaded' : 'No satellite image available'}
        </p>
        {!imageData?.available && (
          <p style={{ color: 'var(--text-muted)', fontSize: '12px', maxWidth: 240, textAlign: 'center' }}>
            The prediction is available but the corresponding imagery has not been supplied.
          </p>
        )}
      </div>
    );
  }

  return (
    <div className="animate-fade-in space-y-2">
      <div className="relative rounded-xl overflow-hidden" style={{ background: '#060d1a' }}>
        <img
          src={imageData.image_url}
          alt={`Satellite observation — ${imageData.location || ''} at ${imageData.timestamp || ''}`}
          className="w-full object-cover rounded-xl"
          style={{ maxHeight: 260, minHeight: 160 }}
          onError={() => setImgError(true)}
        />
        {/* Overlay label */}
        {imageData.channel_label && (
          <div
            className="absolute bottom-2 left-2 px-2 py-0.5 rounded text-xs mono"
            style={{ background: 'rgba(0,0,0,0.65)', color: 'var(--text-secondary)', backdropFilter: 'blur(4px)' }}
          >
            {imageData.channel_label}
          </div>
        )}
      </div>
      {imageData.timestamp && (
        <p style={{ color: 'var(--text-muted)', fontSize: '11px' }}>
          Captured: {imageData.timestamp}
          {imageData.location && <> · {imageData.location}</>}
        </p>
      )}
    </div>
  );
}
