
// frontend/src/components/ReportView.jsx
import React, { useState } from "react";
import FileTree from "./FileTree";

export default function ReportView({ report }) {
  const [expandedSections, setExpandedSections] = useState({
    fileTree: true,
    codeAnalysis: true,
    callGraph: true
  });

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const SectionHeader = ({ title, icon, sectionKey, isExpanded, hasContent }) => (
    <button
      onClick={() => toggleSection(sectionKey)}
      disabled={!hasContent}
      className={`
        w-full flex items-center justify-between p-4 text-left rounded-xl transition-all duration-300
        ${hasContent ? "hover:bg-gray-50 cursor-pointer" : "opacity-50 cursor-not-allowed"}
      `}
    >
      <div className="flex items-center gap-3">
        <span className="text-2xl">{icon}</span>
        <h2 className="text-2xl font-bold text-gray-800">{title}</h2>
      </div>
      {hasContent && (
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">
            {isExpanded ? "Collapse" : "Expand"}
          </span>
          <div className={`
            transform transition-transform duration-300
            ${isExpanded ? "rotate-180" : "rotate-0"}
          `}>
            <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>
      )}
    </button>
  );

  // Fixed SectionContent - using grid for better animation
  const SectionContent = ({ isExpanded, children, className = "" }) => (
    <div className={`
      grid transition-all duration-300 overflow-hidden
      ${isExpanded ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0"}
      ${className}
    `}>
      <div className="min-h-0">
        {children}
      </div>
    </div>
  );

  return (
    <div className="space-y-4">
      {/* File Tree Section */}
      <div className="bg-white/95 backdrop-blur-md rounded-2xl shadow-lg border border-gray-200">
        <SectionHeader
          title="Project Structure"
          icon="📄"
          sectionKey="fileTree"
          isExpanded={expandedSections.fileTree}
          hasContent={!!report.file_tree}
        />
        <SectionContent isExpanded={expandedSections.fileTree && !!report.file_tree}>
          <div className="px-6 pb-6">
            <FileTree fileTree={report.file_tree} />
          </div>
        </SectionContent>
      </div>

      {/* Code Analysis Section */}
      <div className="bg-white/95 backdrop-blur-md rounded-2xl shadow-lg border border-gray-200">
        <SectionHeader
          title="Code Analysis"
          icon="📊"
          sectionKey="codeAnalysis"
          isExpanded={expandedSections.codeAnalysis}
          hasContent={!!report.html}
        />
        <SectionContent isExpanded={expandedSections.codeAnalysis && !!report.html}>
          <div className="px-8 pb-8">
            <div className="prose prose-lg max-w-none" dangerouslySetInnerHTML={{ __html: report.html }} />
          </div>
        </SectionContent>
      </div>

      {/* Call Graph Section */}
      <div className="bg-white/95 backdrop-blur-md rounded-2xl shadow-lg border border-gray-200">
        <SectionHeader
          title="Function Call Graph"
          icon="🔗"
          sectionKey="callGraph"
          isExpanded={expandedSections.callGraph}
          hasContent={!!report.call_graph}
        />
        <SectionContent isExpanded={expandedSections.callGraph && !!report.call_graph}>
          <div className="px-8 pb-8">
            <div className="bg-gray-50 p-4 rounded-xl border">
              <img 
                src={`/static/${report.call_graph}`} 
                alt="Function Call Graph" 
                className="w-full rounded-lg shadow-sm" 
              />
            </div>
          </div>
        </SectionContent>
      </div>

      {/* Expand/Collapse All Buttons */}
      <div className="flex justify-center gap-4 pt-4">
        <button
          onClick={() => setExpandedSections({ fileTree: true, codeAnalysis: true, callGraph: true })}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors duration-200 shadow-sm"
        >
          Expand All
        </button>
        <button
          onClick={() => setExpandedSections({ fileTree: false, codeAnalysis: false, callGraph: false })}
          className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors duration-200 shadow-sm"
        >
          Collapse All
        </button>
      </div>
    </div>
  );
}