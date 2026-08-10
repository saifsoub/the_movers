# MiniBot 🤖

A hyper-focused chatbot that **only** knows about:

1. **Project Management** — tasks, sprints, backlogs, agile, kanban, standups, milestones, and more
2. **Making Money** — pricing, invoicing, MRR, ROI, cashflow, getting clients, retainers, and more

Anything outside these two topics? MiniBot says:
> *"That's outside what I know right now — my owner will teach me that soon."*

---

## Run locally

```bash
cd minibot
pip install -r requirements.txt
uvicorn app:app --reload
```

Open `http://localhost:8000` for API info, or `http://localhost:8000/docs` for the interactive Swagger UI.

## Run with Docker

```bash
cd minibot
docker build -t minibot .
docker run -p 8000:8000 minibot
```

## With LLM (optional)

Set `OPENAI_API_KEY` to enable GPT-powered answers for in-scope questions:

```bash
docker run -p 8000:8000 -e OPENAI_API_KEY=sk-... minibot
```

Without the key, MiniBot uses its built-in rule-based knowledge base.

## API

### `POST /chat`

```json
{ "message": "How do I price my services?" }
```

Response:
```json
{
  "reply": "Calculate your costs, research market rates...",
  "in_scope": true
}
```

Out-of-scope example:
```json
{ "message": "What is the capital of France?" }
```
```json
{
  "reply": "That's outside what I know right now — my owner will teach me that soon.",
  "in_scope": false
}
```

### `GET /health`
```json
{ "status": "ok", "topics": ["project management", "making money"] }
```

---

## Deploy to Render (free tier)

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect repo, set **Root Directory** to `minibot`
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn app:app --host 0.0.0.0 --port 10000`
6. Add `OPENAI_API_KEY` env var (optional)

## Deploy to Railway

```bash
cd minibot
railway init
railway up
```
