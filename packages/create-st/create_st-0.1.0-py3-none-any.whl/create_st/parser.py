import os

def normalize_lines(lines):
    cleaned = []
    for line in lines:
        if not line.strip():
            continue
        cleaned.append(line.rstrip())
    return cleaned

def detect_indent(line):
    return len(line) - len(line.lstrip())

def build_structure(lines, base_path):
    stack = [(0, base_path)]
    for line in lines:
        indent = detect_indent(line)
        name = line.strip().rstrip("/")
        is_dir = line.strip().endswith("/")
        while stack and indent < stack[-1][0]:
            stack.pop()
        current_path = os.path.join(stack[-1][1], name)
        if is_dir:
            os.makedirs(current_path, exist_ok=True)
            stack.append((indent, current_path))
        else:
            os.makedirs(os.path.dirname(current_path), exist_ok=True)
            open(current_path, "w", encoding="utf-8").close()