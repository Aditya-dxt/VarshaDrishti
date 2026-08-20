/**
 * RiskMap.jsx — Light theme
 * Leaflet map with light CartoDB tiles.
 * Clean marker + pulsing ring. No dark styling.
 * All coordinates come from props — nothing hardcoded.
 *
 * Props:
 *   metadata   — { latitude, longitude, location, timestamp }
 *   prediction — { label }
 *   height     — number (px), default 340
 *   zoom       — number, default 7
 */
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import { useEffect } from 'react';
import 'leaflet/dist/leaflet.css';
import { getRiskMeta, formatTimestamp } from '../utils/riskHelpers.js';
import EmptyState from './EmptyState.jsx';

/* ── Recenter helper ──────────────────────────────────────────── */
function RecenterView({ center, zoom }) {
  const map = useMap();
  useEffect(() => {
    map.flyTo(center, zoom, { duration: 0.8 });
  }, [center[0], center[1], zoom]); // eslint-disable-line react-hooks/exhaustive-deps
  return null;
}

export default function RiskMap({ metadata, prediction, height = 340, zoom = 7 }) {
  if (!metadata?.latitude || !metadata?.longitude) {
    return (
      <EmptyState
        title="Location data unavailable"
        body="Coordinates have not been provided for this prediction."
      />
    );
  }

  const { latitude, longitude, location, timestamp } = metadata;
  const meta   = getRiskMeta(prediction?.label);
  const center = [latitude, longitude];

  const latStr = `${Math.abs(latitude).toFixed(3)}°${latitude >= 0 ? 'N' : 'S'}`;
  const lonStr = `${Math.abs(longitude).toFixed(3)}°${longitude >= 0 ? 'E' : 'W'}`;

  return (
    <div
      className="animate-fade-in"
      style={{ position: 'relative', height, overflow: 'hidden', lineHeight: 0 }}
    >
      <MapContainer
        center={center}
        zoom={zoom}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={false}
        zoomControl={true}
        attributionControl={false}
      >
        {/* Light CartoDB tiles */}
        <TileLayer url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png" />

        <RecenterView center={center} zoom={zoom} />

        {/* Outermost diffuse ring */}
        <CircleMarker
          center={center}
          radius={44}
          pathOptions={{
            color:     meta.dotColor,
            fill:      false,
            weight:    1.5,
            opacity:   0.12,
            className: 'animate-pulse-ring',
          }}
        />

        {/* Mid ring */}
        <CircleMarker
          center={center}
          radius={26}
          pathOptions={{
            color:   meta.dotColor,
            fill:    false,
            weight:  1.5,
            opacity: 0.28,
          }}
        />

        {/* Primary filled marker */}
        <CircleMarker
          center={center}
          radius={9}
          pathOptions={{
            color:       meta.dotColor,
            fillColor:   meta.dotColor,
            fillOpacity: 0.45,
            weight:      2,
          }}
        >
          <Popup>
            <div
              style={{
                fontFamily: 'var(--font-sans)',
                fontSize: '12px',
                minWidth: 160,
                color: 'var(--text-primary)',
              }}
            >
              <p style={{ fontWeight: 700, color: meta.dotColor, margin: '0 0 5px' }}>
                {meta.label}
              </p>
              <p style={{ color: 'var(--text-secondary)', margin: '0 0 3px' }}>{location}</p>
              <p
                style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: '10px',
                  color: 'var(--text-muted)',
                  margin: '0 0 3px',
                }}
              >
                {latStr}&nbsp;&nbsp;{lonStr}
              </p>
              <p style={{ color: 'var(--text-muted)', fontSize: '11px', margin: 0 }}>
                {formatTimestamp(timestamp)}
              </p>
            </div>
          </Popup>
        </CircleMarker>
      </MapContainer>

      {/* ── Coordinate annotation overlay ───────────────────── */}
      <div
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          padding: '5px 12px',
          background: 'rgba(255,255,255,0.88)',
          borderTop: '1px solid rgba(0,0,0,0.06)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          zIndex: 400,
          pointerEvents: 'none',
        }}
      >
        <span
          className="coord"
          style={{ fontSize: '10px', color: 'var(--text-muted)' }}
        >
          {latStr}&nbsp;·&nbsp;{lonStr}
        </span>
        {location && (
          <span
            style={{
              fontSize: '10px',
              color: 'var(--text-muted)',
              letterSpacing: '0.03em',
              maxWidth: '55%',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
          >
            {location}
          </span>
        )}
      </div>
    </div>
  );
}
