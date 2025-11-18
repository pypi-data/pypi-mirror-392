import os
import re

def clean_line(line):
    line = line.rstrip("\n")
    line = re.sub(r"[│├└─]+", "", line)
    return line.rstrip()

def normalize_lines(lines):
    result = []
    for line in lines:
        c = clean_line(line)
        if c.strip():
            result.append(c)
    return result

def detect_indent(line):
    return len(line) - len(line.lstrip(" "))

def build_structure(lines, base_path):
    stack = [(0, base_path)]
    for raw in lines:
        indent = detect_indent(raw)
        item = raw.strip()
        is_dir = item.endswith("/")

        if is_dir:
            item = item[:-1]

        while stack and indent < stack[-1][0]:
            stack.pop()

        current_path = os.path.join(stack[-1][1], item)

        if is_dir:
            os.makedirs(current_path, exist_ok=True)
            stack.append((indent, current_path))
        else:
            os.makedirs(os.path.dirname(current_path), exist_ok=True)
            open(current_path, "w", encoding="utf-8").close()