export default function Dashboard({ stats, incidents }) {
  const cards = [
    { label: 'Total Monitors', value: stats.total_monitors, color: '#6366f1' },
    { label: 'Online', value: stats.online_count, color: '#22c55e' },
    { label: 'Offline', value: stats.offline_count, color: '#ef4444' },
    { label: 'Open Incidents', value: stats.open_incidents, color: '#f59e0b' },
    { label: 'Avg Response', value: stats.average_response_time ? `${stats.average_response_time}ms` : 'N/A', color: '#06b6d4' },
  ];

  const recentIncidents = incidents.filter(i => i.status === 'open').slice(0, 10);

  return (
    <div className="dashboard">
      <div className="stats-grid">
        {cards.map(c => (
          <div key={c.label} className="stat-card" style={{ borderTop: `4px solid ${c.color}` }}>
            <div className="stat-value">{c.value}</div>
            <div className="stat-label">{c.label}</div>
          </div>
        ))}
      </div>

      <div className="section">
        <h2>Open Incidents ({recentIncidents.length})</h2>
        {recentIncidents.length === 0 ? (
          <p className="empty-state">All systems operational</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Service</th>
                <th>Severity</th>
                <th>Detected</th>
              </tr>
            </thead>
            <tbody>
              {recentIncidents.map(inc => (
                <tr key={inc.id}>
                  <td>{inc.title}</td>
                  <td>{inc.monitor_name || `#${inc.monitor_id}`}</td>
                  <td><span className={`badge badge-${inc.severity}`}>{inc.severity}</span></td>
                  <td>{new Date(inc.detected_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
