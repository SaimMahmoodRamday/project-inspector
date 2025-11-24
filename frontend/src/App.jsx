// import React, { useState } from "react";
// import UploadForm from "./components/UploadForm";
// import ReportView from "./components/ReportView";

// export default function App() {
//   const [report, setReport] = useState(null);
//   console.log("APP: report =", report);

//   return (
//     <div>
//       <h1>Project Inspector</h1>
//       <UploadForm onResult={setReport} />
//       {report && <ReportView report={report} />}
//     </div>
//   );
// }

// New 02

// import React, { useState } from "react";
// import UploadForm from "./components/UploadForm";
// import ReportView from "./components/ReportView";

// export default function App() {
//   const [report, setReport] = useState(null);

//   return (
//     <div className="min-h-screen bg-gray-50 text-gray-800 font-sans">
//       {/* Header */}
//       <header className="bg-blue-600 text-white p-6 shadow">
//         <h1 className="text-3xl font-bold">Project Inspector</h1>
//       </header>

//       {/* Content */}
//       <main className="max-w-6xl mx-auto p-6 space-y-8">
//         {/* Upload Section */}
//         <section className="bg-white p-6 rounded shadow">
//           <h2 className="text-xl font-semibold mb-4">Upload Project</h2>
//           <UploadForm onResult={setReport} />
//         </section>

//         {/* Report Section */}
//         {report && (
//           <section className="space-y-6">
//             <ReportView report={report} />
//           </section>
//         )}
//       </main>
//     </div>
//   );
// }

// New 03

// frontend/src/App.jsx

import React, { useState } from "react";
import UploadForm from "./components/UploadForm";
import ReportView from "./components/ReportView";
import bgImage from './assets/project-inspector-bg.jpg'; // relative to App.jsx


export default function App() {
  const [report, setReport] = useState(null);

  return (
    <div className="relative min-h-screen font-sans overflow-x-hidden">
      {/* Background Image */}
      <div
        className="absolute top-0 left-0 w-full h-full -z-10"
        style={{
          backgroundImage: `url(${bgImage})`,
          backgroundSize: "cover",
          backgroundPosition: "center",
          backgroundRepeat: "no-repeat",
          opacity: 0.4,
        }}
      ></div>

      {/* Header */}
      <header className="bg-teal-100 text-teal-800 p-6 shadow-md">
        <h1 className="text-3xl font-bold">🚀 Project Inspector</h1>
      </header>

      {/* Main content */}
      <main className="max-w-6xl mx-auto p-6 space-y-8">
        {/* Upload Section */}
        <section className="bg-white/90 backdrop-blur-md p-6 rounded-xl shadow-md hover:shadow-xl transition">
          <h2 className="text-xl font-semibold mb-4">📂 Upload Project</h2>
          <UploadForm onResult={setReport} />
        </section>

        {/* Report Section */}
        {report && (
          <section className="space-y-6">
            <ReportView report={report} />
          </section>
        )}
      </main>
    </div>
  );
}

