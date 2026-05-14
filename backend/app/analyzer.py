
# backend/app/analyzer.py
from pathlib import Path
import os
import time
import base64
from typing import Dict, Any
from app.parsers.python_parser import parse_python_file
import networkx as nx
from graphviz import Digraph
import markdown
from app.summarizer import clean_code_for_summary, get_cached_summary


# ----------------------------
# IGNORE CONSTANTS (ADDED)
# ----------------------------
IGNORE_FOLDERS = {"node_modules", ".git", "__pycache__", "dist", "build", "venv"}
IGNORE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg",
    ".exe", ".dll", ".bin", ".db", ".lock",
    ".zip", ".tar", ".gz", ".pyc" , ".gitignore"
}

LANG_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".java": "java",
    ".ts": "typescript",
    # extend as needed
}

# ---------------------------------------------------
# Helper: Check whether a path should be ignored
# ---------------------------------------------------
def should_ignore(path: Path) -> bool:
    # Ignore folders
    for part in path.parts:
        if part in IGNORE_FOLDERS:
            return True

    # Ignore file extensions
    if path.is_file() and path.suffix.lower() in IGNORE_EXTENSIONS:
        return True

    return False


# ---------------------------------------------------
# Build File Tree (with filtering)
# ---------------------------------------------------
def build_file_tree(root: Path) -> Dict:
    """Return a nested dict representing file tree"""

    def _recurse(p: Path):
        if should_ignore(p):
            return None  # <--- FILTERED

        if p.is_file():
            return {"type": "file", "name": p.name}

        children = []
        for child in sorted(p.iterdir(), key=lambda x: (x.is_file(), x.name.lower())):
            if should_ignore(child):
                continue  # <--- FILTERED

            sub = _recurse(child)
            if sub:
                children.append(sub)

        return {"type": "dir", "name": p.name, "children": children}

    return _recurse(root)


# ---------------------------------------------------
# Analyze Project (with filtering)
# ---------------------------------------------------


def analyze_project(root: Path) -> Dict[str, Any]:
    report = {}
    root = Path(root)
    
    # Build filtered file tree
    report['file_tree'] = build_file_tree(root)
    
    analyses = {}
    call_graph = nx.DiGraph()
    all_functions = {}
    
    # First pass: collect all functions
    for p in root.rglob("*"):
        if should_ignore(p):
            continue

        if p.is_file() and p.suffix.lower() == ".py":
            relative_path = str(p.relative_to(root))
            
            try:
                parsed = parse_python_file(p)
                raw_code = p.read_text(encoding="utf-8", errors="ignore")
                
                # Store functions
                for func in parsed.get("functions", []):
                    func_name = func['name']
                    node_id = f"{relative_path}:{func_name}"
                    all_functions[node_id] = {
                        "file": relative_path,
                        "function": func,
                        "calls": func.get("calls", [])
                    }
                
                # Get summary
                summary_data = get_cached_summary(relative_path, raw_code)
                
                analyses[relative_path] = {
                    "lang": "python", 
                    **parsed,
                    "summary": summary_data
                }
                
            except Exception as e:
                print(f"[ERROR] Failed to analyze {relative_path}: {e}")
                analyses[relative_path] = {
                    "lang": "python", 
                    "error": str(e),
                    "summary": {"summary": "Analysis failed", "external_imports": []}
                }
    
    # Add nodes to graph
    for node_id, func_data in all_functions.items():
        func_info = func_data["function"]
        call_graph.add_node(
            node_id,
            file=func_data["file"],
            function=func_info['name'],
            simple_name=func_info['name'].split('.')[-1],
            lineno=func_info['lineno']
        )
    
    # Build edges - SIMPLIFIED: Only add cross-file edges
    for node_id, func_data in all_functions.items():
        file_path = func_data["file"]
        calls = func_data["calls"]
        
        for callee_name in calls:
            # Look for the callee in ALL functions
            found_callee = None
            
            for candidate_id, candidate_data in all_functions.items():
                candidate_file = candidate_data["file"]
                candidate_name = candidate_data["function"]["name"]
                
                # Skip if same file (we're only showing cross-file calls)
                if candidate_file == file_path:
                    continue
                
                # Check for match
                if (callee_name == candidate_name or 
                    callee_name.endswith(f".{candidate_name.split('.')[-1]}")):
                    found_callee = candidate_id
                    break
            
            if found_callee:
                call_graph.add_edge(node_id, found_callee, type="cross_file")
    
    report['files'] = analyses
    
    # Create CLEAN, SIMPLE graph visualization
    dot = Digraph(comment="Call Graph - Cross-File Dependencies",
                  engine='fdp')  # Using fdp for better force-directed layout
    
    # Configure graph for clean, spacious layout
    dot.attr(
        rankdir='TB',  # Top to bottom
        splines='curved',  # Curved edges for better readability
        overlap='scale',  # Prevent node overlap
        sep='1.2',  # Increase separation between nodes
        nodesep='0.8',  # Space between nodes
        ranksep='1.5',  # Space between ranks
        concentrate='false',  # Don't merge parallel edges
        bgcolor='transparent'
    )
    
    # Group nodes by file for better organization
    file_colors = {}
    color_palette = ['#FFE4E1', '#E0FFFF', '#F0FFF0', '#FFF0F5', '#F5FFFA', 
                     '#FFFACD', '#F0F8FF', '#F8F8FF', '#FAF0E6', '#F5F5DC']
    
    # Assign a color to each file
    files = sorted(set([all_functions[node_id]["file"] for node_id in all_functions.keys()]))
    for i, file in enumerate(files):
        file_colors[file] = color_palette[i % len(color_palette)]
    
    # Add nodes with clean, minimal styling
    for node_id in sorted(call_graph.nodes()):
        func_data = all_functions[node_id]
        file_path = func_data["file"]
        func_info = func_data["function"]
        
        # Get short file name for display
        file_name = file_path.split('/')[-1] if '/' in file_path else file_path
        simple_func_name = func_info['name'].split('.')[-1]
        
        # Create clean label
        label = f"{simple_func_name}\\n({file_name}:{func_info['lineno']})"
        
        dot.node(
            node_id,
            label=label,
            shape='box',
            style='filled,rounded',
            fillcolor=file_colors.get(file_path, 'lightblue'),
            fontname='Arial',
            fontsize='12',  # Increased from '10' to '12'
            width='1.5',  # Increased from '1.2'
            height='1.0',  # Increased from '0.8'
            margin='0.15,0.10'  # Small margin inside node
        )
    
    # Add only cross-file edges (filter out any self-references or same-file edges)
    edge_count = 0
    for u, v, edge_data in call_graph.edges(data=True):
        if edge_data.get('type') == 'cross_file':
            u_file = all_functions[u]["file"]
            v_file = all_functions[v]["file"]
            
            # Skip if same file (shouldn't happen but just in case)
            if u_file == v_file:
                continue
                
            # Color edge black
            edge_color = 'black'  # Changed from file_colors.get(u_file, 'gray')
            
            dot.edge(
                u, v,
                color=edge_color,  # Now always black
                penwidth='1.2',
                arrowsize='0.8',
                fontname='Arial',
                fontsize='8',
                label=''
            )
            edge_count += 1
    
    print(f"Created graph with {call_graph.number_of_nodes()} nodes and {edge_count} cross-file edges")
    
    # ── Option A: File on disk + URL (commented out) ─────────────────────────
    # Kept for reference. Breaks on multi-replica Container Apps because each
    # replica has isolated ephemeral storage, so a different replica may serve
    # the browser's GET /static/<file> request and return 404.
    # Also: FastAPI StaticFiles is not covered by CORSMiddleware, so cross-origin
    # <img> requests are blocked without an extra CORS header.
    #
    # STATIC_DIR = Path("/app/static")
    # STATIC_DIR.mkdir(parents=True, exist_ok=True)
    # graph_filename = f"call_graph_{int(time.time())}.svg"
    # graph_path = STATIC_DIR / graph_filename
    # dot.render(str(graph_path.with_suffix("")), format="svg", cleanup=True)
    # report['call_graph'] = f"https://project-inspector-backend.proudfield-b0f3558f.eastus.azurecontainerapps.io/static/{graph_filename}"
    # ─────────────────────────────────────────────────────────────────────────

    # ── Option B: Data URI embedded in JSON response (active) ─────────────────
    # SVG bytes are base64-encoded and returned as a data: URI inside the JSON.
    # - No disk I/O, no storage to clean up, no storage runout risk
    # - Works correctly across any number of replicas (stateless)
    # - No CORS issue — the data is already in the /upload response body
    # - <img src="data:image/svg+xml;base64,..."> works in all modern browsers
    svg_bytes = dot.pipe(format="svg")
    svg_b64 = base64.b64encode(svg_bytes).decode("utf-8")
    report['call_graph'] = f"data:image/svg+xml;base64,{svg_b64}"
    # ─────────────────────────────────────────────────────────────────────────
    
    # Simple statistics
    stats = {
        "total_functions": call_graph.number_of_nodes(),
        "cross_file_calls": edge_count,
        "files_with_functions": len(files)
    }
    
    print(f"Graph stats: {stats['total_functions']} functions across {stats['files_with_functions']} files")
    print(f"Cross-file dependencies: {stats['cross_file_calls']}")

    # -------------------------------------------
    # Fixed Markdown summary
    # -------------------------------------------
    md = ["# 🗂️ Project Analysis Report", ""]

    # Project Overview
    python_files = [f for f, info in analyses.items() if info.get('lang') == 'python']
    other_files = [f for f, info in analyses.items() if info.get('lang') != 'python']
    total_functions = sum(len(info.get('functions', [])) for f, info in analyses.items() if info.get('functions'))

    md.append("## 📊 Project Overview")
    md.append("")
    md.append(f"- **Python Files:** {len(python_files)}")
    md.append(f"- **Other Files:** {len(other_files)}")
    md.append(f"- **Total Functions:** {total_functions}")
    md.append(f"- **Total Files:** {len(analyses)}")
    md.append("")

    # Python Files Analysis
    if python_files:
        md.append("## 🐍 Python Code Analysis")
        md.append("")
        
        for i, fname in enumerate(python_files, 1):
            info = analyses[fname]
            md.append(f"### {i}. `{fname}`")
            md.append("")
            
            if info.get("error"):
                md.append("❌ **Error:** " + str(info["error"]))
                md.append("")
            else:
                # Get summary data - ensure it's a dictionary
                summary_data = info.get("summary", {})
                if not isinstance(summary_data, dict):
                    # Convert to dict if it's a string
                    summary_data = {"summary": str(summary_data), "external_imports": []}
                
                # Summary
                summary_text = summary_data.get("summary", "No summary available")
                md.append("📝 **Summary:** " + str(summary_text))
                md.append("")
                
                # External imports
                external_imports = summary_data.get("external_imports", [])
                if external_imports and external_imports != ["none"]:
                    md.append("🔗 **Project Imports:**")
                    for imp in external_imports:
                        md.append(f"   - `{imp}`")
                    md.append("")
                else:
                    md.append("🔗 **Project Imports:** None")
                    md.append("")
                
                # Functions
                funcs = info.get("functions", [])
                if funcs:
                    md.append("🔧 **Functions:**")
                    for f in funcs:
                        md.append(f"   - `{f['name']}` (line {f['lineno']})")
                    md.append("")
            
            # Add separator only if not last file
            if i < len(python_files):
                md.append("---")
                md.append("")

    # Add this when parsing implemented for these. 

    # Other Files Section
    if other_files:
        md.append("## 📁 Other Files")
        md.append("")
        
        for i, fname in enumerate(other_files, 1):
            info = analyses[fname]
            md.append(f"### `{fname}`")
            # md.append(f"**Type:** {info.get('lang', 'Unknown')}")
            
            # note = info.get("note")
            # if note:
                # md.append(f"**Note:** {note}")
            
            md.append("")
            
            # Add separator only if not last file
            if i < len(other_files):
                md.append("---")
                md.append("")

    # Clean up
    while md and md[-1] in ["", "---"]:
        md.pop()

    # Ensure all items are strings before joining
    md = [str(item) for item in md]

    report_md = "\n".join(md)
    report['markdown'] = report_md
    report['html'] = markdown.markdown(report_md)

    return report
