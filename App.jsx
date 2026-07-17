import React, { useEffect, useState, useCallback } from "react";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import { sendMessage, fetchConversations, fetchConversation, deleteConversation } from "./api";

export default function App() {
  const [conversations, setConversations] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [error, setError] = useState(null);

  const loadConversations = useCallback(async () => {
    try {
      const data = await fetchConversations();
      setConversations(data);
    } catch (e) {
      setError(e.message);
    }
  }, []);

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  const handleSelect = async (id) => {
    try {
      const convo = await fetchConversation(id);
      setActiveId(id);
      setMessages(convo.messages);
      setSidebarOpen(false);
    } catch (e) {
      setError(e.message);
    }
  };

  const handleNewChat = () => {
    setActiveId(null);
    setMessages([]);
    setSidebarOpen(false);
  };

  const handleDelete = async (id) => {
    try {
      await deleteConversation(id);
      if (id === activeId) handleNewChat();
      loadConversations();
    } catch (e) {
      setError(e.message);
    }
  };

  const handleSend = async (text) => {
    setError(null);
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setIsLoading(true);
    try {
      const res = await sendMessage(activeId, text);
      setActiveId(res.conversation_id);
      setMessages((prev) => [...prev, { role: "assistant", content: res.reply }]);
      loadConversations();
    } catch (e) {
      setError(e.message);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, something went wrong. Please try again." },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <Sidebar
        conversations={conversations}
        activeId={activeId}
        onSelect={handleSelect}
        onNewChat={handleNewChat}
        onDelete={handleDelete}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />
      <ChatWindow
        messages={messages}
        onSend={handleSend}
        isLoading={isLoading}
        onToggleSidebar={() => setSidebarOpen((o) => !o)}
      />
      {error && <div className="error-toast">{error}</div>}
    </div>
  );
}