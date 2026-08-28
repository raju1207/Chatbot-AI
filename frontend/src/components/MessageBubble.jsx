import {
  useState,
} from "react";

import ReactMarkdown from
  "react-markdown";

import remarkGfm from
  "remark-gfm";

import {
  Bot,
  User,
  Copy,
  Check,
  RotateCcw,
} from "lucide-react";


export default function MessageBubble({
  role,
  content,
  isLastAssistant,
  onRegenerate,
  loading,
}) {

  const [
    copied,
    setCopied,
  ] = useState(false);


  const isAssistant =
    role === "assistant";


  const handleCopy =
    async () => {

      try {

        await navigator.clipboard
          .writeText(content);

        setCopied(true);


        setTimeout(
          () => {
            setCopied(false);
          },
          1500
        );

      } catch (error) {

        console.error(
          "Copy failed:",
          error
        );

      }

    };


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
            remarkPlugins={[
              remarkGfm
            ]}
          >
            {content}
          </ReactMarkdown>

        </div>


        {isAssistant &&
         content && (

          <div className="message-actions">

            <button
              className="message-action-button"
              onClick={handleCopy}
              title="Copy response"
            >

              {copied ? (
                <Check size={15} />
              ) : (
                <Copy size={15} />
              )}

              <span>
                {copied
                  ? "Copied"
                  : "Copy"}
              </span>

            </button>


            {isLastAssistant && (

              <button
                className="message-action-button"
                onClick={
                  onRegenerate
                }
                disabled={
                  loading
                }
                title="Regenerate response"
              >

                <RotateCcw
                  size={15}
                />

                <span>
                  Regenerate
                </span>

              </button>

            )}

          </div>

        )}

      </div>

    </div>
  );
}