import {
  Sparkles,
  ChevronDown,
} from "lucide-react";

import MessageBubble from "./MessageBubble";
import ChatInput from "./ChatInput";


export default function ChatWindow({
  messages,
  onSend,
  loading,
}) {
  return (
    <main className="chat-window">

      <header className="chat-header">

        <div className="chat-header-title">
          Chatbot AI
        </div>


        <button className="model-selector">
          Llama 3.2
          <ChevronDown size={14} />
        </button>

      </header>


      <section className="messages-area">

        {messages.length === 0 ? (

          <div className="welcome-screen">

            <div className="welcome-logo">
              <Sparkles size={26} />
            </div>


            <h1>
              How can I help you today?
            </h1>


            <p>
              Ask questions, learn something
              new, write code, or explore
              your ideas.
            </p>


            <div className="suggestion-grid">

              <button
                onClick={() =>
                  onSend(
                    "Explain machine learning in simple words."
                  )
                }
              >
                <strong>
                  Learn something
                </strong>

                <span>
                  Explain machine learning
                  simply
                </span>
              </button>


              <button
                onClick={() =>
                  onSend(
                    "Give me a Python coding interview question."
                  )
                }
              >
                <strong>
                  Practice coding
                </strong>

                <span>
                  Python interview question
                </span>
              </button>


              <button
                onClick={() =>
                  onSend(
                    "Help me prepare for an AI engineer interview."
                  )
                }
              >
                <strong>
                  Interview prep
                </strong>

                <span>
                  AI Engineer preparation
                </span>
              </button>

            </div>

          </div>

        ) : (

          <div className="messages-container">

            {messages.map(
              (message, index) => (
                <MessageBubble
                  key={`${message.role}-${index}`}
                  role={message.role}
                  content={message.content}
                />
              )
            )}


            {loading && (

              <div className="thinking-row">

                <div className="message-avatar">
                  <Sparkles size={18} />
                </div>


                <div>
                  <div className="message-name">
                    Chatbot AI
                  </div>

                  <div className="thinking-animation">
                    <span />
                    <span />
                    <span />
                  </div>
                </div>

              </div>

            )}

          </div>

        )}

      </section>


      <ChatInput
        onSend={onSend}
        loading={loading}
      />

    </main>
  );
}