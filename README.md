# Chatbot-AI

Professional full-stack conversational AI chatbot scaffold.

## Stack
- Backend: Python + FastAPI
- AI: OpenAI API
- Chat database: MongoDB
- Authentication database: PostgreSQL
- Frontend: React + Vite
- Frontend deployment: Vercel
- Backend deployment: Railway

## Build order
1. Backend health check
2. MongoDB connection
3. Text chat + persistence
4. Conversation history
5. React Claude-style UI
6. Streaming responses
7. PostgreSQL + JWT authentication
8. Image support
9. Voice support
10. Deployment

## Backend
```powershell
cd backend
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs

## Frontend
```powershell
cd frontend
npm install
npm run dev
```
Open the Vite URL, normally http://localhost:5173
