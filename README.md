# Startup Opportunity Aggregator


Production-grade Flask SaaS-style project for scraping, validating, deduplicating, storing, searching, scheduling, and exporting startup opportunities.

## Quick Input → Output Guide

### 1) Environment validation input
```bash
python -m utils.system_check
```

Expected output:
- If dependencies are installed: `Status: READY ✅`
- If not installed: list of missing modules + exact fix command.

### 2) Application startup input
```bash
python run.py
```

Expected output:
- Flask app starts on port 5000.
- You can open dashboard at `http://127.0.0.1:5000/`.

### 3) Health endpoint input
```bash
curl -s http://127.0.0.1:5000/api/health
```

Expected output (example):
```json
{"status":"ok","service":"startup-opportunity-aggregator","timestamp_utc":"2026-05-17T10:10:10+00:00"}
```

### 4) Stats endpoint input
```bash
curl -s http://127.0.0.1:5000/api/stats
```

Expected output (example):
```json
{"total": 2, "grants": 1, "accelerators": 1}
```

### 5) Export endpoints input
```bash
curl -s http://127.0.0.1:5000/api/export/json
curl -s http://127.0.0.1:5000/api/export/csv
```

Expected output (example):
```json
{"file":"exports/opportunities_20260517_101234.json","count":20}
```

## Implemented Modules
1. Foundation & Config
2. Database Architecture
3. Core Scraper Engine
4. Source Scrapers (Startup India, F6S, Eventbrite)
5. Data Pipeline
6. Duplicate Detection
7. Dashboard UI
8. Advanced Filtering
9. Scheduling
10. Export System
11. Reliability basics (isolated scraper failures, logging)
13. Basic tests

## Run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m utils.system_check
python run.py
```

## Test
```bash
pytest -q
```
Expected:
- Normal environment with dependencies: tests execute and pass.
- Restricted environment without dependencies: tests are skipped cleanly (no ModuleNotFoundError crash).

## Common Failures + Fix
- Dependency installation blocked by network/proxy:
  - Use internal package mirror or unrestricted network.
  - Validate with `python -m utils.system_check`.
- SQLite lock under heavy writes: keep single process for local dev.
- Scraper source HTML changed: update selectors in source scraper files.
