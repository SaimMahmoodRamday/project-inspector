
// // frontend/src/components/ReportView.jsx
// import React from "react";

// export default function ReportView({ report }) {
//   return (
//     <div>
//       <h2>Project Report</h2>
//       <div dangerouslySetInnerHTML={{ __html: report.html }} />
//       {report.call_graph && <img src={`/static/${report.call_graph}`} alt="call graph" />}
//     </div>
//   );
// }

// frontend/src/components/ReportView.jsx
import React from "react";
import FileTree from "./FileTree"; // Import the new component
// import "./ReportView.css"; // (Optional) Add some CSS for better styling

export default function ReportView({ report }) {

  console.log("🔥 ReportView mounted! Report =", report);
  console.log("call_graph:", report.call_graph);
  
  return (
    <div className="report-container">
      <h1>Project Report</h1>
      <div className="report-section">
        <h2>File Tree</h2>
        {report.file_tree && <FileTree fileTree={report.file_tree} />}
      </div>
      
      <div className="report-section">
        <div dangerouslySetInnerHTML={{ __html: report.html }} />
      </div>

      {report.call_graph && (
        <div className="report-section">
          <h2>Call Graph</h2>
          <img src={`/static/${report.call_graph}`} alt="call graph" />
        </div>
      )}
    </div>
  );
}