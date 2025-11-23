
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

// New 02

// // frontend/src/components/ReportView.jsx
// import React from "react";
// import FileTree from "./FileTree"; // Import the new component
// // import "./ReportView.css"; // (Optional) Add some CSS for better styling

// export default function ReportView({ report }) {

//   console.log("🔥 ReportView mounted! Report =", report);
//   console.log("call_graph:", report.call_graph);
  
//   return (
//     <div className="report-container">
//       <h1>Project Report</h1>
//       <div className="report-section">
//         <h2>File Tree</h2>
//         {report.file_tree && <FileTree fileTree={report.file_tree} />}
//       </div>
      
//       <div className="report-section">
//         <div dangerouslySetInnerHTML={{ __html: report.html }} />
//       </div>

//       {report.call_graph && (
//         <div className="report-section">
//           <h2>Call Graph</h2>
//           <img src={`/static/${report.call_graph}`} alt="call graph" />
//         </div>
//       )}
//     </div>
//   );
// }

// New 03

import React from "react";
import FileTree from "./FileTree";

export default function ReportView({ report }) {
  return (
    <div className="space-y-6">
      {/* File Tree */}
      {report.file_tree && (
        <div className="bg-white/90 backdrop-blur-md p-6 rounded-xl shadow-md hover:shadow-lg transition">
  <h2 className="text-xl font-semibold mb-3 flex items-center gap-2">
    <span>📄</span> File Tree
  </h2>
  <FileTree fileTree={report.file_tree} />
</div>

      )}

      {/* HTML Report */}
      {report.html && (
        <div className="bg-white p-6 rounded shadow">
          <h2 className="text-xl font-semibold mb-3">Summary</h2>
          <div dangerouslySetInnerHTML={{ __html: report.html }} />
        </div>
      )}

      {/* Call Graph */}
      {report.call_graph && (
        <div className="bg-white p-6 rounded shadow">
          <h2 className="text-xl font-semibold mb-3">Call Graph</h2>
          <img src={`/static/${report.call_graph}`} alt="Call Graph" className="w-full border rounded" />
        </div>
      )}
    </div>
  );
}
