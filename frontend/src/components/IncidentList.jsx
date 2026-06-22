import { api } from '../api';

export default function IncidentList({ incidents, onRefresh }) {
  async function resolveIncident(id) {
    await api.updateIncident(id, { status: 'resolved' });
    onRefresh();
  }

  if (incidents.length === 0) {
    return (
      <div className="section">
        <h2>Incident Report History</h2>
        <p className="empty-state">No incidents reported</p>
      </div>
    );
  }

  return (
    <div className="section">
      <h2>Incident Report History</h2>
      <table className="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Title</th>
            <th>Service</th>
            <th>Severity</th>
            <th>Status</th>
            <th>Detected</th>
            <th>Resolved</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {incidents.map(inc => (
            <tr key={inc.id}>
              <td>#{inc.id}</td>
              <td>{inc.title}</td>
              <td>{inc.monitor_name || `#${inc.monitor_id}`}</td>
              <td><span className={`badge badge-${inc.severity}`}>{inc.severity}</span></td>
              <td><span className={`badge badge-${inc.status === 'resolved' ? 'up' : 'down'}`}>{inc.status}</span></td>
              <td>{new Date(inc.detected_at).toLocaleString()}</td>
              <td>{inc.resolved_at ? new Date(inc.resolved_at).toLocaleString() : '-'}</td>
              <td>
                {inc.status === 'open' && (
                  <button className="btn btn-sm" onClick={() => resolveIncident(inc.id)}>
                    Resolve
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
