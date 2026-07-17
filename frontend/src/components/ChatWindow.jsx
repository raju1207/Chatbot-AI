import React, { useEffect, useRef, useState } from "react";
import Message from "./Message";

export default function ChatWindow({ messages, onSend, isLoading, onToggleSidebar }) {
  const [input, setInput] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;
    onSend(trimmed);
    setInput("");
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <main className="chat-window">
      <header className="chat-header">
        <button className="hamburger" onClick={onToggleSidebar} aria-label="Toggle sidebar">
          ☰
        </button>
        <h1>AI Chatbot</h1>
      </header>

      <div className="messages-container">
        {messages.length === 0 && (
          <div className="welcome-screen">
            <h2>How can I help you today?</h2>
          </div>
        )}
        {messages.map((m, i) => (
          <Message key={i} role={m.role} content={m.content} />
        ))}
        {isLoading && (
          <div className="message-row assistant-row">
            <div className="avatar assistant-avatar">AI</div>
            <div className="message-bubble assistant-bubble typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <form className="input-bar" onSubmit={handleSubmit}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Message the AI assistant..."
          rows={1}
        />
        <button type="submit" disabled={isLoading || !input.trim()}>
          Send
        </button>
      </form>
    </main>
  );
}