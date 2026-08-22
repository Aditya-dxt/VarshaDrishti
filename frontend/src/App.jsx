import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useLatestPrediction } from './hooks/useLatestPrediction.js';
import Sidebar    from './components/Shell/Sidebar.jsx';
import Dashboard  from './pages/Dashboard.jsx';
import Historical from './pages/Historical.jsx';
import Metrics    from './pages/Metrics.jsx';

function AppShell() {
  const { data } = useLatestPrediction();
  // data.system is a mock-era field not present in the real PredictionResponse schema.
  // Derive status from what the real API actually provides: a loaded prediction means ready.
  const systemStatus = data?.prediction ? 'ready' : 'waiting';

  return (
    <div className="app-shell">
      <Sidebar systemStatus={systemStatus} />
      <div className="app-content">
        <Routes>
          <Route path="/"           element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard"  element={<Dashboard />} />
          <Route path="/historical" element={<Historical />} />
          <Route path="/metrics"    element={<Metrics />} />
          {/* Catch-all */}
          <Route path="*"           element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </div>
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
