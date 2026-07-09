import { useState } from 'react';
import { api } from '../api';
import MedicalRecords from './MedicalRecords';

export default function PatientList({ patients, onRefresh }) {
  const [selected, setSelected] = useState(null);
  const [records, setRecords] = useState([]);
  const [loadingRecords, setLoadingRecords] = useState(false);

  async function selectPatient(p) {
    setSelected(p);
    setLoadingRecords(true);
    try {
      const recs = await api.listRecords(p.id);
      setRecords(recs);
    } catch (e) {
      setRecords([]);
    }
    setLoadingRecords(false);
  }

  async function deletePatient(id) {
    await api.deletePatient(id);
    if (selected?.id === id) setSelected(null);
    onRefresh();
  }

  async function onRecordsChanged() {
    if (selected) {
      const recs = await api.listRecords(selected.id);
      setRecords(recs);
    }
    onRefresh();
  }

  return (
    <div className="section">
      <h2>Registered Patients</h2>
      {patients.length === 0 ? (
        <p className="empty-state">No patients registered</p>
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
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {patients.map(p => (
              <tr key={p.id} className={selected?.id === p.id ? 'row-selected' : ''}>
                <td><strong>{p.name}</strong></td>
                <td>{p.age}</td>
                <td>{p.gender}</td>
                <td><span className="badge badge-info">{p.blood_group || '-'}</span></td>
                <td>{p.contact}</td>
                <td><span className="badge badge-up">{p.record_count}</span></td>
                <td className="actions">
                  <button className="btn btn-sm" onClick={() => selectPatient(p)}>View Records</button>
                  <button className="btn btn-sm btn-danger" onClick={() => deletePatient(p.id)}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {selected && (
        <MedicalRecords
          patient={selected}
          records={records}
          loading={loadingRecords}
          onChanged={onRecordsChanged}
          onClose={() => setSelected(null)}
        />
      )}
    </div>
  );
}
