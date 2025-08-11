
// frontend/src/components/UploadForm.jsx
import React, { useState } from "react";

export default function UploadForm({ onResult }) {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    if (!file) return;
    setStatus("Uploading...");
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await fetch("/upload", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Upload failed");
      onResult(data);
      setStatus("Done");
    } catch (err) {
      setStatus("Error: " + err.message);
    }
  };

  return (
    <form onSubmit={submit}>
      <input type="file" accept=".zip" onChange={e => setFile(e.target.files[0])} />
      <button type="submit">Upload</button>
      <div>{status}</div>
    </form>
  );
}
