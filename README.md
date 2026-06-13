# 🦅 Dulus Agentic Skills

Agentic skills and plugins from **[Dulus](https://github.com/KevRojo)** — the multi-provider AI agent harness.

> Named after the bird, not the rocket. 🇩🇴

---

## ▶ Demo: AutoAdapter turns `yfinance` into native agent tools in < 30s

Dulus reads an unknown Python repo, detects its type, and an LLM writes real
per-function tool wrappers — with a **real-adaptation gate** that refuses to ship
a generic scaffold. No manifests, no manual glue.

**[▶ Watch the demo (1:06)](demo/dulus-autoadapt-yfinance.mp4)** — Dulus auto-adapting `yfinance` live.

---

## What's here

This is a **Claude Code plugin marketplace**. Add it and install Dulus's agentic
skills straight into your workflow:

```bash
claude plugin marketplace add KevRojo/Dulus-Skills
claude plugin install dulus-autoadapter@dulus-skills
```

### The flagship: AutoAdapter
Point it at *any* Python repo → it becomes native agent tools. The difference from
a template stamp: **the AI actually wires the library's real functions**, and a
verification gate fails any wrapper that doesn't (so you never ship a placeholder).

---

## Roadmap
- [x] AutoAdapter demo (yfinance, < 30s)
- [ ] `dulus-autoadapter` skill packaged for Claude Code
- [ ] Profiles, skill-marketplace browsing, and Composio onboarding skills
- [ ] Submit to the official Anthropic plugin marketplace

---

Built by [@KevRojox](https://x.com/KevRojox) · part of the Dulus journey. 🦅💜🇩🇴
