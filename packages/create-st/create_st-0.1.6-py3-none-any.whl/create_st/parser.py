import os

BRANCH = {"│", "├", "└", "─"}

def strip_eol(line):
    return line.replace("\r", "").replace("\n", "").rstrip()

def get_level(line):
    level = 0
    for ch in line:
        if ch in BRANCH:
            level += 1
        elif ch == " ":
            continue
        else:
            break
    return level

def clean_name(line):
    result = []
    skip = True
    for ch in line:
        if skip and (ch in BRANCH or ch == " "):
            continue
        skip = False
        result.append(ch)
    name = "".join(result).strip()
    return name

def normalize_lines(lines):
    out = []
    for line in lines:
        s = strip_eol(line)
        if s.strip():
            out.append(s)
    return out

def build_structure(lines, base_dir):
    stack = [(0, base_dir)]

    for raw in lines:
        lvl = get_level(raw)
        name = clean_name(raw)

        if name.endswith("/"):
            is_dir = True
            name = name[:-1]
        else:
            is_dir = False

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
