import { useState } from 'react';
import { api } from '../api';

export default function MedicalRecords({ patient, records, loading, onChanged, onClose }) {
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ disease_name: '', symptoms: '', diagnosis_date: '', doctor: '', medicines: '', notes: '' });
  const [submitting, setSubmitting] = useState(false);

  function update(field) {
    return (e) => setForm({ ...form, [field]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!form.disease_name) return;
    setSubmitting(true);
    try {
      await api.createRecord(patient.id, {
        ...form,
        diagnosis_date: form.diagnosis_date ? new Date(form.diagnosis_date).toISOString() : null,
      });
      setForm({ disease_name: '', symptoms: '', diagnosis_date: '', doctor: '', medicines: '', notes: '' });
      setShowForm(false);
      onChanged();
    } catch (err) {
      alert('Failed: ' + err.message);
    }
    setSubmitting(false);
  }

  async function resolveRecord(recordId) {
    await api.updateRecord(recordId, { status: 'resolved' });
    onChanged();
  }

  async function deleteRecord(recordId) {
    await api.deleteRecord(recordId);
    onChanged();
  }

  return (
    <div className="records-panel">
      <div className="records-header">
        <h3>Medical Records — {patient.name}</h3>
        <div className="actions">
          <button className="btn btn-sm btn-primary" onClick={() => setShowForm(!showForm)}>
            {showForm ? 'Cancel' : '+ Add Record'}
          </button>
          <button className="btn btn-sm" onClick={onClose}>Close</button>
        </div>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} style={{ marginBottom: 16, padding: 16, background: '#0f172a', borderRadius: 8 }}>
          <div className="form-row" style={{ marginBottom: 8 }}>
            <input className="input" placeholder="Disease Name*" value={form.disease_name} onChange={update('disease_name')} required />
            <input className="input" type="date" placeholder="Diagnosis Date" value={form.diagnosis_date} onChange={update('diagnosis_date')} style={{ width: 160 }} />
            <input className="input" placeholder="Doctor Name" value={form.doctor} onChange={update('doctor')} />
          </div>
          <div className="form-row" style={{ marginBottom: 8 }}>
            <input className="input" placeholder="Symptoms" value={form.symptoms} onChange={update('symptoms')} />
            <input className="input" placeholder="Medicines / Treatment" value={form.medicines} onChange={update('medicines')} />
          </div>
          <div className="form-row">
            <input className="input" placeholder="Additional Notes" value={form.notes} onChange={update('notes')} />
            <button className="btn btn-primary btn-sm" disabled={submitting}>
              {submitting ? 'Saving...' : 'Save Record'}
            </button>
          </div>
        </form>
      )}

      {loading ? (
        <p className="empty-state">Loading records...</p>
      ) : records.length === 0 ? (
        <p className="empty-state">No medical records for this patient</p>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Disease</th>
              <th>Symptoms</th>
              <th>Doctor</th>
              <th>Diagnosis Date</th>
              <th>Medicines</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {records.map(r => (
              <tr key={r.id}>
                <td><strong>{r.disease_name}</strong></td>
                <td>{r.symptoms || '-'}</td>
                <td>{r.doctor || '-'}</td>
                <td>{r.diagnosis_date ? new Date(r.diagnosis_date).toLocaleDateString() : '-'}</td>
                <td>{r.medicines || '-'}</td>
                <td>
                  <span className={`badge ${r.status === 'resolved' ? 'badge-up' : 'badge-down'}`}>
                    {r.status}
                  </span>
                </td>
                <td className="actions">
                  {r.status === 'ongoing' && (
                    <button className="btn btn-sm" onClick={() => resolveRecord(r.id)}>Resolve</button>
                  )}
                  <button className="btn btn-sm btn-danger" onClick={() => deleteRecord(r.id)}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
