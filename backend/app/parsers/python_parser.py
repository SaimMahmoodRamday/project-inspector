
# backend/app/parsers/python_parser.py
import ast
from pathlib import Path
from typing import Dict, List, Any

class FuncInfo:
    def __init__(self, name, lineno):
        self.name = name
        self.lineno = lineno
        self.calls = []  # list of function names called

class Analyzer(ast.NodeVisitor):
    def __init__(self):
        self.functions = {}  # name -> FuncInfo
        self.current_function = None

    def visit_FunctionDef(self, node):
        fi = FuncInfo(node.name, node.lineno)
        self.functions[node.name] = fi
        prev = self.current_function
        self.current_function = fi
        self.generic_visit(node)
        self.current_function = prev

    def visit_Call(self, node):
        # Simple: get called function name if direct Name or Attr
        name = None
        if isinstance(node.func, ast.Name):
            name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            # maybe obj.method
            name = node.func.attr
        if name and self.current_function:
            self.current_function.calls.append(name)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        # we can collect methods as functions with prefix class.method
        # For simplicity, visit body and treat methods as functions with class prefix
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                fname = f"{node.name}.{item.name}"
                fi = FuncInfo(fname, item.lineno)
                self.functions[fname] = fi
                prev = self.current_function
                self.current_function = fi
                self.generic_visit(item)
                self.current_function = prev
            else:
                self.generic_visit(item)

def parse_python_file(path: Path) -> Dict[str, Any]:
    source = path.read_text(encoding="utf-8", errors="ignore")
    tree = ast.parse(source)
    analyzer = Analyzer()
    analyzer.visit(tree)

    # Build list of funcs
    funcs = [{"name": name, "lineno": fi.lineno, "calls": fi.calls} for name, fi in analyzer.functions.items()]

    # Build call edges (simple: caller -> callee if callee name matches a known function or not)
    edges = []
    # For now, we only create edges where both names are known and in same file
    known_names = set(analyzer.functions.keys())
    # also consider methods by suffix match (e.g., call to 'method' might map to 'Class.method' - fuzzy)
    for name, fi in analyzer.functions.items():
        for callee in fi.calls:
            # find best match
            if callee in known_names:
                edges.append({"caller": name, "callee": callee})
            else:
                # fuzzy match: find any known function that endswith callee
                match = next((k for k in known_names if k.endswith("." + callee) or k == callee), None)
                if match:
                    edges.append({"caller": name, "callee": match})
                else:
                    # unknown callee, you can still record it
                    edges.append({"caller": name, "callee": callee})
    return {
        "functions": funcs,
        "call_edges": edges,
        "summary": f"Parsed {len(funcs)} functions in file."
    }
