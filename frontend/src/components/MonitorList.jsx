import { api } from '../api';

export default function MonitorList({ monitors, onRefresh }) {
  async function toggleMonitor(m) {
    await api.updateMonitor(m.id, { is_active: !m.is_active });
    onRefresh();
  }

  async function removeMonitor(id) {
    await api.deleteMonitor(id);
    onRefresh();
  }

  return (
    <div className="section">
      <h2>Monitored Services</h2>
      {monitors.length === 0 ? (
        <p className="empty-state">No services monitored yet</p>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>URL</th>
              <th>Status</th>
              <th>Response</th>
              <th>Uptime</th>
              <th>Active</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {monitors.map(m => (
              <tr key={m.id}>
                <td><strong>{m.name}</strong></td>
                <td className="url-cell">{m.url}</td>
                <td>
                  <span className={`badge badge-${m.last_status || 'pending'}`}>
                    {m.last_status || 'pending'}
                  </span>
                </td>
                <td>{m.response_time_ms ? `${m.response_time_ms}ms` : '-'}</td>
                <td>{m.uptime_percentage}%</td>
                <td>
                  <span className={`badge ${m.is_active ? 'badge-up' : 'badge-down'}`}>
                    {m.is_active ? 'active' : 'paused'}
                  </span>
                </td>
                <td className="actions">
                  <button className="btn btn-sm" onClick={() => toggleMonitor(m)}>
                    {m.is_active ? 'Pause' : 'Resume'}
                  </button>
                  <button className="btn btn-sm btn-danger" onClick={() => removeMonitor(m.id)}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
