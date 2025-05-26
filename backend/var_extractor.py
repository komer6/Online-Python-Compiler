# var_extractor.py

import ast

def is_code_safe(code: str) -> bool:
    banned_names = {
        "eval", "exec", "compile", "globals", "locals", "open",
        "__import__", "__builtins__", "__dict__", "__class__", "__name__", "__file__"
    }

    try:
        tree = ast.parse(code)

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom, ast.With)):
                return False

            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in banned_names:
                    return False
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in banned_names:
                        return False
                    if isinstance(node.func.value, ast.Name) and node.func.value.id in banned_names:
                        return False

            if isinstance(node, ast.Name) and node.id in banned_names:
                return False

            if isinstance(node, ast.Attribute) and node.attr in banned_names:
                return False

        return True

    except Exception:
        return False

def extract_variables_from_code(code: str) -> list[str]:
    """
    Extract top-level variable names from Python code.
    Only includes simple assignments like x = 1, or a, b = ...
    """
    try:
        tree = ast.parse(code)
        variables = []

        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        variables.append(target.id)
                    elif isinstance(target, ast.Tuple):
                        for elt in target.elts:
                            if isinstance(elt, ast.Name):
                                variables.append(elt.id)

        return variables
    except Exception:
        return []
