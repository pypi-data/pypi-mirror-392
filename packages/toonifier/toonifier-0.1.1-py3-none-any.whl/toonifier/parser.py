import re
from typing import Any, List, Tuple

class ToonError(Exception):
    pass

# ---------------------------
# Scalar conversion
# ---------------------------
def _convert_scalar(tok: str, lines: List[str]=None, idx_ref: List[int]=None) -> Any:
    tok = tok.rstrip()
    if tok == "null": return None
    if tok == "true": return True
    if tok == "false": return False

    # Triple-quoted multi-line string
    if tok.startswith('"""') or tok.startswith("'''"):
        quote = tok[:3]
        if tok.endswith(quote) and len(tok) > 3:
            return tok[3:-3]
        # multiline
        assert lines is not None and idx_ref is not None, "lines and idx_ref required for multi-line string"
        parts = [tok[3:]]
        idx = idx_ref[0]
        while idx < len(lines):
            line = lines[idx]
            idx_ref[0] += 1
            if line.endswith(quote):
                parts.append(line[:-3])
                break
            parts.append(line)
        return "\n".join(parts)

    # Quoted string
    if (tok.startswith('"') and tok.endswith('"')) or (tok.startswith("'") and tok.endswith("'")):
        return tok[1:-1]

    # Numbers
    if re.fullmatch(r"-?\d+", tok): return int(tok)
    if re.fullmatch(r"-?\d+\.\d+", tok): return float(tok)

    return tok

# ---------------------------
# Regex helpers
# ---------------------------
_re_header = re.compile(r"^([^\[\{,]+)\[(\d+)\]\{([^\}]*)\},?$")
_re_keyval  = re.compile(r"^([^\s,]+)\s*,\s*(.*)$")

# ---------------------------
# Public API
# ---------------------------
def loads_string(text: str) -> Any:
    lines = [line.rstrip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")]
    if not lines: return {}
    idx_ref = [0]
    obj = _parse_block(lines, idx_ref, 0)
    return obj

def loads(filename: str) -> Any:
    with open(filename, "r", encoding="utf-8") as f:
        return loads_string(f.read())

# ---------------------------
# Nested object parsing
# ---------------------------
def _parse_block(lines: List[str], idx_ref: List[int], base_indent: int) -> dict:
    obj = {}
    while idx_ref[0] < len(lines):
        line = lines[idx_ref[0]]
        indent = len(line) - len(line.lstrip(" "))
        if indent < base_indent:
            break
        line = line.lstrip()
        idx_ref[0] += 1

        # Table
        m = _re_header.match(line)
        if m:
            key, count, fields = m.group(1).strip(), int(m.group(2)), m.group(3).split()
            arr = []
            for _ in range(count):
                if idx_ref[0] >= len(lines):
                    raise ToonError(f"Table {key} expected {count} rows, got {len(arr)}")
                row_line = lines[idx_ref[0]].lstrip()
                idx_ref[0] += 1
                tokens = row_line.split()
                if len(tokens) != len(fields):
                    raise ToonError(f"Table {key} row length mismatch: expected {len(fields)}, got {len(tokens)}")
                arr.append({f: _convert_scalar(tok) for f, tok in zip(fields, tokens)})
            obj[key] = arr
            continue

        # Key-Value
        kv = _re_keyval.match(line)
        if kv:
            key, val = kv.group(1), kv.group(2)
            if val == "":
                # Nested object
                obj[key] = _parse_block(lines, idx_ref, base_indent + 2)
            else:
                obj[key] = _convert_scalar(val, lines, idx_ref)
            continue

        # Unexpected line
        raise ToonError(f"Unexpected line {idx_ref[0]}: {line}")

    return obj
