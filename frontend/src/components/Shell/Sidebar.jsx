/**
 * Sidebar.jsx — Application sidebar shell
 *
 * Persistent left sidebar. Professional scientific intelligence platform shell.
 * Active route: subtle lighter surface + thin left accent + stronger text.
 * No glows, no gradients, no heavy animation.
 *
 * Props:
 *   systemStatus — 'ready' | 'processing' | 'waiting' | 'unavailable'
 */
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Clock, BarChart2, Satellite } from 'lucide-react';

const NAV_ITEMS = [
  { to: '/dashboard',  label: 'Overview',          Icon: LayoutDashboard },
  { to: '/historical', label: 'Historical Events',  Icon: Clock           },
  { to: '/metrics',    label: 'Model Performance',  Icon: BarChart2       },
];

const STATUS_META = {
  ready:       { label: 'System Ready',       dot: '#22C55E' },
  processing:  { label: 'Processing',         dot: '#D97706' },
  waiting:     { label: 'Awaiting Data',      dot: '#D97706' },
  unavailable: { label: 'System Unavailable', dot: '#DC2626' },
};

export default function Sidebar({ systemStatus = 'ready' }) {
  const status = STATUS_META[systemStatus] || STATUS_META['unavailable'];

  return (
    <aside className="sidebar" aria-label="Application navigation">

      {/* ── Brand ──────────────────────────────────────────── */}
      <div className="sidebar-brand">
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            marginBottom: '10px',
          }}
        >
          <div
            style={{
              width: 30,
              height: 30,
              background: 'rgba(107,143,175,0.12)',
              border: '1px solid rgba(107,143,175,0.22)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}
          >
            <Satellite size={14} color="var(--accent)" />
          </div>
          <div>
            <div
              style={{
                fontSize: '12px',
                fontWeight: 700,
                color: 'var(--text-primary)',
                letterSpacing: '0.10em',
                lineHeight: 1.2,
              }}
            >
              BHOOMIDRISHTI
            </div>
          </div>
        </div>
        <p
          style={{
            fontSize: '10px',
            color: 'var(--text-dim)',
            letterSpacing: '0.08em',
            textTransform: 'uppercase',
            margin: 0,
            lineHeight: 1.4,
            fontWeight: 500,
          }}
        >
          Satellite Rainfall<br />Intelligence
        </p>
      </div>

      {/* ── Navigation ─────────────────────────────────────── */}
      <nav className="sidebar-nav" role="navigation" aria-label="Main navigation">

        <p
          className="label"
          style={{
            padding: '16px 20px 8px',
            display: 'block',
          }}
        >
          Navigation
        </p>

        {NAV_ITEMS.map(({ to, label, Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `nav-item ${isActive ? 'active' : ''}`
            }
          >
            <Icon size={15} style={{ flexShrink: 0, opacity: 0.8 }} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* ── System status footer ────────────────────────────── */}
      <div className="sidebar-footer">
        <p className="label" style={{ marginBottom: '10px' }}>System</p>

        {/* Status */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            marginBottom: '8px',
          }}
          aria-live="polite"
          aria-label={`System status: ${status.label}`}
        >
          <span
            style={{
              display: 'inline-block',
              width: 6,
              height: 6,
              borderRadius: '50%',
              background: status.dot,
              flexShrink: 0,
            }}
          />
          <span
            style={{
              fontSize: '12px',
              color: 'var(--text-secondary)',
              fontWeight: 450,
            }}
          >
            {status.label}
          </span>
        </div>

        {/* Instrument */}
        <div
          style={{
            fontSize: '10px',
            color: 'var(--text-dim)',
            letterSpacing: '0.07em',
            textTransform: 'uppercase',
            fontWeight: 500,
          }}
        >
          INSAT-3DR
        </div>
      </div>
    </aside>
  );
}
