# AGENTS.md

This repository is a small full-stack chatbot app built around:
- FastAPI backend in `backend/`
- React frontend in `frontend/`
- MongoDB for chat history
- OpenAI for reply generation

## Project map
- Start with [README.md](README.md) for environment setup and architecture.
- Backend entrypoint: [backend/main.py](backend/main.py)
- AI orchestration: [backend/chat_service.py](backend/chat_service.py)
- MongoDB connection and index creation: [backend/database.py](backend/database.py)
- API schemas: [backend/models.py](backend/models.py)
- Frontend API wrapper: [frontend/src/api.js](frontend/src/api.js)
- UI components: [frontend/src/components](frontend/src/components)

## Run commands
- Backend (from the repo root): `uvicorn backend.main:app --reload --port 8000`
- Frontend (from `frontend/`): `npm install` then `npm start`
- Build frontend: `npm run build`

## Environment and secrets
- Required backend environment variables: `OPENAI_API_KEY`, `MONGO_URI`
- Optional backend envs: `DB_NAME`, `OPENAI_MODEL`, `FRONTEND_ORIGIN`
- The app expects `.env` values to exist in `backend/` when running locally.

## Key conventions
- Keep the backend and frontend separate; prefer changes that respect the existing API contract.
- Conversation history is stored in MongoDB and fetched from `backend/chat_service.py` with a `MAX_HISTORY_MESSAGES` window.
- The backend exposes REST endpoints under `/api/*`; the frontend talks to those endpoints via `frontend/src/api.js`.
- CORS is configured for `http://localhost:3000` and `http://127.0.0.1:3000`.

## Common pitfalls
- `backend/main.py` is package-style code, so run it as a module from the repo root rather than as a loose script.
- If the backend fails with an AI error, check `OPENAI_API_KEY` and OpenAI billing status before changing app logic.
- If conversations do not persist, verify MongoDB connectivity and the `MONGO_URI` value.

## Coding expectations
- Favor small, targeted changes that preserve the existing Pydantic/FastAPI and React component structure.
- Link to [README.md](README.md) for full setup details instead of duplicating setup instructions here.
- When adding new backend endpoints, keep request/response schemas aligned with [backend/models.py](backend/models.py).
