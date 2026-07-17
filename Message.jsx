import React from "react";

export default function Message({ role, content }) {
  const isUser = role === "user";
  return (
    <div className={`message-row ${isUser ? "user-row" : "assistant-row"}`}>
      <div className={`avatar ${isUser ? "user-avatar" : "assistant-avatar"}`}>
        {isUser ? "U" : "AI"}
      </div>
      <div className={`message-bubble ${isUser ? "user-bubble" : "assistant-bubble"}`}>
        {content}
      </div>
    </div>
  );
}