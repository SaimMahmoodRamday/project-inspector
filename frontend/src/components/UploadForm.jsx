
// frontend/src/components/UploadForm.jsx

import React, { useState } from "react";

export default function UploadForm({ onResult }) {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    if (!file || isLoading) return;

    setIsLoading(true);
    setStatus("Uploading and analysing… this may take up to a minute ⏳");
    onResult(null); // clear previous report

    const formData = new FormData();
    formData.append("file", file);

    try {
      const apiUrl = import.meta.env.VITE_API_URL || "";
      const res = await fetch(`${apiUrl}/upload`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Upload failed");
      onResult(data);
      setStatus("Analysis complete ✅");
    } catch (err) {
      setStatus("Error: " + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const isError = status.startsWith("Error");

  return (
    <form onSubmit={submit} className="flex flex-col space-y-3">
      <input
        type="file"
        accept=".zip"
        disabled={isLoading}
        onChange={(e) => setFile(e.target.files[0])}
        className="border p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-400 disabled:opacity-50"
      />
      <button
        type="submit"
        disabled={isLoading || !file}
        className="bg-teal-100 text-teal-800 p-4 shadow-md rounded-lg hover:bg-teal-200 transition font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoading ? "Analysing…" : "Upload & Analyse"}
      </button>
      {status && (
        <div className={`text-sm font-medium ${isError ? "text-red-600" : "text-gray-700"}`}>
          {status}
        </div>
      )}
    </form>
  );
}
