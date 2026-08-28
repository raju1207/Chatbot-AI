import {
  LogOut,
  MessageSquare,
  Plus,
  Sparkles,
  Trash2,
  X,
} from "lucide-react";

import {
  useState,
} from "react";

import {
  useAuth,
} from "../context/AuthContext";


export default function Sidebar({
  conversations,
  selectedConversationId,
  onNewChat,
  onSelectConversation,
  onDeleteConversation,
  mobileOpen,
  onCloseMobile,
}) {
  const {
    user,
    logout,
  } = useAuth();

  const [
    loggingOut,
    setLoggingOut,
  ] = useState(false);


  /* =========================================
     USER INITIALS
  ========================================= */

  const getInitials = () => {
    if (!user?.name) {
      return "U";
    }

    const parts =
      user.name
        .trim()
        .split(/\s+/);

    if (parts.length === 1) {
      return parts[0]
        .charAt(0)
        .toUpperCase();
    }

    return (
      parts[0]
        .charAt(0) +
      parts[parts.length - 1]
        .charAt(0)
    ).toUpperCase();
  };


  /* =========================================
     LOGOUT
  ========================================= */

  const handleLogout =
    async () => {
      if (loggingOut) {
        return;
      }

      setLoggingOut(true);

      try {
        await logout();

        onCloseMobile?.();

      } catch (error) {
        console.error(
          "Logout failed:",
          error
        );

      } finally {
        setLoggingOut(false);
      }
    };


  return (
    <aside
      className={`sidebar ${
        mobileOpen
          ? "mobile-open"
          : ""
      }`}
    >

      {/* =====================================
          BRAND
      ===================================== */}

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


      {/* =====================================
          NEW CHAT
      ===================================== */}

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


      {/* =====================================
          RECENT
      ===================================== */}

      <div className="sidebar-section-title">
        Recent
      </div>


      {/* =====================================
          CONVERSATIONS
      ===================================== */}

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

                    className=
                      "conversation-main"

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

                    className=
                      "conversation-delete"

                    onClick={(event) => {
                      event.stopPropagation();

                      onDeleteConversation(
                        id
                      );
                    }}

                    title=
                      "Delete conversation"

                    aria-label=
                      "Delete conversation"
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


      {/* =====================================
          LOGGED-IN USER
      ===================================== */}

      <div className="sidebar-user-footer">

        <div className="sidebar-user-info">

          <div className="user-avatar">
            {getInitials()}
          </div>


          <div className="user-details">

            <div className="sidebar-user-name">
              {user?.name ||
                "User"}
            </div>

            <div className="sidebar-user-email">
              {user?.email ||
                ""}
            </div>

          </div>

        </div>


        <button
          type="button"

          className="logout-button"

          onClick={
            handleLogout
          }

          disabled={
            loggingOut
          }

          title="Logout"

          aria-label="Logout"
        >

          <LogOut size={18} />

        </button>

      </div>

    </aside>
  );
}