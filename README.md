# Karma Backend — Chitragupt

A FastAPI + Google ADK + Ollama microservice backend for civic karma verification.

Upload an image, get an AI-generated description, and verify it against 366 civic karma actions across 22 categories.

---

## Services

| Service | Prefix | Description |
|---|---|---|
| Health | `/health` | Liveness check + Ollama connectivity |
| Vision | `/vision` | Image → text description via Ollama |
| Verification | `/verification` | Image description + action → verdict |

---

## Requirements

- [Ollama](https://ollama.com) running locally with `gemma4:e4b` pulled
- Python 3.13 (conda env `sys` recommended)

```bash
ollama pull gemma4:e4b
```

---

## Setup

```bash
git clone https://github.com/Xwits-Developers/karma-backend.git
cd karma-backend

# create env file
cp .env.example .env

# install dependencies
conda activate sys
pip install -r requirements.txt
```

---

## Run

```bash
uvicorn gateway.main:app --reload --port 8000
```

Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## API

### Health

```
GET /health/          → { status, app_name }
GET /health/ollama    → { status, model }
```

### Vision — Describe an image

```
POST /vision/describe
Content-Type: application/json

{
  "image": "https://example.com/photo.jpg"   // URL or local path
}
```

```
POST /vision/describe/upload
Content-Type: multipart/form-data

file=<raw image bytes>
```

Response:
```json
{ "description": "...", "model": "gemma4:e4b" }
```

### Verification — Verify a karma action

```
POST /verification/verify
Content-Type: application/json

{
  "image_description": "A young neem sapling planted near a park boundary wall.",
  "action_id": "ENV-P01",
  "title": "Planted neem sapling at community park",
  "description": "I planted this sapling at Vastrapur lake garden.",
  "location": { "area": "Vastrapur", "city": "Ahmedabad" }
}
```

Response:
```json
{
  "action_id": "ENV-P01",
  "action_name": "Plant a tree (sapling)",
  "category_id": "ENV",
  "category_name": "Environment & Green Cover",
  "points": 50,
  "verdict": "Approved",
  "comment": "Image clearly shows a sapling being planted."
}
```

Verdicts: `Approved` · `Rejected` · `Human Review`

### Karma Rule Book

```
GET /verification/actions                → all 366 action IDs grouped by category
GET /verification/actions/{action_id}   → full detail for one action
```

---

## Project Structure

```
├── agents/
│   ├── base.py                  # LiteLLM model factory
│   ├── image_agent.py           # Image description prompt
│   └── verification_agent.py   # Verification prompt + verdict parser
├── core/
│   ├── config.py                # Settings via pydantic-settings
│   ├── exceptions.py            # HTTP exception types
│   ├── image_loader.py          # Load image from URL / path / base64
│   └── karma_registry.py       # In-memory action lookup (366 actions)
├── data/
│   └── karma_categories.json   # 22 categories, 366 actions
├── gateway/
│   └── main.py                  # FastAPI app factory
├── services/
│   ├── health/                  # Health endpoints
│   ├── vision/                  # Image description endpoints
│   └── verification/            # Karma verification endpoints
└── tests/
    └── services/
        ├── test_health.py
        ├── test_vision.py
        └── test_verification.py
```

---

## Tests

```bash
# Unit tests (no Ollama needed)
python -m pytest -m "not live"

# Live integration test (requires Ollama)
python -m pytest -m live -s
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_API_BASE` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `gemma4:e4b` | Model name |
| `APP_PORT` | `8000` | Server port |
| `DEBUG` | `false` | Enable debug mode |
| `CORS_ORIGINS` | `["*"]` | Allowed CORS origins |
