import React, { useState } from "react";
import UploadForm from "./components/UploadForm";
import ReportView from "./components/ReportView";

export default function App() {
  const [report, setReport] = useState(null);
  console.log("APP: report =", report);

  return (
    <div>
      <h1>Project Inspector</h1>
      <UploadForm onResult={setReport} />
      {report && <ReportView report={report} />}
    </div>
  );
}
