/**
 * Sidebar.jsx — Application sidebar shell
 * Light scientific theme. White background, dark text, blue active state.
 * Restrained, professional, institutional.
 */
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Clock, BarChart2, Satellite, RefreshCw, Settings } from 'lucide-react';

const NAV_ITEMS = [
  { to: '/dashboard',  label: 'Overview',          Icon: LayoutDashboard },
  { to: '/historical', label: 'Historical Events',  Icon: Clock           },
  { to: '/metrics',    label: 'Model Performance',  Icon: BarChart2       },
];

const STATUS_META = {
  ready:       { label: 'System Online',      dot: '#16A34A' },
  processing:  { label: 'Processing',         dot: '#D97706' },
  waiting:     { label: 'Awaiting Data',      dot: '#D97706' },
  unavailable: { label: 'Offline',            dot: '#DC2626' },
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
            marginBottom: '8px',
          }}
        >
          <div
            style={{
              width: 28,
              height: 28,
              background: 'var(--accent-light)',
              border: '1px solid var(--accent-border)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
              borderRadius: '4px',
            }}
          >
            <Satellite size={13} color="var(--accent)" />
          </div>
          <div
            style={{
              fontSize: '13px',
              fontWeight: 700,
              color: 'var(--text-primary)',
              letterSpacing: '0.06em',
              lineHeight: 1.2,
            }}
          >
            BHOOMIDRISHTI
          </div>
        </div>
        <p
          style={{
            fontSize: '10px',
            color: 'var(--text-muted)',
            letterSpacing: '0.04em',
            margin: 0,
            lineHeight: 1.5,
            fontWeight: 500,
            paddingLeft: '38px',
          }}
        >
          Satellite Rainfall Intelligence
        </p>
      </div>

      {/* ── Navigation ─────────────────────────────────────── */}
      <nav className="sidebar-nav" role="navigation" aria-label="Main navigation">
        <p
          className="label"
          style={{
            padding: '16px 20px 6px',
            display: 'block',
            color: 'var(--text-dim)',
          }}
        >
          Navigation
        </p>

        {NAV_ITEMS.map(({ to, label, Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <Icon size={15} style={{ flexShrink: 0 }} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* ── System status footer ────────────────────────────── */}
      <div className="sidebar-footer">
        <p className="label" style={{ marginBottom: '10px', color: 'var(--text-dim)' }}>
          System
        </p>

        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            marginBottom: '6px',
          }}
          aria-live="polite"
          aria-label={`System status: ${status.label}`}
        >
          <span
            style={{
              display: 'inline-block',
              width: 7,
              height: 7,
              borderRadius: '50%',
              background: status.dot,
              flexShrink: 0,
            }}
          />
          <span
            style={{
              fontSize: '12px',
              color: 'var(--text-secondary)',
              fontWeight: 500,
            }}
          >
            {status.label}
          </span>
        </div>

        <div
          style={{
            fontSize: '10px',
            color: 'var(--text-dim)',
            letterSpacing: '0.06em',
            textTransform: 'uppercase',
            fontWeight: 600,
            paddingTop: '2px',
          }}
        >
          INSAT-3DR
        </div>
      </div>
    </aside>
  );
}
