/**
 * api.js
 * ─────────────────────────────────────────────────────────────
 * Public service interface used by all React components and hooks.
 *
 * HOW TO SWITCH FROM MOCK → REAL FASTAPI:
 *   Set VITE_USE_MOCK=false in .env.local
 *   Set VITE_API_BASE=http://localhost:8000 (or your deployed URL)
 *
 * Components never need to change. Only this file and mockApi.js
 * are relevant during the integration step.
 * ─────────────────────────────────────────────────────────────
 */

import axios from 'axios';
import * as mock from './mockApi.js';

/* ── Configuration ──────────────────────────────────────── */
const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false';
const API_BASE  = import.meta.env.VITE_API_BASE  || '/api';

const http = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

/* ── Error normaliser ───────────────────────────────────── */
const normalise = (err) => {
  // Never expose raw Axios internals to components
  if (err.response) {
    throw new Error(
      err.response.data?.detail || `Server error: ${err.response.status}`
    );
  }
  if (err.request) {
    throw new Error('Unable to reach the prediction service. Check your connection.');
  }
  throw new Error(err.message || 'An unexpected error occurred.');
};

/* ── API functions ──────────────────────────────────────── */

/**
 * Get the latest processed prediction (with XAI and metadata).
 * FastAPI route: GET /api/latest
 */
export const getLatest = async () => {
  if (USE_MOCK) return mock.mockLatestPrediction();
  try {
    const { data } = await http.get('/latest');
    return data;
  } catch (err) { normalise(err); }
};

/**
 * Trigger a fresh prediction on the latest available observation.
 * FastAPI route: POST /api/predict
 */
export const predict = async () => {
  if (USE_MOCK) return mock.mockLatestPrediction();
  try {
    const { data } = await http.post('/predict');
    return data;
  } catch (err) { normalise(err); }
};

/**
 * Fetch satellite image metadata for the latest observation.
 * FastAPI route: GET /api/satellite/latest
 */
export const getSatelliteImage = async () => {
  if (USE_MOCK) return mock.mockSatelliteImage();
  try {
    const { data } = await http.get('/satellite/latest');
    return data;
  } catch (err) { normalise(err); }
};


/**
 * Fetch model evaluation metrics.
 * FastAPI route: GET /api/metrics
 */
export const getMetrics = async () => {
  if (USE_MOCK) return mock.mockMetrics();
  try {
    const { data } = await http.get('/metrics');
    return data;
  } catch (err) { normalise(err); }
};

/**
 * List all available historical events.
 * FastAPI route: GET /api/historical
 */
export const getHistoricalList = async () => {
  if (USE_MOCK) return mock.mockHistoricalList();
  try {
    const { data } = await http.get('/historical');
    return data;
  } catch (err) { normalise(err); }
};

/**
 * Get full prediction + XAI for a specific historical event.
 * FastAPI route: GET /api/historical/:id
 */
export const getHistoricalEvent = async (id) => {
  if (USE_MOCK) return mock.mockHistoricalEvent(id);
  try {
    const { data } = await http.get(`/historical/${id}`);
    return data;
  } catch (err) { normalise(err); }
};

/* ── Polling interval (ms) ──────────────────────────────── */
export const POLLING_INTERVAL_MS = Number(
  import.meta.env.VITE_POLLING_INTERVAL_MS || 30000
);
