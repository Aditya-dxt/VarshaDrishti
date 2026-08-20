/**
 * riskHelpers.js
 * Single source of truth for risk label → visual token mapping.
 * Colors aligned with the light theme palette.
 */

export const RISK_META = {
  no_rain: {
    label:       'No Rain',
    shortLabel:  'No Rain',
    colorClass:  'risk-badge-none',
    textColor:   '#64748B',   /* slate-500 */
    dotColor:    '#64748B',
    barColor:    '#64748B',
    bgColor:     'rgba(100,116,139,0.08)',
    borderColor: 'rgba(100,116,139,0.25)',
  },
  moderate: {
    label:       'Moderate Rain',
    shortLabel:  'Moderate',
    colorClass:  'risk-badge-moderate',
    textColor:   '#D97706',   /* amber-600 */
    dotColor:    '#D97706',
    barColor:    '#F59E0B',   /* amber-500 */
    bgColor:     'rgba(245,158,11,0.08)',
    borderColor: 'rgba(245,158,11,0.35)',
  },
  heavy: {
    label:       'Heavy Rain',
    shortLabel:  'Heavy',
    colorClass:  'risk-badge-heavy',
    textColor:   '#EA580C',   /* orange-600 */
    dotColor:    '#EA580C',
    barColor:    '#F97316',   /* orange-500 */
    bgColor:     'rgba(249,115,22,0.08)',
    borderColor: 'rgba(249,115,22,0.35)',
  },
  high_impact: {
    label:       'High-Impact Rain',
    shortLabel:  'High Impact',
    colorClass:  'risk-badge-impact',
    textColor:   '#DC2626',   /* red-600 */
    dotColor:    '#DC2626',
    barColor:    '#DC2626',
    bgColor:     'rgba(220,38,38,0.08)',
    borderColor: 'rgba(220,38,38,0.35)',
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
