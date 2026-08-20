/**
 * riskHelpers.js
 * Single source of truth for risk label → visual token mapping.
 * All colour values reference CSS custom properties where possible.
 */

export const RISK_META = {
  no_rain: {
    label:       'No Rain',
    shortLabel:  'No Rain',
    colorClass:  'risk-badge-none',
    textColor:   '#4b5563',
    dotColor:    '#4b5563',
    barColor:    '#4b5563',
    bgColor:     'rgba(75,85,99,0.10)',
    borderColor: 'rgba(75,85,99,0.25)',
  },
  moderate: {
    label:       'Moderate Rain',
    shortLabel:  'Moderate',
    colorClass:  'risk-badge-moderate',
    textColor:   '#d97706',
    dotColor:    '#d97706',
    barColor:    '#d97706',
    bgColor:     'rgba(217,119,6,0.10)',
    borderColor: 'rgba(217,119,6,0.30)',
  },
  heavy: {
    label:       'Heavy Rain',
    shortLabel:  'Heavy',
    colorClass:  'risk-badge-heavy',
    textColor:   '#ea580c',
    dotColor:    '#ea580c',
    barColor:    '#ea580c',
    bgColor:     'rgba(234,88,12,0.10)',
    borderColor: 'rgba(234,88,12,0.30)',
  },
  high_impact: {
    label:       'High-Impact Rain',
    shortLabel:  'High Impact',
    colorClass:  'risk-badge-impact',
    textColor:   '#dc2626',
    dotColor:    '#dc2626',
    barColor:    '#dc2626',
    bgColor:     'rgba(220,38,38,0.10)',
    borderColor: 'rgba(220,38,38,0.30)',
  },
};

export function getRiskMeta(label) {
  return RISK_META[label] || RISK_META['no_rain'];
}

export function formatTimestamp(isoString) {
  if (!isoString) return '—';
  try {
    return new Date(isoString).toLocaleString('en-IN', {
      day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
      timeZone: 'UTC', timeZoneName: 'short',
    });
  } catch {
    return isoString;
  }
}

export function formatConfidence(value) {
  if (value == null) return '—';
  return `${Math.round(value * 100)}%`;
}

export function formatMetric(value) {
  if (value == null) return '—';
  return (value * 100).toFixed(1) + '%';
}
