# Cloud Monitoring & Incident Report System

A real-time cloud monitoring system with automatic incident detection and reporting.

## Features

- **Health Monitoring** — Periodically checks service endpoints and tracks uptime
- **Auto-Detect Incidents** — Automatically creates incident reports when a service goes down
- **Auto-Resolve** — Incidents are auto-resolved when the service recovers
- **Dashboard** — Real-time stats dashboard with service status overview
- **Incident History** — Full incident report log with severity levels
- **REST API** — Full CRUD API for monitors and incidents

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python FastAPI |
| Scheduler | APScheduler |
| HTTP Client | httpx |
| Database | SQLite (via SQLAlchemy) |
| Frontend | React + Vite |

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

API runs at `http://localhost:8000`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/monitors/dashboard` | Dashboard stats |
| GET | `/api/monitors` | List all monitors |
| POST | `/api/monitors` | Add a monitor |
| GET | `/api/monitors/:id` | Get monitor |
| PUT | `/api/monitors/:id` | Update monitor |
| DELETE | `/api/monitors/:id` | Delete monitor |
| GET | `/api/incidents` | List incidents |
| GET | `/api/incidents/:id` | Get incident |
| PATCH | `/api/incidents/:id` | Update incident status |
