# Dulus AutoAdapter 🦅

Turn **any** Python repo, PyPI package, or MCP server into a working **native Dulus
plugin** with one command — powered by the *real* Dulus AutoAdapter engine.

This is not a text prompt that pretends to adapt code. The plugin ships an MCP server
that drives the actual Dulus engine: it clones the source, runs Dulus's multi-strategy
AI adapter, and **verifies the generated wrapper references the library's real
exports** (it fails loudly with `SCAFFOLD_ONLY` instead of shipping a fake stub).

## Install

```
/plugin marketplace add KevRojo/Dulus-Skills
/plugin install autoadapter@dulus-skills
```

## Use

The plugin exposes two MCP tools:

| Tool | What it does |
|---|---|
| `adapt_repo` | Adapt a repo/package/MCP server into a native Dulus plugin. Args: `source` (git URL, local path, or `name@gh`), optional `name`. |
| `autoadapter_status` | Check that Dulus is installed and how to configure a model provider. Run this first if `adapt_repo` fails. |

Just ask Claude: *"adapt https://github.com/sherlock-project/sherlock into a tool"* and
it will call `adapt_repo`. The generated plugin lands at `~/.dulus/plugins/<name>/`.

## Requirements

- **Python 3.10+** on `PATH` (the MCP server is stdlib-only; no extra packages).
- **Dulus** — installed automatically on first run, or `pip install dulus`.
- **A model provider** configured in Dulus: Anthropic, Gemini, OpenAI, the free
  **NVIDIA** tier, or local **Ollama**. Set it with `dulus -c "config model <model>"`.

## Running what it makes

The output is a **native Dulus plugin**, so you run it with Dulus:

```
dulus -c "plugin reload"
dulus -c "plugin list"
```

Get the full Dulus harness → https://github.com/KevRojo/DulusUnchainned

---

*Dulus is the Cigua Palmera, the national bird of the Dominican Republic 🇩🇴 — named
after the bird, not the rocket.*
