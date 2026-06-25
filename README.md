# Dulus Agentic Skills

Agentic skills and plugins from **[Dulus](https://github.com/KevRojo/DulusUnchainned)**,
the multi-provider AI agent harness. These are real engines, not just prompt packs.

> Named after the bird, not the rocket.

A Claude Code and MCP-compatible plugin marketplace. Add it once, then install any plugin:

```text
/plugin marketplace add KevRojo/Dulus-Skills
/plugin install autoadapter@dulus-skills
```

---

## Demo: AutoAdapter turns `yfinance` into native agent tools in under 30 seconds

Dulus reads an unknown Python repo, an LLM writes real per-function tool wrappers,
and a real adaptation gate refuses to ship a generic scaffold. No manifests. No
manual glue.

[Watch the demo (1:06)](demo/dulus-autoadapt-yfinance.mp4)

---

## Plugins

### `autoadapter` - turn any repo into a working plugin

Adapt any Python repo, PyPI package, or MCP server into a working native Dulus
plugin with one command. The plugin ships an MCP server that drives the real
Dulus AutoAdapter engine shown in the demo: AI generation plus real export
verification, not a fake wrapper.

```text
/plugin install autoadapter@dulus-skills
```

Then ask Claude something like:

> adapt https://github.com/user/repo into a tool

See [`./autoadapter`](./autoadapter) for details.

---

Built by [@KevRojox](https://x.com/KevRojox) as part of the Dulus journey.
