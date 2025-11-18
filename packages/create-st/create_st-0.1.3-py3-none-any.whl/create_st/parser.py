import os
import re

TREE_CHARS = "│├└─"

def clean_tree(line):
    line = line.rstrip("\n")
    line = "".join(ch for ch in line if ch not in TREE_CHARS)
    return line.rstrip()

def normalize_lines(lines):
    cleaned = []
    for line in lines:
        cl = clean_tree(line)
        if cl.strip():
            cleaned.append(cl)
    return cleaned

def detect_indent_levels(lines):
    indents = []
    for line in lines:
        n = len(line) - len(line.lstrip())
        if n > 0:
            indents.append(n)
    if not indents:
        return 1
    return min(indents)

def get_indent(line, step):
    raw = len(line) - len(line.lstrip())
    return raw // step

def build_structure(lines, base_path):
    step = detect_indent_levels(lines)
    stack = [(0, base_path)]

    for raw in lines:
        indent = get_indent(raw, step)
        name = raw.strip()
        is_dir = name.endswith("/")
        if is_dir:
            name = name[:-1]

        while stack and indent < stack[-1][0]:
            stack.pop()

        if indent > stack[-1][0]:
            stack.append((indent, os.path.join(stack[-1][1], "")))

        parent = stack[-1][1]
        path = os.path.join(parent, name)

        if is_dir:
            os.makedirs(path, exist_ok=True)
            stack.append((indent, path))
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, "w", encoding="utf-8").close()
