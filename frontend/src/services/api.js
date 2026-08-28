import axios from "axios";


const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://localhost:8000";


const TOKEN_KEY =
  "chatbot_access_token";


/* =========================================
   TOKEN HELPERS
========================================= */

export const getAccessToken = () => {
  return localStorage.getItem(
    TOKEN_KEY
  );
};


export const setAccessToken = (
  token
) => {
  localStorage.setItem(
    TOKEN_KEY,
    token
  );
};


export const clearAccessToken =
  () => {
    localStorage.removeItem(
      TOKEN_KEY
    );
  };


/* =========================================
   AXIOS INSTANCE
========================================= */

const api = axios.create({
  baseURL: API_BASE_URL,

  headers: {
    "Content-Type":
      "application/json",
  },
});


/* =========================================
   AUTOMATIC JWT HEADER
========================================= */

api.interceptors.request.use(
  (config) => {
    const token =
      getAccessToken();

    if (token) {
      config.headers.Authorization =
        `Bearer ${token}`;
    }

    return config;
  },

  (error) =>
    Promise.reject(error)
);


/* =========================================
   AUTH API
========================================= */

export const registerUser =
  async ({
    name,
    email,
    password,
  }) => {
    const response =
      await api.post(
        "/api/auth/register",
        {
          name,
          email,
          password,
        }
      );

    return response.data;
  };


export const loginUser =
  async ({
    email,
    password,
  }) => {
    const response =
      await api.post(
        "/api/auth/login",
        {
          email,
          password,
        }
      );

    return response.data;
  };


export const getCurrentUser =
  async () => {
    const response =
      await api.get(
        "/api/auth/me"
      );

    return response.data;
  };


export const logoutUser =
  async () => {
    const response =
      await api.post(
        "/api/auth/logout"
      );

    return response.data;
  };


/* =========================================
   CONVERSATIONS
========================================= */

export const getConversations =
  async () => {
    const response =
      await api.get(
        "/api/conversations"
      );

    return response.data;
  };


export const getConversation =
  async (conversationId) => {
    const response =
      await api.get(
        `/api/conversations/${conversationId}`
      );

    return response.data;
  };


export const deleteConversation =
  async (conversationId) => {
    const response =
      await api.delete(
        `/api/conversations/${conversationId}`
      );

    return response.data;
  };


/* =========================================
   FETCH AUTH HEADER
========================================= */

const getFetchAuthHeaders =
  () => {
    const token =
      getAccessToken();

    if (!token) {
      return {};
    }

    return {
      Authorization:
        `Bearer ${token}`,
    };
  };


/* =========================================
   STREAM PROCESSOR
========================================= */

const processStream =
  async ({
    response,
    onConversationId,
    onToken,
    onDone,
  }) => {
    if (!response.body) {
      throw new Error(
        "Streaming response unavailable."
      );
    }

    const reader =
      response.body.getReader();

    const decoder =
      new TextDecoder();

    let buffer = "";

    while (true) {
      const {
        value,
        done,
      } = await reader.read();

      if (done) {
        break;
      }

      buffer += decoder.decode(
        value,
        {
          stream: true,
        }
      );

      const lines =
        buffer.split("\n");

      buffer =
        lines.pop() || "";

      for (const line of lines) {
        if (!line.trim()) {
          continue;
        }

        const data =
          JSON.parse(line);

        if (
          data.type === "meta"
        ) {
          onConversationId?.(
            data.conversation_id
          );
        }

        if (
          data.type === "delta"
        ) {
          onToken?.(
            data.content
          );
        }

        if (
          data.type === "done"
        ) {
          onDone?.();
        }

        if (
          data.type === "error"
        ) {
          throw new Error(
            data.message
          );
        }
      }
    }
  };


/* =========================================
   TEXT STREAM
========================================= */

export const streamMessage =
  async ({
    message,
    conversationId,
    signal,
    onConversationId,
    onToken,
    onDone,
    onAbort,
    onError,
  }) => {
    try {
      const response =
        await fetch(
          `${API_BASE_URL}/api/chat/stream`,
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json",

              ...getFetchAuthHeaders(),
            },

            body:
              JSON.stringify({
                conversation_id:
                  conversationId,

                message,
              }),

            signal,
          }
        );

      if (!response.ok) {
        const text =
          await response.text();

        throw new Error(
          text ||
          `HTTP ${response.status}`
        );
      }

      await processStream({
        response,
        onConversationId,
        onToken,
        onDone,
      });

    } catch (error) {
      if (
        error.name ===
        "AbortError"
      ) {
        onAbort?.();
        return;
      }

      console.error(
        "Streaming error:",
        error
      );

      onError?.(error);

      throw error;
    }
  };


/* =========================================
   REGENERATE STREAM
========================================= */

export const regenerateMessage =
  async ({
    conversationId,
    signal,
    onConversationId,
    onToken,
    onDone,
    onAbort,
    onError,
  }) => {
    try {
      const response =
        await fetch(
          `${API_BASE_URL}/api/chat/regenerate/stream`,
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json",

              ...getFetchAuthHeaders(),
            },

            body:
              JSON.stringify({
                conversation_id:
                  conversationId,
              }),

            signal,
          }
        );

      if (!response.ok) {
        const text =
          await response.text();

        throw new Error(
          text ||
          `HTTP ${response.status}`
        );
      }

      await processStream({
        response,
        onConversationId,
        onToken,
        onDone,
      });

    } catch (error) {
      if (
        error.name ===
        "AbortError"
      ) {
        onAbort?.();
        return;
      }

      console.error(
        "Regenerate error:",
        error
      );

      onError?.(error);

      throw error;
    }
  };


/* =========================================
   IMAGE STREAM
========================================= */

export const streamImageMessage =
  async ({
    message,
    image,
    conversationId,
    signal,
    onConversationId,
    onToken,
    onDone,
    onAbort,
    onError,
  }) => {
    try {
      const formData =
        new FormData();

      formData.append(
        "message",
        message
      );

      if (conversationId) {
        formData.append(
          "conversation_id",
          conversationId
        );
      }

      formData.append(
        "image",
        image
      );

      const response =
        await fetch(
          `${API_BASE_URL}/api/chat/image/stream`,
          {
            method: "POST",

            headers: {
              ...getFetchAuthHeaders(),
            },

            body: formData,

            signal,
          }
        );

      if (!response.ok) {
        const text =
          await response.text();

        throw new Error(
          text ||
          `HTTP ${response.status}`
        );
      }

      await processStream({
        response,
        onConversationId,
        onToken,
        onDone,
      });

    } catch (error) {
      if (
        error.name ===
        "AbortError"
      ) {
        onAbort?.();
        return;
      }

      console.error(
        "Image streaming error:",
        error
      );

      onError?.(error);

      throw error;
    }
  };


export default api;