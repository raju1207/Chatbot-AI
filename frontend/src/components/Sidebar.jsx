import {
  MessageSquare,
  Plus,
  Trash2,
  Sparkles,
} from "lucide-react";


export default function Sidebar({
  conversations = [],
  selectedConversationId,
  onNewChat,
  onSelectConversation,
  onDeleteConversation,
}) {
  return (
    <aside className="sidebar">

      <div className="sidebar-brand">
        <div className="brand-icon">
          <Sparkles size={18} />
        </div>

        <span>Chatbot AI</span>
      </div>


      <button
        className="new-chat-button"
        onClick={onNewChat}
      >
        <Plus size={17} />
        <span>New chat</span>
      </button>


      <div className="sidebar-section-title">
        Recent
      </div>


      <div className="conversation-list">

        {conversations.length === 0 ? (
          <div className="empty-history">
            No conversations yet
          </div>
        ) : (
          conversations.map((conversation) => {

            const isActive =
              selectedConversationId ===
              conversation.conversation_id;

            return (
              <div
                key={conversation.conversation_id}
                className={
                  isActive
                    ? "conversation-item active"
                    : "conversation-item"
                }
              >

                <button
                  className="conversation-main"
                  onClick={() =>
                    onSelectConversation(
                      conversation.conversation_id
                    )
                  }
                >
                  <MessageSquare size={15} />

                  <span>
                    {conversation.title ||
                      "New Chat"}
                  </span>
                </button>


                <button
                  className="conversation-delete"
                  onClick={(event) => {
                    event.stopPropagation();

                    onDeleteConversation(
                      conversation.conversation_id
                    );
                  }}
                  title="Delete conversation"
                >
                  <Trash2 size={14} />
                </button>

              </div>
            );
          })
        )}

      </div>


      <div className="sidebar-footer">
        <div className="avatar">
          AI
        </div>

        <div>
          <div className="sidebar-footer-name">
            Local Assistant
          </div>

          <div className="sidebar-footer-model">
            Llama 3.2
          </div>
        </div>
      </div>

    </aside>
  );
}