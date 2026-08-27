import { useEffect, useState } from "react";

import Sidebar from "../components/Sidebar";
import ChatWindow from "../components/ChatWindow";

import {
  sendMessage,
  getConversations,
  getConversation,
  deleteConversation,
} from "../services/api";


export default function ChatPage() {
  const [conversations, setConversations] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);


  const loadConversations = async () => {
    try {
      const data = await getConversations();
      setConversations(data);
    } catch (error) {
      console.error("Conversation list error:", error);
    }
  };


  useEffect(() => {
    loadConversations();
  }, []);


  const handleSend = async (message) => {
    if (!message.trim() || loading) {
      return;
    }

    const userMessage = {
      role: "user",
      content: message,
    };

    setMessages((previous) => [
      ...previous,
      userMessage,
    ]);

    setLoading(true);

    try {
      console.log("Sending message:", message);

      const result = await sendMessage(
        message,
        conversationId
      );

      console.log("Backend response:", result);

      setConversationId(
        result.conversation_id
      );

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: result.response,
        },
      ]);

      // Do not block the chat UI while refreshing history.
      loadConversations();

    } catch (error) {
      console.error("Chat request failed:", error);

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            "Unable to connect to the chatbot backend. Please try again.",
        },
      ]);

    } finally {
      setLoading(false);
    }
  };


  const handleNewChat = () => {
    setConversationId(null);
    setMessages([]);
  };


  const handleSelectConversation = async (id) => {
    try {
      const data = await getConversation(id);

      setConversationId(id);
      setMessages(data.messages || []);

    } catch (error) {
      console.error(
        "Failed to load conversation:",
        error
      );
    }
  };


  const handleDeleteConversation = async (id) => {
    try {
      await deleteConversation(id);

      if (conversationId === id) {
        handleNewChat();
      }

      loadConversations();

    } catch (error) {
      console.error(
        "Failed to delete conversation:",
        error
      );
    }
  };


  return (
    <div className="app-shell">

      <Sidebar
        conversations={conversations}
        selectedConversationId={conversationId}
        onNewChat={handleNewChat}
        onSelectConversation={
          handleSelectConversation
        }
        onDeleteConversation={
          handleDeleteConversation
        }
      />

      <ChatWindow
        messages={messages}
        onSend={handleSend}
        loading={loading}
      />

    </div>
  );
}