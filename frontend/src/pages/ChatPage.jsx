import {
  useEffect,
  useRef,
  useState,
} from "react";

import Sidebar from
  "../components/Sidebar";

import ChatWindow from
  "../components/ChatWindow";

import {
  deleteConversation,
  getConversation,
  getConversations,
  regenerateMessage,
  streamMessage,
} from "../services/api";


export default function ChatPage() {

  const [
    conversations,
    setConversations,
  ] = useState([]);


  const [
    conversationId,
    setConversationId,
  ] = useState(null);


  const [
    messages,
    setMessages,
  ] = useState([]);


  const [
    loading,
    setLoading,
  ] = useState(false);


  const controllerRef =
    useRef(null);


  const loadConversations =
    async () => {

      try {

        const data =
          await getConversations();

        setConversations(
          data
        );

      } catch (error) {

        console.error(
          "Conversation list error:",
          error
        );

      }

    };


  useEffect(() => {

    loadConversations();

  }, []);


  const appendToken =
    (token) => {

      setMessages(
        (previous) => {

          const updated =
            [...previous];


          const index =
            updated.length - 1;


          if (
            index >= 0 &&
            updated[index]
              .role ===
                "assistant"
          ) {

            updated[index] = {
              ...updated[index],

              content:
                updated[index]
                  .content +
                token,
            };

          }


          return updated;

        }
      );

    };


  const removeEmptyAssistant =
    () => {

      setMessages(
        (previous) => {

          const updated =
            [...previous];


          const last =
            updated[
              updated.length - 1
            ];


          if (
            last?.role ===
              "assistant" &&
            !last.content
              .trim()
          ) {

            return updated.slice(
              0,
              -1
            );

          }


          return updated;

        }
      );

    };


  const handleSend =
    async (message) => {

      if (
        !message.trim() ||
        loading
      ) {
        return;
      }


      setMessages(
        (previous) => [
          ...previous,

          {
            role: "user",
            content: message,
          },

          {
            role:
              "assistant",

            content: "",
          },
        ]
      );


      setLoading(true);


      const controller =
        new AbortController();


      controllerRef.current =
        controller;


      try {

        await streamMessage({

          message,

          conversationId,

          signal:
            controller.signal,


          onConversationId:
            (newId) => {

              setConversationId(
                newId
              );

            },


          onToken:
            appendToken,


          onDone:
            () => {

              loadConversations();

            },


          onAbort:
            () => {

              removeEmptyAssistant();

              loadConversations();

            },


          onError:
            () => {

              setMessages(
                (previous) => {

                  const updated =
                    [...previous];


                  const index =
                    updated.length - 1;


                  if (
                    index >= 0
                  ) {

                    updated[index] = {
                      role:
                        "assistant",

                      content:
                        "Sorry, something went wrong while generating the response.",
                    };

                  }


                  return updated;

                }
              );

            },

        });

      } catch (error) {

        console.error(
          "Chat stream failed:",
          error
        );

      } finally {

        if (
          controllerRef.current ===
          controller
        ) {

          controllerRef.current =
            null;

        }


        setLoading(false);

      }

    };


  const handleStop = () => {

    if (
      controllerRef.current
    ) {

      controllerRef.current
        .abort();

    }

  };


  const handleRegenerate =
    async () => {

      if (
        !conversationId ||
        loading
      ) {
        return;
      }


      let assistantIndex = -1;


      for (
        let index =
          messages.length - 1;

        index >= 0;

        index--
      ) {

        if (
          messages[index]
            .role ===
              "assistant"
        ) {

          assistantIndex =
            index;

          break;

        }

      }


      if (
        assistantIndex === -1
      ) {
        return;
      }


      const originalResponse =
        messages[
          assistantIndex
        ].content;


      setMessages(
        (previous) => {

          const updated =
            [...previous];


          updated[
            assistantIndex
          ] = {

            ...updated[
              assistantIndex
            ],

            content: "",

          };


          return updated;

        }
      );


      setLoading(true);


      const controller =
        new AbortController();


      controllerRef.current =
        controller;


      try {

        await regenerateMessage({

          conversationId,

          signal:
            controller.signal,


          onToken:
            appendToken,


          onDone:
            () => {

              loadConversations();

            },


          onAbort:
            () => {

              setMessages(
                (previous) => {

                  const updated =
                    [...previous];


                  const index =
                    updated.length - 1;


                  if (
                    index >= 0 &&
                    updated[index]
                      .role ===
                        "assistant"
                  ) {

                    updated[index] = {

                      ...updated[index],

                      content:
                        originalResponse,

                    };

                  }


                  return updated;

                }
              );

            },


          onError:
            () => {

              setMessages(
                (previous) => {

                  const updated =
                    [...previous];


                  const index =
                    updated.length - 1;


                  if (
                    index >= 0
                  ) {

                    updated[index] = {

                      role:
                        "assistant",

                      content:
                        originalResponse,

                    };

                  }


                  return updated;

                }
              );

            },

        });

      } catch (error) {

        console.error(
          "Regenerate failed:",
          error
        );

      } finally {

        if (
          controllerRef.current ===
          controller
        ) {

          controllerRef.current =
            null;

        }


        setLoading(false);

      }

    };


  const handleNewChat = () => {

    if (loading) {
      return;
    }

    setConversationId(null);

    setMessages([]);

  };


  const handleSelectConversation =
    async (id) => {

      if (loading) {
        return;
      }


      try {

        const data =
          await getConversation(
            id
          );


        setConversationId(id);

        setMessages(
          data.messages || []
        );

      } catch (error) {

        console.error(
          "Conversation load failed:",
          error
        );

      }

    };


  const handleDeleteConversation =
    async (id) => {

      if (loading) {
        return;
      }


      try {

        await deleteConversation(
          id
        );


        if (
          conversationId ===
          id
        ) {

          setConversationId(
            null
          );

          setMessages([]);

        }


        await loadConversations();

      } catch (error) {

        console.error(
          "Delete conversation failed:",
          error
        );

      }

    };


  return (
    <div className="app-shell">

      <Sidebar
        conversations={
          conversations
        }

        selectedConversationId={
          conversationId
        }

        onNewChat={
          handleNewChat
        }

        onSelectConversation={
          handleSelectConversation
        }

        onDeleteConversation={
          handleDeleteConversation
        }
      />


      <ChatWindow
        messages={messages}

        onSend={
          handleSend
        }

        onStop={
          handleStop
        }

        onRegenerate={
          handleRegenerate
        }

        loading={
          loading
        }
      />

    </div>
  );
}