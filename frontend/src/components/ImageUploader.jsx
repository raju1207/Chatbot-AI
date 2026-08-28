import { useRef } from "react";
import { Paperclip } from "lucide-react";

export default function ImageUploader({
  onSelect,
  disabled,
}) {
  const inputRef = useRef(null);

  const handleChange = (event) => {
    const file = event.target.files?.[0];

    if (!file) return;

    onSelect(file);

    // Allows selecting the same image again later
    event.target.value = "";
  };

  return (
    <>
      <button
        type="button"
        className="tool-button"
        disabled={disabled}
        onClick={() =>
          inputRef.current?.click()
        }
        title="Upload image"
      >
        <Paperclip size={19} />
      </button>

      <input
        ref={inputRef}
        type="file"
        accept="image/png,image/jpeg,image/webp"
        onChange={handleChange}
        hidden
      />
    </>
  );
}