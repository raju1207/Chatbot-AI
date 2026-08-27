import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const sendMessage = async (message, conversationId = null) => {
  const response = await api.post("/api/chat", {
    conversation_id: conversationId,
    message: message,
  });

  return response.data;
};

export const getConversations = async () => {
  const response = await api.get("/api/conversations");
  return response.data;
};

export const getConversation = async (conversationId) => {
  const response = await api.get(
    `/api/conversations/${conversationId}`
  );

  return response.data;
};

export const deleteConversation = async (conversationId) => {
  const response = await api.delete(
    `/api/conversations/${conversationId}`
  );

  return response.data;
};

export default api;