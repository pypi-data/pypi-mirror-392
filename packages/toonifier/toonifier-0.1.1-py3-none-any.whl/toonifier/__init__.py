from .parser import loads_string as _loads_string, loads as _loads_file
from .encoder import dumps as _dumps
from pathlib import Path

__all__ = ["load", "dump", "loads", "dumps"]

# ---------------------------
# File-based API
# ---------------------------

def load(filename):
    """Load Toon file into a Python object."""
    return _loads_file(filename)

def dump(obj, filename):
    """Write a Python object to a Toon file."""
    Path(filename).write_text(_dumps(obj), encoding="utf-8")


# ---------------------------
# String-based API
# ---------------------------

def loads(text):
    """Parse Toon string into a Python object."""
    return _loads_string(text)

def dumps(obj):
    """Convert Python object into Toon text."""
    return _dumps(obj)
