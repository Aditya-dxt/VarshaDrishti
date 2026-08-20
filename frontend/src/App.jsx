import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useLatestPrediction } from './hooks/useLatestPrediction.js';
import Navbar     from './components/Shell/Navbar.jsx';
import Dashboard  from './pages/Dashboard.jsx';
import Historical from './pages/Historical.jsx';
import Metrics    from './pages/Metrics.jsx';

function AppShell() {
  // Pull system status from the prediction hook so Navbar always reflects it
  const { data } = useLatestPrediction();
  const systemStatus = data?.system?.model_status ?? 'waiting';

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-base)' }}>
      <Navbar systemStatus={systemStatus} />
      <Routes>
        <Route path="/"           element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard"  element={<Dashboard />} />
        <Route path="/historical" element={<Historical />} />
        <Route path="/metrics"    element={<Metrics />} />
        {/* Catch-all */}
        <Route path="*"           element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppShell />
    </BrowserRouter>
  );
}
