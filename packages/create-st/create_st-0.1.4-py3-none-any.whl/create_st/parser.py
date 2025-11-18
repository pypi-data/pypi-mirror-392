import os
import re

TREE = "│├└─"

def clean_line(line):
    return line.rstrip("\n").rstrip()

def level_from_tree(line):
    count = 0
    for ch in line:
        if ch in TREE:
            count += 1
        elif ch.strip() == "":
            continue
        else:
            break
    return count

def strip_tree_chars(line):
    return "".join(ch for ch in line if ch not in TREE).lstrip()

def normalize_lines(lines):
    result = []
    for line in lines:
        if line.strip():
            result.append(line)
    return result

def build_structure(lines, base_path):
    stack = [(0, base_path)]

    for raw in lines:
        lvl = level_from_tree(raw)
        name = strip_tree_chars(raw)
        is_dir = name.endswith("/")
        if is_dir:
            name = name[:-1]

        while stack and lvl < stack[-1][0]:
            stack.pop()

        if lvl > stack[-1][0]:
            stack.append((lvl, stack[-1][1]))

        parent = stack[-1][1]
        path = os.path.join(parent, name)

        if is_dir:
            os.makedirs(path, exist_ok=True)
            stack.append((lvl, path))
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, "w", encoding="utf-8").close()
