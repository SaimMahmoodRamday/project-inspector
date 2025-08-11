
// frontend/src/components/ReportView.jsx
import React from "react";

export default function ReportView({ report }) {
  return (
    <div>
      <h2>Project Report</h2>
      <div dangerouslySetInnerHTML={{ __html: report.html }} />
      {report.call_graph && <img src={`/static/${report.call_graph}`} alt="call graph" />}
    </div>
  );
}
