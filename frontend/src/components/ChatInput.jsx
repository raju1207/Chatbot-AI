import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

import {
  ArrowUp,
  Square,
  X,
} from "lucide-react";

import ImageUploader from "./ImageUploader";
import VoiceRecorder from "./VoiceRecorder";


export default function ChatInput({
  onSend,
  onSendImage,
  onStop,
  loading,
}) {
  const [message, setMessage] =
    useState("");

  const [image, setImage] =
    useState(null);

  const [previewUrl, setPreviewUrl] =
    useState(null);

  const textareaRef =
    useRef(null);


  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(
          previewUrl
        );
      }
    };
  }, [previewUrl]);


  const resizeTextarea = () => {
    if (!textareaRef.current) {
      return;
    }

    textareaRef.current.style.height =
      "auto";

    textareaRef.current.style.height =
      `${Math.min(
        textareaRef.current.scrollHeight,
        180
      )}px`;
  };


  const handleVoiceTranscript =
    useCallback((transcript) => {
      setMessage((previous) => {
        if (!previous.trim()) {
          return transcript;
        }

        return `${previous.trim()} ${transcript}`;
      });


      setTimeout(() => {
        resizeTextarea();
      }, 0);
    }, []);


  const handleImageSelect = (file) => {
    const allowedTypes = [
      "image/jpeg",
      "image/png",
      "image/webp",
    ];


    if (
      !allowedTypes.includes(
        file.type
      )
    ) {
      alert(
        "Only JPG, PNG and WEBP images are supported."
      );

      return;
    }


    if (
      file.size >
      10 * 1024 * 1024
    ) {
      alert(
        "Image must be smaller than 10 MB."
      );

      return;
    }


    if (previewUrl) {
      URL.revokeObjectURL(
        previewUrl
      );
    }


    setImage(file);

    setPreviewUrl(
      URL.createObjectURL(file)
    );
  };


  const removeImage = () => {
    if (previewUrl) {
      URL.revokeObjectURL(
        previewUrl
      );
    }

    setImage(null);

    setPreviewUrl(null);
  };


  const handleSubmit = () => {
    const text =
      message.trim();


    if (loading) {
      return;
    }


    if (
      !text &&
      !image
    ) {
      return;
    }


    if (image) {
      onSendImage(
        text ||
          "Please describe this image.",
        image,
        previewUrl
      );

      setImage(null);

      setPreviewUrl(null);

    } else {
      onSend(text);
    }


    setMessage("");


    if (
      textareaRef.current
    ) {
      textareaRef.current.style.height =
        "auto";
    }
  };


  const handleChange = (event) => {
    setMessage(
      event.target.value
    );

    event.target.style.height =
      "auto";

    event.target.style.height =
      `${Math.min(
        event.target.scrollHeight,
        180
      )}px`;
  };


  const handleKeyDown = (event) => {
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

        {previewUrl && (
          <div className="image-preview-container">

            <div className="image-preview">

              <img
                src={previewUrl}
                alt="Selected"
              />


              <button
                type="button"

                className="remove-image-button"

                onClick={
                  removeImage
                }

                disabled={
                  loading
                }

                title="Remove image"
              >
                <X size={14} />
              </button>

            </div>


            <div className="image-preview-name">
              {image?.name}
            </div>

          </div>
        )}


        <textarea
          ref={textareaRef}

          value={message}

          onChange={
            handleChange
          }

          onKeyDown={
            handleKeyDown
          }

          placeholder={
            image
              ? "Ask something about this image..."
              : "How can I help you today?"
          }

          rows={1}

          disabled={
            loading
          }
        />


        <div className="composer-bottom">

          <div className="composer-tools">

            <ImageUploader
              onSelect={
                handleImageSelect
              }

              disabled={
                loading
              }
            />


            <VoiceRecorder
              onTranscript={
                handleVoiceTranscript
              }

              disabled={
                loading
              }
            />

          </div>


          {loading ? (
            <button
              type="button"

              className=
                "send-button stop-button"

              onClick={
                onStop
              }

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
                !message.trim() &&
                !image
              }
            >
              <ArrowUp size={19} />
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