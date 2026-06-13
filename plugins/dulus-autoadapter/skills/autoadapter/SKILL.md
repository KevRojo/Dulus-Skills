---
name: autoadapter
description: Turn any Python library or repository into native agent tools. Use when the user wants to wrap, adapt, or expose a Python repo/package as callable tools (a "plugin") — e.g. "adapt yfinance", "make tools from this repo", "wrap sherlock as a tool". Reads the real source, generates per-function wrappers, and verifies they actually call the library (a real-adaptation gate), never shipping a generic scaffold.
---

# AutoAdapter — adapt any Python repo into native agent tools

Born in [Dulus](https://github.com/KevRojo). The point that makes this different
from template stamping: **the model must actually wire the library's real
functions.** A wrapper that compiles and "runs" but never calls the target
library is a generic scaffold — a false success. This skill bakes in a gate
that rejects that.

## When to use
The user points at a Python package/repo (local path or git URL) and wants its
capabilities as callable tools. Examples: "adapt `yfinance`", "turn this repo
into tools", "wrap `sherlock`".

## Process

### 1. Analyze the source FIRST (do not skip)
- Read the README, `pyproject.toml`/`requirements.txt` for dependencies, and the
  main `.py` files (skip `tests/`, `docs/`, `venv/`, `build/`).
- With AST, list the **public** functions and classes the repo exports and the
  EXACT parameters each expects. Read the consumer code — never infer shapes from
  class names.
- Detect the library *type* to pick a starting structure (it only guides; you
  still write real code):
  - **library** → import functions directly (preferred)
  - **CLI tool** → `subprocess.run([sys.executable, "-m", pkg, ...])`
  - **web/API client** → call its endpoints
  - **TUI/rendering lib** → use OFFLINE render APIs only (stdout is captured, no TTY)
  - **file-generating** → return the output path

### 2. Generate `plugin_tool.py` — wrap the REAL functions
Write one tool per meaningful capability, calling the library's actual exported
functions/classes with their real parameters.

Required exports:
- `TOOL_DEFS`: list of `ToolDef(name, schema, func)` objects
- `TOOL_SCHEMAS = [t.schema for t in TOOL_DEFS]`
- Each tool: `func(params: dict, config: dict) -> str` — MUST return a string

Hard rules (each one is a real bug we hit):
- `params.get("key", default)` — never `params["key"]`
- `encoding="utf-8", errors="replace"` for all file/subprocess I/O
- No TTY: `Screen.play()`, `curses.initscr()` will crash — use offline APIs
- `True`/`False`/`None` only (never `true`/`false`/`null`)
- JSON Schema types only: string/integer/boolean/number/object/array (never "any")

### 3. Token-efficient output (non-negotiable)
A tool that dumps raw responses gets truncated and pollutes context. NEVER dump
`.info`, `.to_dict()`, full DataFrames, or `json.dumps()` of library objects.
Extract the 6–12 fields that matter, format as compact `key: value` lines or a
small table. Every list tool: `limit` (default 10) and `verbose` (default False).

```python
# BAD : return json.dumps(yf.Ticker(t).info)            # 8KB dump
# GOOD:
i = yf.Ticker(t).info
return (f"{t}: ${i['currentPrice']:.2f} "
        f"({i['regularMarketChangePercent']:+.2%}) | "
        f"MCap ${i['marketCap']/1e9:.1f}B | P/E {i.get('trailingPE','N/A')}")
```

### 4. Verify — including the real-adaptation gate
Run, in order:
1. **compiles** (no SyntaxError)
2. **imports** without runtime errors
3. **exports** `TOOL_DEFS` / `TOOL_SCHEMAS`
4. **ToolDef shape** (objects, not raw functions)
5. **🚪 real-adaptation gate**: the generated `plugin_tool.py` MUST reference at
   least one of the library's real exported names. If it references NONE, it is a
   generic scaffold, not an adaptation — **fail and rewrite** to call the real
   functions. (Skip only for pure-CLI repos with no importable exports.)
6. **smoke test**: each tool runs with default params and returns non-empty,
   non-error, non-bloated output.

If a check fails, read the actual source again and fix the specific issue — most
post-compile failures are TYPE-SHAPE mismatches (passing wrapper objects where a
function wanted a raw dict). Don't guess; read.

### 5. Emit `plugin.json`
`{"name", "version", "description", "dependencies": [<pip names>], "tools": ["plugin_tool"]}`
— `dependencies` is a flat list of strings.

## Definition of done
The tools import and call the **library's real functions**, pass the smoke test
with curated output, and clear the real-adaptation gate. If a tool only wraps a
generic "do anything" path and never touches the library, it is NOT done.
