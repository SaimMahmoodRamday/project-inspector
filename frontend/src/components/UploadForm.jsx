
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
      setStatus("Upload complete ✅");
    } catch (err) {
      setStatus("Error: " + err.message);
    }
  };

  return (
    <form onSubmit={submit} className="flex flex-col space-y-3">
      <input
        type="file"
        accept=".zip"
        onChange={(e) => setFile(e.target.files[0])}
        className="border p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
      />
      <button
        type="submit"
        className="bg-teal-100 text-teal-800 p-6 shadow-md rounded-lg hover:bg-teal-200 transition font-semibold"
      >
        Upload
      </button>
      <div className="text-gray-700">{status}</div>
    </form>
  );
}
