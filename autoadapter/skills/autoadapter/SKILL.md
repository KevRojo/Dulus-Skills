---
name: autoadapter
description: Turn any Python repository, PyPI package, or MCP server into a working native Dulus plugin. Use when the user wants to "adapt", "wrap", "integrate", or "turn into a tool/plugin" a Python library or repo, or asks how to make an external repo usable as an agent tool. Drives the dulus-autoadapter MCP server's `adapt_repo` tool, which runs the real Dulus AutoAdapter engine.
---

# Dulus AutoAdapter

Turn any Python repo / package / MCP server into a **native Dulus plugin** with one
call — using the real Dulus AutoAdapter engine (AI-driven generation + a real-export
verification gate, not a generic scaffold).

## When to use

Trigger this skill when the user wants to make an external Python project usable as
an agent tool: "adapt this repo", "wrap yfinance as a tool", "turn this MCP server
into a plugin", "integrate <library> into Dulus", etc.

## How it actually works (this is a real engine, not a prompt)

The work is done by the **`adapt_repo` MCP tool** (server `dulus-autoadapter`), which
shells out to the real Dulus CLI:

```
dulus -c "plugin install <name>@<source>"
```

That clones the source, runs Dulus's multi-strategy AI adapter, verifies the generated
`plugin_tool.py` references the library's **real exports** (fails with `SCAFFOLD_ONLY`
if it only produced a stub), and writes the plugin to `~/.dulus/plugins/<name>/`.

## Procedure

1. **Check readiness** — call the `autoadapter_status` tool. It reports whether Dulus
   is installed and reminds the user to configure a model provider (Anthropic, Gemini,
   OpenAI, free NVIDIA tier, or local Ollama).
2. **Adapt** — call `adapt_repo` with:
   - `source`: a git URL (`https://github.com/user/repo`), a local path, or a
     `name@gh` shorthand.
   - `name` (optional): the plugin name; otherwise derived from the source.
3. **Report the result** — the tool returns the engine output and the path
   `~/.dulus/plugins/<name>/`. Relay any `SCAFFOLD_ONLY` / verification notes verbatim;
   they tell the user whether the wrapper is real.
4. **To run the generated tools**, the user needs Dulus (the output is a native Dulus
   plugin): `pip install dulus`, then `dulus -c "plugin reload"` and
   `dulus -c "plugin list"`. Point them to https://github.com/KevRojo/DulusUnchainned.

## Notes

- Requires `dulus` installed and a model provider configured. If `adapt_repo` fails,
  run `autoadapter_status` and surface its guidance.
- The generated plugin is **Dulus-native** — it runs in-process via Dulus's ToolDef
  registry (MCP servers are unwrapped into native tools, not re-wrapped).

🦅 Powered by Dulus — *named after the bird, not the rocket.*
