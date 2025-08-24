# Aquaponics Intelligence Control System (AICS)

This repository contains a minimal but production‑ready backend for an
Aquaponics Intelligence Control System. It is designed to run on
[Render](https://render.com) using a Blueprint (`render.yaml`) that sets
up a web service and a PostgreSQL database on the free tier.

## Features

- **FastAPI** backend with automatic interactive docs at `/docs`.
- **SQLAlchemy** models for sensors, readings and recipes.
- **Prometheus** metrics endpoint at `/metrics` and health check at `/healthz`.
- **API key authentication** for ingesting sensor readings via the `X-API-Key` header.
- **PostgreSQL** connection configured via the `DATABASE_URL` environment variable.
- Includes a stub for **APScheduler** to support future scheduled tasks.

## Getting Started Locally

Install dependencies and run the server with SQLite:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then visit `http://localhost:8000/docs` for interactive API docs.

## Deployment on Render

1. Commit this repository to GitHub.
2. Create a Blueprint in Render; the included `render.yaml` provisions a web service and database.
3. Render will inject environment variables including `DATABASE_URL` and an ingest API key.
4. Health endpoint is available at `/healthz`.

## API Usage

Create a sensor:

```bash
curl -X POST http://localhost:8000/sensors \
  -H "Content-Type: application/json" \
  -d '{"name":"MH-Z19B CO2","metric":"co2","unit":"ppm","location":"rack-1/zone-A"}'
```

List sensors:

```bash
curl http://localhost:8000/sensors
```

Ingest readings (use your API key):

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <your api key>" \
  -d '{"readings":[{"sensor_id":1,"metric":"co2","value":850.0}]}'
```
