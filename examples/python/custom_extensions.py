"""
Example: Creating Custom EPLua Extensions

This file demonstrates how to create your own Python functions
that can be called from Lua scripts using the @export_to_lua decorator.
"""

import hashlib
import datetime
from eplua import export_to_lua, python_to_lua_table


@export_to_lua("current_datetime")
def current_datetime() -> any:
    """Get current date and time information as a Lua table."""
    now = datetime.datetime.now()
    return python_to_lua_table({
        "year": now.year,
        "month": now.month,
        "day": now.day,
        "hour": now.hour,
        "minute": now.minute,
        "second": now.second,
        "weekday": now.strftime("%A"),
        "formatted": now.strftime("%Y-%m-%d %H:%M:%S"),
        "iso": now.isoformat()
    })


@export_to_lua("hash_text")
def hash_text(text: str) -> any:
    """Generate multiple hashes for the given text."""
    return python_to_lua_table({
        "original": text,
        "length": len(text),
        "md5": hashlib.md5(text.encode()).hexdigest(),
        "sha1": hashlib.sha1(text.encode()).hexdigest(),
        "sha256": hashlib.sha256(text.encode()).hexdigest()
    })


@export_to_lua("string_utils")
def string_utils(text: str) -> any:
    """Provide various string utilities."""
    return python_to_lua_table({
        "original": text,
        "length": len(text),
        "upper": text.upper(),
        "lower": text.lower(),
        "reversed": text[::-1],
        "words": text.split(),
        "word_count": len(text.split()),
        "char_count": len(text),
        "is_numeric": text.isnumeric(),
        "is_alpha": text.isalpha()
    })


@export_to_lua("math_operations")
def math_operations(a: float, b: float) -> any:
    """Perform various math operations on two numbers."""
    import math
    
    return python_to_lua_table({
        "a": a,
        "b": b,
        "sum": a + b,
        "difference": a - b,
        "product": a * b,
        "quotient": a / b if b != 0 else None,
        "power": a ** b,
        "max": max(a, b),
        "min": min(a, b),
        "average": (a + b) / 2,
        "gcd": math.gcd(int(a), int(b)) if isinstance(a, int) and isinstance(b, int) else None
    })


if __name__ == "__main__":
    print("This is an EPLua extension module.")
    print("Import this in your EPLua engine to add custom functions.")
    print("\nAvailable functions:")
    print("  _PY.current_datetime() - Get current date/time info")
    print("  _PY.hash_text(text) - Generate hashes for text")
    print("  _PY.string_utils(text) - String manipulation utilities")
    print("  _PY.math_operations(a, b) - Math operations on two numbers")
