/**
 * mockApi.js
 * ─────────────────────────────────────────────────────────────
 * ALL development mock responses live here.
 * Components never import from this file directly.
 * Only api.js imports from here and conditionally delegates to it.
 *
 * When the real FastAPI backend is ready, set:
 *   VITE_USE_MOCK=false
 * in .env.local and api.js will route to the real service.
 * ─────────────────────────────────────────────────────────────
 */

const delay = (ms) => new Promise((res) => setTimeout(res, ms));

/* ── Shared mock timestamp ───────────────────────────────── */
const MOCK_TS = "2026-08-20T10:30:00Z";

/* ── Mock prediction response ────────────────────────────── */
export const mockLatestPrediction = async () => {
  await delay(900);
  return {
    prediction: {
      class_id: 3,
      label: "high_impact",
      confidence: 0.91,
    },
    probabilities: {
      no_rain:    0.01,
      moderate:   0.03,
      heavy:      0.05,
      high_impact: 0.91,
    },
    xai: {
      gradcam: {
        // In production, FastAPI returns a URL to the generated image.
        // Mock uses a base64 placeholder generated at runtime.
        image_url: null,        // will be replaced by SatelliteViewer/GradCAMViewer
        available: true,
      },
      shap: {
        available: true,
        features: [
          { name: "Cloud Top Temperature",  value: 0.72, contribution:  0.42 },
          { name: "Moisture Gradient",      value: 0.61, contribution:  0.31 },
          { name: "Temperature Difference", value: 0.54, contribution:  0.19 },
          { name: "Precipitable Water",     value: 0.48, contribution:  0.11 },
          { name: "Outgoing LW Radiation",  value: 0.29, contribution: -0.08 },
          { name: "Wind Shear Index",       value: 0.22, contribution: -0.12 },
        ],
      },
    },
    metadata: {
      timestamp: MOCK_TS,
      location:  "Lucknow Region, Uttar Pradesh",
      latitude:  26.85,
      longitude: 80.95,
      source:    "INSAT-3DR (mock)",
    },
    system: {
      model_status: "ready",       // "ready" | "processing" | "waiting" | "unavailable"
      data_status:  "fresh",       // "fresh" | "stale" | "waiting" | "unavailable"
      last_data_at:  MOCK_TS,
    },
  };
};

/* ── Mock satellite imagery ──────────────────────────────── */
// Returns a canvas-generated colourful placeholder so the viewer
// is never blank during development.
export const mockSatelliteImage = async () => {
  await delay(400);
  return {
    available:    true,
    image_url:    "/mock/satellite.png",  // served from public/mock/
    timestamp:    MOCK_TS,
    location:     "Lucknow Region, UP",
    channel_label: "INSAT-3DR WV (mock)",
  };
};

/* ── Mock Grad-CAM ───────────────────────────────────────── */
export const mockGradCAM = async () => {
  await delay(600);
  return {
    available:      true,
    original_url:   "/mock/satellite.png",
    heatmap_url:    "/mock/gradcam_heatmap.png",
    overlay_url:    "/mock/gradcam_overlay.png",
    timestamp:      MOCK_TS,
  };
};

/* ── Mock metrics ────────────────────────────────────────── */
export const mockMetrics = async () => {
  await delay(700);
  return {
    available: true,
    overall: {
      accuracy:  0.847,
      precision: 0.831,
      recall:    0.819,
      f1:        0.825,
      roc_auc:   0.941,
    },
    per_class: {
      no_rain:    { precision: 0.94, recall: 0.96, f1: 0.95, support: 1240 },
      moderate:   { precision: 0.81, recall: 0.78, f1: 0.79, support:  620 },
      heavy:      { precision: 0.74, recall: 0.71, f1: 0.72, support:  310 },
      high_impact:{ precision: 0.88, recall: 0.84, f1: 0.86, support:  180 },
    },
    confusion_matrix: {
      labels: ["No Rain", "Moderate", "Heavy", "High Impact"],
      matrix: [
        [1190,  35,  10,   5],
        [  18, 484,  82,  36],
        [   7,  55, 220,  28],
        [   4,  12,  13, 151],
      ],
    },
    evaluation_set: "Test split — 2350 samples",
    evaluated_at:   "2026-08-15T00:00:00Z",
  };
};

/* ── Mock historical events ──────────────────────────────── */
const HISTORICAL_EVENTS = [
  {
    id: "event-001",
    name: "Bihar Flood Precursor",
    date: "2024-07-14",
    location: "Patna Region, Bihar",
    latitude:  25.59,
    longitude: 85.13,
    type: "high_impact",
    description: "Rapid convective development 6 hours before major flooding.",
    available: true,
  },
  {
    id: "event-002",
    name: "Monsoon Onset — Mumbai",
    date: "2024-06-10",
    location: "Mumbai, Maharashtra",
    latitude:  19.08,
    longitude: 72.88,
    type: "heavy",
    description: "Southwest monsoon arrival with sustained heavy rainfall.",
    available: true,
  },
  {
    id: "event-003",
    name: "Cyclone Remnant — Odisha Coast",
    date: "2024-10-26",
    location: "Bhubaneswar Region, Odisha",
    latitude:  20.29,
    longitude: 85.82,
    type: "high_impact",
    description: "Post-landfall circulation producing extreme rainfall.",
    available: true,
  },
  {
    id: "event-004",
    name: "Dry Spell — Rajasthan",
    date: "2024-05-22",
    location: "Jaipur, Rajasthan",
    latitude:  26.91,
    longitude: 75.78,
    type: "no_rain",
    description: "Extended dry period with low convective activity.",
    available: true,
  },
];

export const mockHistoricalList = async () => {
  await delay(500);
  return { events: HISTORICAL_EVENTS };
};

export const mockHistoricalEvent = async (id) => {
  await delay(1100);
  const event = HISTORICAL_EVENTS.find((e) => e.id === id);
  if (!event) throw new Error(`Event ${id} not found`);
  return {
    event,
    prediction: {
      class_id: event.type === "high_impact" ? 3
               : event.type === "heavy" ? 2
               : event.type === "moderate" ? 1 : 0,
      label:      event.type,
      confidence: event.type === "high_impact" ? 0.88 : 0.76,
    },
    probabilities: event.type === "high_impact"
      ? { no_rain: 0.02, moderate: 0.04, heavy: 0.06, high_impact: 0.88 }
      : { no_rain: 0.08, moderate: 0.12, heavy: 0.76, high_impact: 0.04 },
    xai: {
      gradcam: { available: true, original_url: "/mock/satellite.png", heatmap_url: "/mock/gradcam_heatmap.png", overlay_url: "/mock/gradcam_overlay.png" },
      shap: {
        available: true,
        features: [
          { name: "Cloud Top Temperature",  value: 0.68, contribution: 0.38 },
          { name: "Moisture Gradient",      value: 0.55, contribution: 0.27 },
          { name: "Wind Shear Index",       value: 0.41, contribution: 0.16 },
        ],
      },
    },
    metadata: {
      timestamp:  event.date + "T06:00:00Z",
      location:   event.location,
      latitude:   event.latitude,
      longitude:  event.longitude,
    },
  };
};
