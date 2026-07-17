# AI Chatbot — FastAPI + MongoDB + React + OpenAI

A ChatGPT-style chatbot: React frontend, Python (FastAPI) backend, MongoDB
for conversation storage, OpenAI API for the actual language model.

## Architecture

```
React (UI, port 3000)
    │  fetch() calls
    ▼
FastAPI (API, port 8000)
    │             │
    ▼             ▼
MongoDB      OpenAI API
(history)    (generates replies)
```

## Folder structure

```
chatbot-project/
├── backend/
│   ├── main.py           # FastAPI app + routes
│   ├── database.py       # MongoDB connection
│   ├── models.py         # Request/response schemas
│   ├── chat_service.py   # Context building + OpenAI call
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── package.json
    ├── public/index.html
    └── src/
        ├── App.jsx
        ├── App.css
        ├── index.js
        ├── api.js
        └── components/
            ├── Sidebar.jsx
            ├── ChatWindow.jsx
            └── Message.jsx
```

## Step 1 — Install MongoDB

Easiest is a free MongoDB Atlas cluster (no local install needed):
1. Go to mongodb.com/cloud/atlas, create a free (M0) cluster.
2. Get your connection string (looks like `mongodb+srv://user:pass@cluster.mongodb.net`).

Or run it locally with Docker:
```bash
docker run -d -p 27017:27017 --name mongo mongo:7
```

## Step 2 — Get an OpenAI API key

Sign up at platform.openai.com, go to API Keys, create one. You'll need
billing enabled (even the cheap `gpt-4o-mini` model requires a funded account).

## Step 3 — Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# now edit .env and paste in your OPENAI_API_KEY and MONGO_URI
```

Run the server:
```bash
uvicorn main:app --reload --port 8000
```

Visit http://localhost:8000/docs — this is FastAPI's auto-generated
interactive API tester. Try the `/api/chat` endpoint there first to confirm
OpenAI + MongoDB are both wired up correctly before touching the frontend.

## Step 4 — Frontend setup

```bash
cd frontend
npm install
npm start
```

This opens http://localhost:3000 automatically. Start chatting — messages
flow to FastAPI, which pulls conversation history from MongoDB, sends it
to OpenAI, saves the reply, and returns it to React.

## Step 5 — How context-aware conversation works

- Every message (user + assistant) is saved in MongoDB tied to a `conversation_id`.
- On each new message, `chat_service.py` pulls the last 20 messages of that
  conversation and sends them all to OpenAI as context, so the model
  "remembers" what was said earlier — exactly how ChatGPT keeps a thread coherent.
- `MAX_HISTORY_MESSAGES` in `chat_service.py` controls how far back it looks.
  Raise it for longer memory (costs more tokens per request), lower it for
  speed/cost savings.

## Step 6 — Deploying to production (scalability notes)

- **Backend**: deploy on Render, Railway, Fly.io, or an AWS/GCP VM behind
  a process manager (gunicorn + uvicorn workers). FastAPI is async, so a
  single instance already handles many concurrent chats efficiently.
- **Database**: use MongoDB Atlas in production (managed, auto-scaling,
  automatic backups) rather than self-hosting.
- **Frontend**: `npm run build` produces a static bundle — deploy it to
  Vercel, Netlify, or S3 + CloudFront.
- **Scaling further**:
  - Add Redis caching for frequent lookups.
  - Add rate-limiting middleware (e.g. `slowapi`) to protect your OpenAI budget.
  - Switch to OpenAI's streaming API (`stream=True`) so replies appear
    token-by-token instead of all at once — feels much faster to users.
  - Put FastAPI behind a load balancer and run multiple uvicorn workers
    (`uvicorn main:app --workers 4`) once traffic grows.

## Common issues

| Symptom | Fix |
|---|---|
| CORS error in browser console | Check `FRONTEND_ORIGIN` in `.env` matches your React URL exactly |
| "AI service is temporarily unavailable" | Check your OpenAI API key and billing status |
| Conversations don't persist | Confirm `MONGO_URI` is reachable — test with `mongosh <your-uri>` |
| Blank page on `npm start` | Delete `node_modules` and `package-lock.json`, re-run `npm install` |
