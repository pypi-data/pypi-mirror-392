from typing import Any, List
import json

def _needs_quote(s: str) -> bool:
    return s == "" or any(c in s for c in ",\n\r\t") or s in ("true", "false", "null") or s.startswith(" ") or s.endswith(" ")

def _format_scalar(v: Any) -> str:
    if v is None:
        return "null"
    if v is True:
        return "true"
    if v is False:
        return "false"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, str):
        # Use triple-quoted for multi-line strings
        if "\n" in v:
            escaped = v.replace('"""', r'\"\"\"')
            return f'"""{escaped}"""'
        if _needs_quote(v):
            return f'"{v}"'
        return v
    raise TypeError(f"Unsupported scalar type: {type(v)}")


def dumps(obj: Any) -> str:
    if not isinstance(obj, dict):
        raise TypeError("Top-level must be a dict for official Toon")
    return "\n".join(_dump_dict(obj, 0)) + "\n"

def _dump_dict(d: dict, level: int) -> List[str]:
    lines = []
    for k, v in d.items():
        lines.extend(_dump_key(k, v, level))
    return lines

def _dump_key(key: str, value: Any, level: int) -> List[str]:
    pad = "  " * level
    if isinstance(value, (str, int, float, bool)) or value is None:
        return [f"{pad}{key},{_format_scalar(value)}"]
    if isinstance(value, dict):
        lines = [f"{pad}{key},"]
        for k, v in value.items():
            lines.extend(_dump_key(k, v, level + 1))
        return lines
    if isinstance(value, list):
        if all(isinstance(x, dict) for x in value):
            # table: must have same keys in all dicts
            keys_set = [set(x.keys()) for x in value]
            if not all(keys_set[0] == ks for ks in keys_set):
                raise TypeError(f"All dicts in list {key} must have same fields")
            fields = list(value[0].keys())
            lines = [f"{pad}{key}[{len(value)}]{{{' '.join(fields)}}},"]
            for row in value:
                row_line = " ".join(_format_scalar(row[f]) for f in fields)
                lines.append(pad + "  " + row_line)
            return lines
        else:
            raise TypeError(f"Lists of non-dict type are not supported for key {key} in official Toon")
    raise TypeError(f"Unsupported type: {type(value)}")
