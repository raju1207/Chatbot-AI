import axios from "axios";


const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://localhost:8000";


const api = axios.create({
  baseURL: API_BASE_URL,

  headers: {
    "Content-Type":
      "application/json",
  },
});


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


const consumeStream =
  async ({
    url,
    body,
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
          `${API_BASE_URL}${url}`,
          {
            method: "POST",

            signal,

            headers: {
              "Content-Type":
                "application/json",
            },

            body:
              JSON.stringify(
                body
              ),
          }
        );


      if (!response.ok) {

        const errorText =
          await response.text();

        throw new Error(
          errorText ||
          `HTTP ${response.status}`
        );
      }


      if (!response.body) {

        throw new Error(
          "Streaming response is unavailable."
        );
      }


      const reader =
        response.body.getReader();


      const decoder =
        new TextDecoder();


      let buffer = "";


      const processLine =
        (line) => {

          if (!line.trim()) {
            return;
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

        };


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


        for (
          const line
          of lines
        ) {

          processLine(line);

        }

      }


      if (buffer.trim()) {
        processLine(buffer);
      }


    } catch (error) {

      if (
        error.name ===
        "AbortError"
      ) {

        console.log(
          "Generation stopped."
        );

        onAbort?.();

        return;
      }


      console.error(
        "Streaming request failed:",
        error
      );


      onError?.(error);

      throw error;
    }

  };


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

    return consumeStream({

      url:
        "/api/chat/stream",

      body: {
        conversation_id:
          conversationId,

        message,
      },

      signal,
      onConversationId,
      onToken,
      onDone,
      onAbort,
      onError,

    });

  };


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

    return consumeStream({

      url:
        "/api/chat/regenerate/stream",

      body: {
        conversation_id:
          conversationId,
      },

      signal,
      onConversationId,
      onToken,
      onDone,
      onAbort,
      onError,

    });

  };


export default api;