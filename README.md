# 🦅 Dulus Agentic Skills

Agentic skills & plugins from **[Dulus](https://github.com/KevRojo/DulusUnchainned)** —
the multi-provider AI agent harness. **Real engines, not text prompts.**

> Named after the bird, not the rocket. 🇩🇴

A Claude Code (and MCP-compatible) plugin marketplace. Add it once, install any plugin:

```
/plugin marketplace add KevRojo/Dulus-Skills
/plugin install autoadapter@dulus-skills
```

---

## ▶ Demo: AutoAdapter turns `yfinance` into native agent tools in < 30s

Dulus reads an unknown Python repo, an LLM writes real per-function tool wrappers,
and a **real-adaptation gate** refuses to ship a generic scaffold. No manifests,
no manual glue.

**[▶ Watch the demo (1:06)](demo/dulus-autoadapt-yfinance.mp4)**

---

## Plugins

### `autoadapter` — turn any repo into a working plugin ✅ available

Adapt any Python repo, PyPI package, or MCP server into a working **native Dulus
plugin** with one command. The plugin ships an MCP server that drives the **real**
Dulus AutoAdapter engine (the one in the demo) — AI generation + real-export
verification, **not a prompt**.

```
/plugin install autoadapter@dulus-skills
```

Then just ask Claude: *"adapt https://github.com/user/repo into a tool"*. See
[`./autoadapter`](./autoadapter) for details.

---

Built by [@KevRojox](https://x.com/KevRojox) · part of the Dulus journey.
`#dulusisgonnabetheway` 🦅💜🇩🇴
