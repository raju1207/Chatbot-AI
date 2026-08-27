import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import {
  Bot,
  User,
} from "lucide-react";


export default function MessageBubble({
  role,
  content,
}) {
  const isAssistant =
    role === "assistant";

  return (
    <div
      className={`message-row ${
        isAssistant
          ? "assistant-message"
          : "user-message"
      }`}
    >

      <div className="message-avatar">

        {isAssistant ? (
          <Bot size={18} />
        ) : (
          <User size={18} />
        )}

      </div>


      <div className="message-main">

        <div className="message-name">
          {isAssistant
            ? "Chatbot AI"
            : "You"}
        </div>


        <div className="message-content">

          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
          >
            {content}
          </ReactMarkdown>

        </div>

      </div>

    </div>
  );
}