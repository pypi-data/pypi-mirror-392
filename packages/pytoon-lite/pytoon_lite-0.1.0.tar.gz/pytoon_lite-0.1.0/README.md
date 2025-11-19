# PyTOON 🧩

**PyTOON** is a lightweight, zero-dependency Python library for working with  
**TOON – Token-Oriented Object Notation**: a compact, human-readable encoding of the JSON data
model designed for LLM prompts.

Think of it as a **PyYAML-like API for TOON**:

- `load` / `loads` – parse TOON into native Python objects
- `dump` / `dumps` – encode Python objects into TOON
- `to_json` / `from_json` – easy round-trips with JSON strings

> ⚠️ PyTOON aims to be **small, minimal, and easy to read**, not yet a fully spec-compliant
> reference implementation. It focuses on the most common shapes used in LLM prompts:
> nested objects, arrays of primitives, and tabular arrays of objects.

For full spec details, see the official TOON spec and reference implementation.

---

## Features

- Minimal, **no runtime dependencies**
- Familiar **PyYAML-like API**
- Clean, readable TOON output suitable for LLM prompts
- Handles:
  - nested objects
  - arrays of primitives
  - **tabular arrays of uniform objects**, e.g.:

    ```toon
    users[2]{id,name,role}:
      1,Alice,admin
      2,Bob,user
    ```

- Simple integration with JSON:
  - `to_json(obj)` – JSON string
  - `from_json(json_str)` – Python object, ready for TOON encoding

---

## Installation

PyTOON is designed to play nicely with [`uv`](https://docs.astral.sh/uv/), but it’s a normal
PEP 621 package and works fine with `pip` as well.

```bash
# with uv (recommended for development)
uv add pytoon

# with pip
pip install pytoon
```

## Quick Start

### Basic Usage

```bash
from pytoon import loads, dumps

toon_text = """
context:
  task: Our favorite hikes together
  location: Boulder
  season: spring_2025

friends[3]: ana,luis,sam

hikes[3]{id,name,distanceKm,elevationGain,companion,wasSunny}:
  1,Blue Lake Trail,7.5,320,ana,true
  2,Ridge Overlook,9.2,540,luis,false
  3,Wildflower Loop,5.1,180,sam,true
"""

data = loads(toon_text)

assert data["context"]["location"] == "Boulder"
assert len(data["friends"]) == 3
assert data["hikes"][0]["name"] == "Blue Lake Trail"

# Modify and dump back to TOON
data["context"]["season"] = "summer_2026"
print(dumps(data))
```

### JSON Round-Trip

```bash
from pytoon import to_json, from_json, dumps

obj = {
    "users": [
        {"id": 1, "name": "Alice", "role": "admin"},
        {"id": 2, "name": "Bob", "role": "user"},
    ]
}

json_str = to_json(obj)
restored = from_json(json_str)
toon_text = dumps(restored)

print(toon_text)
```

Produces something like this:

```
users[2]{id,name,role}:
  1,Alice,admin
  2,Bob,user
```

### API

All functions live in the top-level `pytoon` package.

`loads(text: str) -> Any`

```
from pytoon import loads

data = loads("friends[2]: ana,luis")
# {'friends': ['ana', 'luis']}

```

`load(fp: IO[str]) -> Any`

```
from pytoon import load

with open("data.toon", "r", encoding="utf-8") as f:
    data = load(f)
```

## Development

Assuming you cloned this repository:

```bash
# Install dev dependencies with uv
uv sync

# Run tests
uv run pytest

# Lint
uv run ruff check src tests

# Type-check
uv run mypy src
```

## License
MIT. Use it, fork it, tweak it.


## FAQ

### Q: Why another TOON library when an official one exists?

PyTOON is intentionally:

- minimal (zero dependencies),

- educational (small readable codebase),

- and API-aligned with PyYAML-style workflows.

If you need strict conformance to every corner of the TOON spec and full fixtures support,
you should also look at the official TOON Python implementation. For quick integration into
LLM-heavy Python codebases with a familiar API, PyTOON aims to be a pleasant choice.