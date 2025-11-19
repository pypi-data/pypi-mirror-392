"""Canonical JSON serialization utilities.

Provides deterministic JSON serialization with sorted keys, minimal whitespace,
and normalized floating-point numbers for consistent output across runs.
"""

import json
from typing import Any


def canonical_dumps(obj: Any, indent: int = 0) -> str:
    """Serialize object to canonical JSON string.
    
    Canonical JSON means:
    - Keys are sorted alphabetically
    - Minimal whitespace (unless indent > 0)
    - Deterministic floating-point representation
    - Consistent formatting across runs
    
    Args:
        obj: Python object to serialize (dict, list, str, int, float, bool, None)
        indent: Number of spaces for indentation (0 = compact, >0 = pretty)
    
    Returns:
        Canonical JSON string representation
    
    Example:
        >>> canonical_dumps({"b": 2, "a": 1})
        '{"a":1,"b":2}'
        >>> canonical_dumps({"b": 2, "a": 1}, indent=2)
        '{\\n  "a": 1,\\n  "b": 2\\n}'
    """
    # Normalize floats to ensure deterministic representation
    normalized = _normalize_floats(obj)
    
    # Use sort_keys=True for deterministic key ordering
    if indent > 0:
        return json.dumps(normalized, sort_keys=True, indent=indent, ensure_ascii=False)
    else:
        return json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _normalize_floats(obj: Any) -> Any:
    """Recursively normalize floats in nested structures.
    
    Converts floats to integers if they represent whole numbers,
    and ensures consistent precision for floating-point values.
    
    Args:
        obj: Object to normalize
    
    Returns:
        Object with normalized floats
    """
    if isinstance(obj, float):
        # Convert whole-number floats to ints for consistency
        if obj.is_integer():
            return int(obj)
        # Round to reasonable precision to avoid floating-point noise
        return round(obj, 10)
    elif isinstance(obj, dict):
        return {k: _normalize_floats(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_normalize_floats(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(_normalize_floats(item) for item in obj)
    else:
        return obj

