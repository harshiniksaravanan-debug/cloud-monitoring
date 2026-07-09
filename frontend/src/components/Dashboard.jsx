export default function Dashboard({ stats, patients }) {
  const cards = [
    { label: 'Total Patients', value: stats.total_patients, color: '#6366f1' },
    { label: 'Active Cases', value: stats.active_records, color: '#f59e0b' },
    { label: 'Resolved', value: stats.resolved_records, color: '#22c55e' },
    { label: 'Total Records', value: stats.total_records, color: '#06b6d4' },
    { label: 'Male / Female', value: `${stats.male_count} / ${stats.female_count}`, color: '#8b5cf6' },
  ];

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
        <h2>Recent Patients</h2>
        {patients.length === 0 ? (
          <p className="empty-state">No patients registered yet</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Age</th>
                <th>Gender</th>
                <th>Blood Group</th>
                <th>Contact</th>
                <th>Records</th>
              </tr>
            </thead>
            <tbody>
              {patients.slice(0, 10).map(p => (
                <tr key={p.id}>
                  <td><strong>{p.name}</strong></td>
                  <td>{p.age}</td>
                  <td>{p.gender}</td>
                  <td><span className="badge badge-info">{p.blood_group || '-'}</span></td>
                  <td>{p.contact}</td>
                  <td>{p.record_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
