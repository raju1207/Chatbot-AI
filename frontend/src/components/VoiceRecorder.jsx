import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  Mic,
  MicOff,
} from "lucide-react";


export default function VoiceRecorder({
  onTranscript,
  disabled,
}) {
  const [listening, setListening] =
    useState(false);

  const [supported, setSupported] =
    useState(true);

  const recognitionRef =
    useRef(null);


  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition ||
      window.webkitSpeechRecognition;


    if (!SpeechRecognition) {
      setSupported(false);
      return;
    }


    const recognition =
      new SpeechRecognition();


    recognition.continuous = false;

    recognition.interimResults = true;

    recognition.lang = "en-IN";


    recognition.onstart = () => {
      setListening(true);
    };


    recognition.onend = () => {
      setListening(false);
    };


    recognition.onerror = (event) => {
      console.error(
        "Speech recognition error:",
        event.error
      );

      setListening(false);
    };


    recognition.onresult = (event) => {
      let finalTranscript = "";


      for (
        let index =
          event.resultIndex;

        index < event.results.length;

        index++
      ) {
        const result =
          event.results[index];


        if (result.isFinal) {
          finalTranscript +=
            result[0].transcript;
        }
      }


      if (finalTranscript.trim()) {
        onTranscript(
          finalTranscript.trim()
        );
      }
    };


    recognitionRef.current =
      recognition;


    return () => {
      recognition.abort();
    };
  }, [onTranscript]);


  const toggleListening = () => {
    if (
      !supported ||
      disabled
    ) {
      return;
    }


    const recognition =
      recognitionRef.current;


    if (!recognition) {
      return;
    }


    try {
      if (listening) {
        recognition.stop();
      } else {
        recognition.start();
      }
    } catch (error) {
      console.error(
        "Microphone error:",
        error
      );
    }
  };


  return (
    <button
      type="button"

      className={`tool-button ${
        listening
          ? "voice-listening"
          : ""
      }`}

      onClick={
        toggleListening
      }

      disabled={
        disabled ||
        !supported
      }

      title={
        !supported
          ? "Voice input is not supported in this browser"
          : listening
          ? "Stop listening"
          : "Start voice input"
      }
    >
      {listening ? (
        <MicOff size={19} />
      ) : (
        <Mic size={19} />
      )}
    </button>
  );
}