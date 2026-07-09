import { useState } from 'react';
import { api } from '../api';

export default function AddPatient({ onAdded }) {
  const [form, setForm] = useState({
    name: '', age: '', gender: 'Male', contact: '',
    blood_group: '', allergies: '', height: '', weight: '', emergency_contact: '',
  });
  const [loading, setLoading] = useState(false);

  function update(field) {
    return (e) => setForm({ ...form, [field]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!form.name || !form.age || !form.contact) return;
    setLoading(true);
    try {
      await api.createPatient({
        ...form,
        age: parseInt(form.age),
        height: form.height ? parseFloat(form.height) : null,
        weight: form.weight ? parseFloat(form.weight) : null,
      });
      setForm({ name: '', age: '', gender: 'Male', contact: '', blood_group: '', allergies: '', height: '', weight: '', emergency_contact: '' });
      onAdded();
    } catch (err) {
      alert('Failed: ' + err.message);
    }
    setLoading(false);
  }

  return (
    <div className="section add-monitor">
      <h2>Register New Patient</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-row" style={{ marginBottom: 12 }}>
          <input className="input" placeholder="Full Name*" value={form.name} onChange={update('name')} required />
          <input className="input" type="number" placeholder="Age*" value={form.age} onChange={update('age')} required style={{ width: 100 }} />
          <select className="input" value={form.gender} onChange={update('gender')} style={{ width: 120 }}>
            <option>Male</option>
            <option>Female</option>
            <option>Other</option>
          </select>
          <input className="input" placeholder="Contact*" value={form.contact} onChange={update('contact')} required />
        </div>
        <div className="form-row" style={{ marginBottom: 12 }}>
          <input className="input" placeholder="Blood Group (e.g. A+)" value={form.blood_group} onChange={update('blood_group')} style={{ width: 140 }} />
          <input className="input" placeholder="Allergies" value={form.allergies} onChange={update('allergies')} />
          <input className="input" type="number" step="0.1" placeholder="Height (cm)" value={form.height} onChange={update('height')} style={{ width: 130 }} />
          <input className="input" type="number" step="0.1" placeholder="Weight (kg)" value={form.weight} onChange={update('weight')} style={{ width: 130 }} />
        </div>
        <div className="form-row">
          <input className="input" placeholder="Emergency Contact" value={form.emergency_contact} onChange={update('emergency_contact')} />
          <button className="btn btn-primary" disabled={loading}>
            {loading ? 'Adding...' : 'Register Patient'}
          </button>
        </div>
      </form>
    </div>
  );
}
