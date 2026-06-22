const API_BASE = 'http://localhost:8000/api';

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
  getDashboard: () => request('/monitors/dashboard'),
  listMonitors: () => request('/monitors'),
  createMonitor: (data) => request('/monitors', { method: 'POST', body: JSON.stringify(data) }),
  updateMonitor: (id, data) => request(`/monitors/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteMonitor: (id) => request(`/monitors/${id}`, { method: 'DELETE' }),
  listIncidents: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request(`/incidents?${qs}`);
  },
  updateIncident: (id, data) => request(`/incidents/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
};
