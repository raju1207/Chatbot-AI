import React from "react";

export default function Sidebar({
  conversations,
  activeId,
  onSelect,
  onNewChat,
  onDelete,
  isOpen,
  onClose,
}) {
  return (
    <>
      {isOpen && <div className="sidebar-overlay" onClick={onClose} />}
      <aside className={`sidebar ${isOpen ? "sidebar-open" : ""}`}>
        <button className="new-chat-btn" onClick={onNewChat}>
          + New Chat
        </button>
        <div className="conversation-list">
          {conversations.length === 0 && (
            <p className="empty-hint">No conversations yet</p>
          )}
          {conversations.map((c) => (
            <div
              key={c.id}
              className={`conversation-item ${c.id === activeId ? "active" : ""}`}
              onClick={() => onSelect(c.id)}
            >
              <span className="conversation-title">{c.title}</span>
              <button
                className="delete-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(c.id);
                }}
                aria-label="Delete conversation"
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      </aside>
    </>
  );
}