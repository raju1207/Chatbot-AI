import {
  MessageSquare,
  Plus,
  Sparkles,
  Trash2,
  X,
} from "lucide-react";


export default function Sidebar({
  conversations,
  selectedConversationId,
  onNewChat,
  onSelectConversation,
  onDeleteConversation,
  mobileOpen,
  onCloseMobile,
}) {

  return (
    <aside
      className={`sidebar ${
        mobileOpen
          ? "mobile-open"
          : ""
      }`}
    >

      <div className="sidebar-brand-row">

        <div className="sidebar-brand">

          <div className="brand-icon">
            <Sparkles size={17} />
          </div>

          <span>
            Chatbot AI
          </span>

        </div>


        <button
          type="button"
          className="mobile-close-button"
          onClick={
            onCloseMobile
          }
          aria-label="Close sidebar"
          title="Close sidebar"
        >
          <X size={20} />
        </button>

      </div>


      <button
        type="button"
        className="new-chat-button"
        onClick={
          onNewChat
        }
      >
        <Plus size={17} />

        <span>
          New chat
        </span>
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

          conversations.map(
            (conversation) => {

              const id =
                conversation
                  .conversation_id;

              return (
                <div
                  key={id}

                  className={`conversation-item ${
                    selectedConversationId ===
                    id
                      ? "active"
                      : ""
                  }`}
                >

                  <button
                    type="button"
                    className="conversation-main"

                    onClick={() =>
                      onSelectConversation(
                        id
                      )
                    }
                  >

                    <MessageSquare
                      size={15}
                    />

                    <span>
                      {conversation.title ||
                        "New Chat"}
                    </span>

                  </button>


                  <button
                    type="button"
                    className="conversation-delete"

                    onClick={(event) => {
                      event.stopPropagation();

                      onDeleteConversation(
                        id
                      );
                    }}

                    title="Delete conversation"

                    aria-label="Delete conversation"
                  >
                    <Trash2
                      size={15}
                    />
                  </button>

                </div>
              );
            }
          )

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