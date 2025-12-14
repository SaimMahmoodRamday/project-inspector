
// frontend/src/components/FileTree.jsx

import React from "react";

const FileTree = ({ fileTree }) => {
  if (!fileTree) return null;

  const isDirectory = fileTree.type === "dir";
  const children = fileTree.children
    ? Array.isArray(fileTree.children)
      ? fileTree.children
      : Object.values(fileTree.children)
    : [];

  return (
    <ul className="list-none pl-4 space-y-1">
      <li>
        <span className="font-medium">
          {isDirectory ? "📂" : "📄"} {fileTree.name}
        </span>
        {isDirectory && children.length > 0 && (
          <ul className="pl-4 mt-1 space-y-1">
            {children.map((child, index) => (
              <li key={index}>
                <FileTree fileTree={child} />
              </li>
            ))}
          </ul>
        )}
      </li>
    </ul>
  );
};

export default FileTree;
