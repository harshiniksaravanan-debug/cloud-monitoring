import { useEffect, useState } from 'react';
import { api } from './api';
import Dashboard from './components/Dashboard';
import MonitorList from './components/MonitorList';
import AddMonitor from './components/AddMonitor';
import IncidentList from './components/IncidentList';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState(null);
  const [monitors, setMonitors] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [error, setError] = useState(null);

  async function fetchAll() {
    try {
      const [s, m, i] = await Promise.all([
        api.getDashboard(),
        api.listMonitors(),
        api.listIncidents({ limit: '100' }),
      ]);
      setStats(s);
      setMonitors(m);
      setIncidents(i);
      setError(null);
    } catch (e) {
      setError(e.message);
    }
  }

  useEffect(() => { fetchAll(); const t = setInterval(fetchAll, 15000); return () => clearInterval(t); }, []);

  const tabs = [
    { key: 'dashboard', label: 'Dashboard' },
    { key: 'monitors', label: 'Monitors' },
    { key: 'incidents', label: 'Incidents' },
  ];

  return (
    <div className="app">
      <header className="header">
        <h1>Cloud Monitoring & Incident Report</h1>
        <nav className="tabs">
          {tabs.map(t => (
            <button key={t.key} className={`tab ${activeTab === t.key ? 'active' : ''}`}
              onClick={() => setActiveTab(t.key)}>{t.label}</button>
          ))}
        </nav>
      </header>

      <main className="main">
        {error && <div className="error-banner">Connection Error: {error}</div>}

        {activeTab === 'dashboard' && stats && <Dashboard stats={stats} incidents={incidents} />}
        {activeTab === 'monitors' && (
          <>
            <AddMonitor onAdded={fetchAll} />
            <MonitorList monitors={monitors} onRefresh={fetchAll} />
          </>
        )}
        {activeTab === 'incidents' && (
          <IncidentList incidents={incidents} onRefresh={fetchAll} />
        )}
      </main>
    </div>
  );
}
