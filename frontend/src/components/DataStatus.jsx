/**
 * DataStatus.jsx
 * Plain text data freshness status. No icons.
 */
import { formatTimestamp } from '../utils/riskHelpers.js';

export default function DataStatus({ system }) {
  if (!system) return null;
  const { data_status, last_data_at } = system;
  const isWaiting = data_status === 'waiting' || data_status === 'unavailable';

  return (
    <span
      style={{ fontSize: '11px', color: 'var(--text-muted)', letterSpacing: '0.04em' }}
      aria-label="Data freshness"
    >
      {isWaiting
        ? 'Awaiting satellite data'
        : <>Last observation · <span style={{ color: 'var(--text-secondary)' }}>{formatTimestamp(last_data_at)}</span></>}
    </span>
  );
}
