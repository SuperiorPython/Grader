import ast
import json


def _has(tree, node_types):
    return any(isinstance(n, node_types) for n in ast.walk(tree))


def _is_recursive(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            fname = node.name
            for inner in ast.walk(node):
                if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Name) and inner.func.id == fname:
                    return True
    return False


def _has_decorators(tree):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.decorator_list:
            return True
    return False


def _has_type_hints(tree):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.returns is not None:
                return True
            for a in node.args.args:
                if a.annotation is not None:
                    return True
    return False


def _has_varargs(tree):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.args.vararg or node.args.kwarg:
                return True
    return False


def _has_default_args(tree):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.args.defaults:
            return True
    return False


def _has_multi_inheritance(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and len(node.bases) > 1:
            return True
    return False


def _has_inheritance(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.bases:
            return True
    return False


def _has_call_named(tree, func_names):
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in func_names:
            return True
    return False


def _has_method_call(tree, method_names):
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in method_names:
            return True
    return False


def _has_import(tree, module_names=None):
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if module_names is None or alias.name.split(".")[0] in module_names:
                    return True
        elif isinstance(node, ast.ImportFrom):
            if module_names is None or (node.module and node.module.split(".")[0] in module_names):
                return True
    return False


STRING_METHODS = {
    "split", "join", "strip", "lstrip", "rstrip", "upper", "lower", "replace",
    "format", "startswith", "endswith", "find", "title", "capitalize",
}
LIST_METHODS = {"append", "pop", "sort", "extend", "remove", "insert", "reverse", "count", "index"}
DICT_METHODS = {"keys", "values", "items", "get", "update", "setdefault"}

CONCEPT_DETECTORS = {
    "input_function": lambda t: _has_call_named(t, {"input"}),
    "for_loop": lambda t: _has(t, ast.For),
    "while_loop": lambda t: _has(t, ast.While),
    "conditionals": lambda t: _has(t, ast.If),
    "functions": lambda t: _has(t, (ast.FunctionDef, ast.AsyncFunctionDef)),
    "strings_methods": lambda t: _has_method_call(t, STRING_METHODS),
    "lists": lambda t: _has(t, ast.List) or _has_method_call(t, LIST_METHODS),
    "dictionaries": lambda t: _has(t, ast.Dict) or _has_method_call(t, DICT_METHODS),
    "modules_import": lambda t: _has_import(t, None),
    "api_requests": lambda t: _has_import(t, {"requests", "urllib", "http"}),
    "file_io": lambda t: _has_call_named(t, {"open"}),
    "image_processing": lambda t: _has_import(t, {"PIL", "Image", "cv2", "matplotlib"}),
    "classes": lambda t: _has(t, ast.ClassDef),
    "inheritance": _has_inheritance,
    "multiple_inheritance": _has_multi_inheritance,
    "recursion": _is_recursive,
    "lambda": lambda t: _has(t, ast.Lambda),
    "list_comprehension": lambda t: _has(t, ast.ListComp),
    "dict_comprehension": lambda t: _has(t, ast.DictComp),
    "set_comprehension": lambda t: _has(t, ast.SetComp),
    "generator_expression": lambda t: _has(t, ast.GeneratorExp),
    "generators_yield": lambda t: _has(t, (ast.Yield, ast.YieldFrom)),
    "try_except": lambda t: _has(t, ast.Try),
    "with_statement": lambda t: _has(t, ast.With),
    "decorators": _has_decorators,
    "async_await": lambda t: _has(t, (ast.AsyncFunctionDef, ast.Await)),
    "walrus_operator": lambda t: _has(t, ast.NamedExpr),
    "f_strings": lambda t: _has(t, ast.JoinedStr),
    "type_hints": _has_type_hints,
    "ternary_expression": lambda t: _has(t, ast.IfExp),
    "star_unpacking": lambda t: _has(t, ast.Starred),
    "variadic_args": _has_varargs,
    "default_arguments": _has_default_args,
    "global_keyword": lambda t: _has(t, ast.Global),
    "nonlocal_keyword": lambda t: _has(t, ast.Nonlocal),
}


def detect_concepts(source_code):
    tree = ast.parse(source_code)
    return sorted(name for name, fn in CONCEPT_DETECTORS.items() if fn(tree))


def analyze(source_code, known_json):
    """Entry point called from JS. known_json is a JSON array of concept names."""
    known = set(json.loads(known_json))
    try:
        used = detect_concepts(source_code)
    except SyntaxError as e:
        return json.dumps({"error": f"SyntaxError: {e}"})
    flagged = sorted(set(used) - known)
    return json.dumps({"used": used, "flagged": flagged})


if __name__ == "__main__":
    # quick smoke test
    sample = "is_even = lambda n: n % 2 == 0\nnums = [1,2,3]\nnums.append(4)\n"
    print(analyze(sample, json.dumps(["lists"])))
