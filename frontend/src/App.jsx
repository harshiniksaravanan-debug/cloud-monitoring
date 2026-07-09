import { useEffect, useState } from 'react';
import { api } from './api';
import Dashboard from './components/Dashboard';
import PatientList from './components/PatientList';
import AddPatient from './components/AddPatient';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState(null);
  const [patients, setPatients] = useState([]);
  const [error, setError] = useState(null);

  async function fetchAll() {
    try {
      const [s, p] = await Promise.all([
        api.getDashboard(),
        api.listPatients(),
      ]);
      setStats(s);
      setPatients(p);
      setError(null);
    } catch (e) {
      setError(e.message);
    }
  }

  useEffect(() => { fetchAll(); }, []);

  const tabs = [
    { key: 'dashboard', label: 'Dashboard' },
    { key: 'patients', label: 'Patients' },
  ];

  return (
    <div className="app">
      <header className="header">
        <h1>Hospital Patient & Disease Management</h1>
        <nav className="tabs">
          {tabs.map(t => (
            <button key={t.key} className={`tab ${activeTab === t.key ? 'active' : ''}`}
              onClick={() => setActiveTab(t.key)}>{t.label}</button>
          ))}
        </nav>
      </header>

      <main className="main">
        {error && <div className="error-banner">Connection Error: {error}</div>}

        {activeTab === 'dashboard' && stats && (
          <Dashboard stats={stats} patients={patients} />
        )}
        {activeTab === 'patients' && (
          <>
            <AddPatient onAdded={fetchAll} />
            <PatientList patients={patients} onRefresh={fetchAll} />
          </>
        )}
      </main>
    </div>
  );
}
