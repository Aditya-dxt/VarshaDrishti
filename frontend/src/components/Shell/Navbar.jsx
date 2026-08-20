/**
 * Navbar.jsx — Application header
 * Flat, solid, typographically clear.
 * No frosted glass, no glow, no decorative container around the logo.
 */
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Clock, BarChart2 } from 'lucide-react';
import ModelStatus from '../ModelStatus.jsx';

const NAV_ITEMS = [
  { to: '/dashboard',  label: 'Overview',    Icon: LayoutDashboard },
  { to: '/historical', label: 'History',     Icon: Clock           },
  { to: '/metrics',    label: 'Performance', Icon: BarChart2       },
];

export default function Navbar({ systemStatus }) {
  return (
    <header
      role="banner"
      style={{
        position: 'sticky',
        top: 0,
        zIndex: 50,
        background: 'var(--bg-surface)',
        borderBottom: '1px solid var(--border)',
      }}
    >
      <div
        className="mx-auto flex items-center justify-between"
        style={{ maxWidth: 1400, padding: '0 28px', height: 52 }}
      >
        {/* ── Brand ─────────────────────────────────────────── */}
        <div className="flex items-center gap-4">
          <div className="leading-none">
            <span
              className="block font-semibold tracking-widest"
              style={{ fontSize: '13px', color: 'var(--text-primary)', letterSpacing: '0.12em' }}
            >
              BHOOMIDRISHTI
            </span>
            <span
              className="block"
              style={{ fontSize: '9px', color: 'var(--text-muted)', letterSpacing: '0.14em', marginTop: '1px' }}
            >
              SATELLITE RAINFALL INTELLIGENCE
            </span>
          </div>

          {/* vertical rule */}
          <div style={{ width: 1, height: 28, background: 'var(--border-mid)' }} />

          {/* Navigation */}
          <nav
            className="hidden sm:flex items-center"
            role="navigation"
            aria-label="Main navigation"
            style={{ gap: 2 }}
          >
            {NAV_ITEMS.map(({ to, label, Icon }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium tracking-wide transition-colors duration-100
                   ${isActive
                     ? 'text-[var(--text-primary)]'
                     : 'text-[var(--text-muted)] hover:text-[var(--text-secondary)]'}`
                }
                style={({ isActive }) => ({
                  borderBottom: isActive ? '1px solid var(--accent)' : '1px solid transparent',
                  paddingBottom: '14px',
                  paddingTop: '14px',
                  letterSpacing: '0.06em',
                })}
              >
                <Icon size={12} />
                {label.toUpperCase()}
              </NavLink>
            ))}
          </nav>
        </div>

        {/* ── Status ────────────────────────────────────────── */}
        <ModelStatus status={systemStatus || 'ready'} />
      </div>

      {/* Mobile nav — full-width tab bar below header */}
      <div
        className="sm:hidden flex"
        style={{ borderTop: '1px solid var(--border)' }}
      >
        {NAV_ITEMS.map(({ to, label, Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex-1 flex flex-col items-center gap-0.5 py-2 text-[10px] font-medium tracking-widest transition-colors
               ${isActive ? 'text-[var(--text-primary)]' : 'text-[var(--text-muted)]'}`
            }
          >
            <Icon size={14} />
            {label.toUpperCase()}
          </NavLink>
        ))}
      </div>
    </header>
  );
}
