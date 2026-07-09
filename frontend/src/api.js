const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

async function request(url, options = {}) {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  getDashboard: () => request('/patients/dashboard'),
  listPatients: () => request('/patients'),
  getPatient: (id) => request(`/patients/${id}`),
  createPatient: (data) => request('/patients', { method: 'POST', body: JSON.stringify(data) }),
  updatePatient: (id, data) => request(`/patients/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deletePatient: (id) => request(`/patients/${id}`, { method: 'DELETE' }),
  listRecords: (patientId) => request(`/patients/${patientId}/records`),
  createRecord: (patientId, data) => request(`/patients/${patientId}/records`, { method: 'POST', body: JSON.stringify(data) }),
  updateRecord: (recordId, data) => request(`/patients/records/${recordId}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteRecord: (recordId) => request(`/patients/records/${recordId}`, { method: 'DELETE' }),
};
