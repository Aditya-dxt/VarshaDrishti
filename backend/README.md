# BHOOMIDRISHTI backend

FastAPI integration layer for the BHOOMIDRISHTI rainfall-risk frontend and the future ML/XAI pipeline. It deliberately contains no model, predictions, metrics, historical events, or fallback data.

## Run

Use Python 3.11+.

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

The API docs are available at `http://localhost:8000/docs`; health is `GET /health`.

## Configuration

All settings use the `BHOOMIDRISHTI_` prefix. Set `CORS_ORIGINS` to a JSON array; the default permits Vite at `http://localhost:5173`.

`PREDICTOR_CLASS` must be `package.module:Class`. `METRICS_PATH` and `HISTORICAL_EVENTS_PATH` must point to real JSON artifacts. If any source is missing, the API returns an explicit 503 or 404 instead of invented data.

## Person 1 model interface

Person 1 should implement a class with `predict(observation: Mapping | None) -> Mapping`. Configure that class through `BHOOMIDRISHTI_PREDICTOR_CLASS`. Its returned mapping must contain `prediction`, `probabilities`, and `metadata`; `xai` is optional. `prediction` uses class IDs 0–3 mapped to `no_rain`, `moderate`, `heavy`, `high_impact`. Probability keys use those labels and must sum to approximately 1. `metadata.timestamp` must be timezone-aware ISO-8601, and include latitude/longitude.

The adapter accepts either a keyed probability mapping or a four-element probability sequence in the specified class order. Put integration-specific imports, checkpoint loading, tensor conversion, and raw-output translation in `app/adapters/model_adapter.py`; routes and schemas remain unchanged.

## Artifacts

`METRICS_PATH` contains one object matching the `/api/metrics` schema. `HISTORICAL_EVENTS_PATH` contains either a list, or `{ "events": [...] }`; each entry for event detail contains `event` plus the normal prediction response fields. The list endpoint derives its event summaries from those entries. Grad-CAM uses `xai.gradcam.image_url`; SHAP uses `xai.shap.features` with `name`, `value`, and `contribution`.

## Endpoints

- `POST /api/predict` — optional `{ "observation": { ... } }` sent to the configured model.
- `GET /api/latest` — configured model’s current/latest observation.
- `GET /api/metrics` — validated real metrics artifact.
- `GET /api/historical` and `GET /api/historical/{event_id}` — validated real historical artifact.
- `GET /health` — process health only; it does not claim the model/artifacts are available.

## Tests

```powershell
cd backend
pytest
```
