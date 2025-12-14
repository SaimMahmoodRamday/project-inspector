
# backend/app/parsers/python_parser.py

import ast
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple

class FunctionInfo:
    def __init__(self, name: str, lineno: int, file_path: str):
        self.name = name
        self.lineno = lineno
        self.file_path = file_path
        self.calls = []  # List of (called_function_name, is_local)

class ModuleAnalyzer(ast.NodeVisitor):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.functions = {}  # function_name -> FunctionInfo
        self.current_function = None
        self.local_modules = set()  # Modules imported from the same project
        self.external_modules = set()  # External libraries
        
    def visit_Import(self, node):
        for alias in node.names:
            module_name = alias.name
            # Check if it's a local project module
            if self._is_local_module(module_name):
                self.local_modules.add(module_name)
            else:
                self.external_modules.add(module_name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        module_name = node.module if node.module else ""
        if self._is_local_module(module_name):
            self.local_modules.add(module_name)
        else:
            self.external_modules.add(module_name)
        self.generic_visit(node)
    
    def _is_local_module(self, module_name: str) -> bool:
        """Check if module is likely part of the current project"""
        # Simple heuristic: if no dots or starts with dot, likely local
        return '.' not in module_name or module_name.startswith('.')
    
    def visit_FunctionDef(self, node):
        func_name = node.name
        func_info = FunctionInfo(func_name, node.lineno, self.file_path)
        self.functions[func_name] = func_info
        
        # Track scope
        prev_function = self.current_function
        self.current_function = func_info
        self.generic_visit(node)
        self.current_function = prev_function
    
    def visit_ClassDef(self, node):
        # Process class methods
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_name = f"{node.name}.{item.name}"
                method_info = FunctionInfo(method_name, item.lineno, self.file_path)
                self.functions[method_name] = method_info
                
                prev_function = self.current_function
                self.current_function = method_info
                self.generic_visit(item)
                self.current_function = prev_function
        # Don't visit other class body elements to avoid confusion
    
    def visit_Call(self, node):
        if not self.current_function:
            self.generic_visit(node)
            return
        
        called_name = None
        is_local = True  # Assume local unless proven otherwise
        
        if isinstance(node.func, ast.Name):
            called_name = node.func.id
            # Check if it's from an imported external module
            for ext_mod in self.external_modules:
                if called_name.startswith(ext_mod) or ext_mod in called_name:
                    is_local = False
                    break
        
        elif isinstance(node.func, ast.Attribute):
            # Handle method calls and module.function calls
            if isinstance(node.func.value, ast.Name):
                module_name = node.func.value.id
                func_name = node.func.attr
                called_name = f"{module_name}.{func_name}"
                
                # Check if module is external
                if module_name in self.external_modules:
                    is_local = False
            else:
                # Complex attribute access - keep simple
                called_name = node.func.attr
        
        if called_name and is_local:  # Only track local calls
            self.current_function.calls.append(called_name)
        
        self.generic_visit(node)

def parse_python_file(path: Path) -> Dict[str, Any]:
    """Parse a Python file and extract function/call information"""
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source)
    except SyntaxError as e:
        return {
            "functions": [],
            "call_edges": [],
            "local_modules": [],
            "error": f"Syntax error: {e}"
        }
    
    analyzer = ModuleAnalyzer(str(path))
    analyzer.visit(tree)
    
    # Prepare function data
    functions = []
    for func_name, func_info in analyzer.functions.items():
        functions.append({
            "name": func_name,
            "lineno": func_info.lineno,
            "file": func_info.file_path,
            "calls": func_info.calls
        })
    
    # Build call edges within this file
    call_edges = []
    for func_name, func_info in analyzer.functions.items():
        for called_func in func_info.calls:
            # Only create edge if the called function is defined in this file
            if called_func in analyzer.functions:
                call_edges.append({
                    "caller": func_name,
                    "callee": called_func,
                    "type": "internal"
                })
            else:
                # This is a call to a function possibly defined elsewhere
                call_edges.append({
                    "caller": func_name,
                    "callee": called_func,
                    "type": "cross_file",
                    "target_module": called_func.split('.')[0] if '.' in called_func else None
                })
    
    return {
        "functions": functions,
        "call_edges": call_edges,
        "local_modules": list(analyzer.local_modules),
        "external_modules": list(analyzer.external_modules),
        "function_count": len(functions),
        "internal_call_count": len([e for e in call_edges if e["type"] == "internal"]),
        "cross_file_call_count": len([e for e in call_edges if e["type"] == "cross_file"])
    }