/**
 * ProbabilityChart.jsx
 * Flat horizontal bar chart. No rounded caps. Grid removed.
 * Risk colours map correctly to rainfall severity only.
 */
import {
  BarChart, Bar, XAxis, YAxis,
  Tooltip, ResponsiveContainer, Cell,
} from 'recharts';
import { getRiskMeta } from '../utils/riskHelpers.js';

const CLASS_ORDER = ['no_rain', 'moderate', 'heavy', 'high_impact'];

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const { name, value } = payload[0].payload;
  const meta = getRiskMeta(name);
  return (
    <div
      style={{
        background: 'var(--bg-raised)',
        border: '1px solid var(--border-mid)',
        padding: '8px 12px',
        fontSize: '12px',
      }}
    >
      <p style={{ color: meta.dotColor, fontWeight: 600, margin: '0 0 2px' }}>{meta.label}</p>
      <p style={{ color: 'var(--text-secondary)', margin: 0 }}>
        {(value * 100).toFixed(1)}%
      </p>
    </div>
  );
};

export default function ProbabilityChart({ probabilities }) {
  if (!probabilities) return null;

  const data = CLASS_ORDER.map((key) => ({
    name:  key,
    label: getRiskMeta(key).shortLabel,
    value: probabilities[key] ?? 0,
  }));

  return (
    <div style={{ width: '100%', height: 160 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 0, right: 8, left: 0, bottom: 0 }}
        >
          <XAxis
            type="number"
            domain={[0, 1]}
            tickFormatter={(v) => `${Math.round(v * 100)}%`}
            tick={{ fill: 'var(--text-muted)', fontSize: 10, fontFamily: 'var(--font-mono)' }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            type="category"
            dataKey="label"
            width={72}
            tick={{ fill: 'var(--text-secondary)', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            content={<CustomTooltip />}
            cursor={{ fill: 'rgba(255,255,255,0.02)' }}
          />
          <Bar dataKey="value" radius={0} maxBarSize={14}>
            {data.map((entry) => (
              <Cell key={entry.name} fill={getRiskMeta(entry.name).barColor} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
