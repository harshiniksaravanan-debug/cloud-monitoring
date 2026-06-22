import { useState } from 'react';
import { api } from '../api';

export default function AddMonitor({ onAdded }) {
  const [name, setName] = useState('');
  const [url, setUrl] = useState('');
  const [interval, setInterval] = useState(60);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!name || !url) return;
    setLoading(true);
    try {
      await api.createMonitor({ name, url, check_interval: interval });
      setName('');
      setUrl('');
      setInterval(60);
      onAdded();
    } catch (err) {
      alert('Failed to add monitor: ' + err.message);
    }
    setLoading(false);
  }

  return (
    <div className="section add-monitor">
      <h2>Add Service to Monitor</h2>
      <form onSubmit={handleSubmit} className="form-row">
        <input className="input" placeholder="Service name" value={name}
          onChange={e => setName(e.target.value)} required />
        <input className="input" placeholder="https://example.com/health" value={url}
          onChange={e => setUrl(e.target.value)} required type="url" />
        <input className="input" type="number" placeholder="Interval (sec)" value={interval}
          onChange={e => setInterval(Number(e.target.value))} min={10} style={{ width: 140 }} />
        <button className="btn btn-primary" disabled={loading}>
          {loading ? 'Adding...' : 'Add Monitor'}
        </button>
      </form>
    </div>
  );
}
