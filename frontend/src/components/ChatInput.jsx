import {
  useRef,
  useState,
} from "react";

import {
  ArrowUp,
  Paperclip,
  Mic,
  Square,
} from "lucide-react";


export default function ChatInput({
  onSend,
  onStop,
  loading,
}) {

  const [
    message,
    setMessage,
  ] = useState("");


  const textareaRef =
    useRef(null);


  const handleSubmit = () => {

    const text =
      message.trim();


    if (
      !text ||
      loading
    ) {
      return;
    }


    onSend(text);

    setMessage("");


    if (
      textareaRef.current
    ) {

      textareaRef.current
        .style.height =
          "auto";

    }

  };


  const handleChange =
    (event) => {

      setMessage(
        event.target.value
      );


      event.target
        .style.height =
          "auto";


      event.target
        .style.height =
          `${Math.min(
            event.target
              .scrollHeight,
            180
          )}px`;

    };


  const handleKeyDown =
    (event) => {

      if (
        event.key === "Enter" &&
        !event.shiftKey
      ) {

        event.preventDefault();

        handleSubmit();

      }

    };


  return (
    <div className="composer-wrapper">

      <div className="composer">

        <textarea
          ref={textareaRef}
          value={message}
          onChange={
            handleChange
          }
          onKeyDown={
            handleKeyDown
          }
          placeholder=
            "How can I help you today?"
          rows={1}
          disabled={loading}
        />


        <div className="composer-bottom">

          <div className="composer-tools">

            <button
              type="button"
              className="tool-button"
              disabled
            >
              <Paperclip
                size={19}
              />
            </button>


            <button
              type="button"
              className="tool-button"
              disabled
            >
              <Mic size={19} />
            </button>

          </div>


          {loading ? (

            <button
              type="button"
              className=
                "send-button stop-button"
              onClick={onStop}
              title="Stop generation"
            >

              <Square
                size={14}
                fill="currentColor"
              />

            </button>

          ) : (

            <button
              type="button"
              className="send-button"
              onClick={
                handleSubmit
              }
              disabled={
                !message.trim()
              }
            >

              <ArrowUp
                size={19}
              />

            </button>

          )}

        </div>

      </div>


      <div className="input-footer">
        Chatbot AI may make mistakes.
        Verify important information.
      </div>

    </div>
  );
}