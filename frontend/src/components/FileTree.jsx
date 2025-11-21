// // frontend/src/components/FileTree.jsx
// import React, { useState } from "react";

// const FileTree = ({ fileTree }) => {
//   const [isOpen, setIsOpen] = useState(false);
//   const isDirectory = fileTree.type === "dir";

//   const toggleOpen = () => {
//     if (isDirectory) {
//       setIsOpen(!isOpen);
//     }
//   };

//   return (
//     <ul style={{ listStyleType: "none", paddingLeft: "20px" }}>
//       <li onClick={toggleOpen}>
//         <span style={{ cursor: isDirectory ? "pointer" : "default" }}>
//           {isDirectory ? (isOpen ? "📂" : "📁") : "📄"} {fileTree.name}
//         </span>
//         {isDirectory && isOpen && (
//           <ul>
//             {fileTree.children.map((child, index) => (
//               <li key={index}>
//                 <FileTree fileTree={child} />
//               </li>
//             ))}
//           </ul>
//         )}
//       </li>
//     </ul>
//   );
// };

// export default FileTree;

// frontend/src/components/FileTree.jsx
import React from "react";

const FileTree = ({ fileTree }) => {
  if (!fileTree) return null;

  const isDirectory = fileTree.type === "dir";

  // Ensure children is always an array
  const children =
    fileTree.children && Array.isArray(fileTree.children)
      ? fileTree.children
      : fileTree.children
      ? Object.values(fileTree.children) // convert object to array if needed
      : [];

  return (
    <ul style={{ listStyleType: "none", paddingLeft: "20px" }}>
      <li>
        <span>
          {isDirectory ? "📂" : "📄"} {fileTree.name}
        </span>

        {isDirectory && children.length > 0 && (
          <ul style={{ listStyleType: "none", paddingLeft: "20px" }}>
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
