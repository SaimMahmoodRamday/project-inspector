
# backend/app/analyzer.py
from pathlib import Path
import os
from typing import Dict, Any, List
from app.parsers.python_parser import parse_python_file
import networkx as nx
from graphviz import Digraph
import markdown
from app.summarizer import clean_code_for_summary, get_cached_summary

import json

LANG_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".java": "java",
    ".ts": "typescript",
    # extend as needed
}

def build_file_tree(root: Path) -> Dict:
    """Return a nested dict representing file tree"""
    def _recurse(p: Path):
        if p.is_file():
            return {"type": "file", "name": p.name}
        children = []
        for child in sorted(p.iterdir(), key=lambda x: (x.is_file(), x.name.lower())):
            children.append(_recurse(child))
        return {"type": "dir", "name": p.name, "children": children}
    return _recurse(root)

def analyze_project(root: Path) -> Dict[str, Any]:
    report = {}
    root = Path(root)
    report['file_tree'] = build_file_tree(root)

    # Collect analyses per file
    analyses = {}
    call_graph = nx.DiGraph()

    for p in root.rglob("*"):
        if p.is_file():
            ext = p.suffix.lower()
            lang = LANG_EXTENSIONS.get(ext)
            if lang == "python":
                try:
                    parsed = parse_python_file(p)

                    # Read and clean code for LLM
                    raw_code = p.read_text(encoding="utf-8", errors="ignore")
                    safe_code = clean_code_for_summary(raw_code)

                    # Get Gemini summary (cached to save cost/time)
                    llm_summary = get_cached_summary(str(p.relative_to(root)), safe_code)

                    # Overwrite or enhance parsed summary
                    parsed["summary"] = llm_summary

                    analyses[str(p.relative_to(root))] = {"lang": "python", **parsed}

                    # Add nodes/edges to call_graph
                    for func in parsed.get("functions", []):
                        node_name = f"{p.name}:{func['name']}"
                        call_graph.add_node(node_name, file=str(p.relative_to(root)), type="function")
                    for edge in parsed.get("call_edges", []):
                        caller = f"{p.name}:{edge['caller']}"
                        callee = f"{p.name}:{edge['callee']}"
                        call_graph.add_edge(caller, callee)
                except Exception as e:
                    analyses[str(p.relative_to(root))] = {"lang": "python", "error": str(e)}
            else:
                # For other langs, we can add placeholder or sniff
                analyses[str(p.relative_to(root))] = {"lang": lang or "unknown", "note": "parsing not implemented"}

    report['files'] = analyses

    # Render call graph using graphviz
    dot = Digraph(comment="Call graph")
    for n in call_graph.nodes:
        dot.node(n)
    for u, v in call_graph.edges:
        dot.edge(u, v)
    graph_path = root / "call_graph.svg"
    dot.render(str(graph_path.with_suffix("")), format="svg", cleanup=True)  # creates call_graph.svg
    report['call_graph'] = "call_graph.svg"

    # Create a simple markdown summary
    md = ["# Project Report", ""]
    md.append("## File Tree")
    md.append("```")
    def pretty_tree(d, prefix=""):
        lines = []
        name = d.get("name", "")
        if d["type"] == "dir":
            lines.append(f"{prefix}{name}/")
            for c in d.get("children", []):
                lines.extend(pretty_tree(c, prefix + "  "))
        else:
            lines.append(f"{prefix}{name}")
        return lines
    md.extend(pretty_tree(report['file_tree']))
    md.append("```")
    md.append("## File Summaries")
    for fname, info in analyses.items():
        md.append(f"### {fname}")
        md.append(f"Language: {info.get('lang')}")
        if info.get("error"):
            md.append(f"Error: {info['error']}")
        else:
            if info.get("summary"):
                md.append(info['summary'])
            funcs = info.get("functions", [])
            if funcs:
                md.append("Functions:")
                for f in funcs:
                    md.append(f"- `{f['name']}` ({f['lineno']})")
    report_md = "\n".join(md)
    report['markdown'] = report_md
    report['html'] = markdown.markdown(report_md)

    return report
