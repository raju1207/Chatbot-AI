# 🤖 Chatbot AI

A full-stack conversational AI assistant inspired by modern AI chat applications such as ChatGPT and Claude.

Chatbot AI supports real-time AI streaming, private user conversations, image understanding, voice input, conversation history, JWT authentication, and responsive desktop/mobile interfaces.

The application supports two AI environments:

- **Production:** Google Gemini
- **Local Development:** Ollama with Llama 3.2 and Gemma 3

---

## 🌐 Live Demo

🔗 https://chatbot-ai-alpha-pearl.vercel.app/

---

## 📌 Project Overview

Chatbot AI is a production-ready full-stack AI chatbot built using:

- React + Vite
- FastAPI
- MongoDB Atlas
- Google Gemini
- Ollama
- JWT Authentication
- Vercel

The application allows users to create accounts, maintain private conversation history, communicate with an AI assistant in real time, upload images for AI analysis, use voice input, regenerate responses, and manage conversations.

---

# ✨ Key Features

## 🔐 Authentication

- User registration
- User login
- JWT authentication
- Persistent login session
- Logout functionality
- User-specific private conversations
- Protected API routes

Each user can access only their own conversations.

---

## 💬 AI Chat

- Real-time streaming responses
- Multi-turn conversation memory
- Markdown rendering
- Code block support
- Conversation history
- New chat creation
- Delete conversations
- Stop AI generation
- Regenerate AI responses
- Copy AI responses

---

## 🧠 Conversation Memory

Conversation history is stored in MongoDB Atlas.

The backend retrieves recent conversation messages and sends them to the AI model so the assistant can understand previous context.

Example:

```text
User:
Remember this word: Mango123

AI:
Sure.

User:
What word did I ask you to remember?

AI:
Mango123