#!/usr/bin/env python3
"""Dulus AutoAdapter — MCP server.

Bridges Claude Code (or any MCP host) to the REAL Dulus AutoAdapter engine.
This is NOT a prompt that pretends to adapt code: the `adapt_repo` tool shells
out to the actual `dulus` CLI (`dulus -c "plugin install <name>@<source>"`),
which clones the repo, runs the AI-driven adapter (multi-strategy analysis +
real-export verification gate + fix loop), and writes a native Dulus plugin to
`~/.dulus/plugins/<name>/`. Powered by Dulus 🦅 — https://github.com/KevRojo/DulusUnchainned

Transport: MCP stdio (newline-delimited JSON-RPC 2.0). Stdlib only — the server
itself needs no third-party packages. `dulus` is required only to RUN an
adaptation, and the server installs/locates it lazily.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys

SERVER_NAME = "dulus-autoadapter"
SERVER_VERSION = "0.1.0"
DEFAULT_PROTOCOL = "2025-06-18"

# Adaptation can take a while (clone + AI generation + verification fix loop).
ADAPT_TIMEOUT_SEC = int(os.environ.get("DULUS_ADAPT_TIMEOUT", "600"))


# ── stdio JSON-RPC plumbing ──────────────────────────────────────────────────

def _send(msg: dict) -> None:
    """Write one newline-delimited JSON-RPC message to stdout."""
    sys.stdout.write(json.dumps(msg, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def _result(req_id, result: dict) -> None:
    _send({"jsonrpc": "2.0", "id": req_id, "result": result})


def _error(req_id, code: int, message: str) -> None:
    _send({"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}})


def _text_result(req_id, text: str, is_error: bool = False) -> None:
    """tools/call result: a single text content block."""
    _result(req_id, {"content": [{"type": "text", "text": text}], "isError": is_error})


# ── Dulus engine bridge ──────────────────────────────────────────────────────

def _dulus_base() -> list[str] | None:
    """Return the argv prefix that runs the Dulus CLI, or None if unavailable.

    Prefers `python -m dulus` with the current interpreter (so it shares the
    env the server was launched in), then a `dulus` entry point on PATH.
    """
    try:
        probe = subprocess.run(
            [sys.executable, "-c", "import dulus"],
            capture_output=True, timeout=30,
        )
        if probe.returncode == 0:
            return [sys.executable, "-m", "dulus"]
    except Exception:
        pass
    found = shutil.which("dulus")
    if found:
        return [found]
    return None


def _ensure_dulus() -> tuple[list[str] | None, str]:
    """Locate Dulus; if missing, try a one-time `pip install dulus`."""
    base = _dulus_base()
    if base:
        return base, ""
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--quiet", "dulus"],
            capture_output=True, timeout=ADAPT_TIMEOUT_SEC,
        )
    except Exception as exc:
        return None, f"Dulus is not installed and auto-install failed: {exc}"
    base = _dulus_base()
    if base:
        return base, ""
    return None, (
        "Dulus is not installed. Install it with `pip install dulus`, then retry. "
        "Docs: https://github.com/KevRojo/DulusUnchainned"
    )


def _derive_name(source: str) -> str:
    """Pick a safe plugin name from a repo URL / path / shorthand."""
    s = source.strip()
    if "@" in s and not s.startswith(("http", "git@", "/", ".")):
        # already `name@source` form — caller handles that, but be safe
        s = s.split("@", 1)[0]
    s = s.rstrip("/")
    if s.endswith(".git"):
        s = s[:-4]
    tail = re.split(r"[\\/]", s)[-1] or "adapted_plugin"
    name = re.sub(r"[^a-zA-Z0-9_]", "_", tail.lower()).strip("_")
    return name or "adapted_plugin"


def _run_dulus(base: list[str], dulus_cmd: str, timeout: int) -> tuple[int, str]:
    """Run `dulus -c "<dulus_cmd>"` and return (returncode, combined_output)."""
    env = dict(os.environ)
    env.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        proc = subprocess.run(
            base + ["-c", dulus_cmd],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=timeout, env=env,
        )
    except subprocess.TimeoutExpired:
        return 124, f"Timed out after {timeout}s running: dulus -c \"{dulus_cmd}\""
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, out


def _truncate(text: str, limit: int = 6000) -> str:
    if len(text) <= limit:
        return text
    return text[-limit:] + f"\n…(output truncated to last {limit} chars)"


# ── Tools ────────────────────────────────────────────────────────────────────

def tool_adapt_repo(args: dict) -> tuple[str, bool]:
    source = (args.get("source") or "").strip()
    if not source:
        return ("Error: `source` is required (a git URL, local path, or `name@gh` shorthand).", True)
    name = (args.get("name") or "").strip() or _derive_name(source)
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name.lower()).strip("_") or "adapted_plugin"

    base, msg = _ensure_dulus()
    if base is None:
        return (msg, True)

    identifier = source if "@" in source and not source.startswith(("http", "git@", "/", ".")) else f"{name}@{source}"
    rc, out = _run_dulus(base, f"plugin install {identifier}", ADAPT_TIMEOUT_SEC)
    home = os.path.expanduser("~")
    plugin_path = os.path.join(home, ".dulus", "plugins", name)
    header = (
        f"AutoAdapter run for `{source}` (plugin name: `{name}`)\n"
        f"Generated Dulus plugin → {plugin_path}\n"
        f"Engine exit code: {rc}\n"
        "Powered by the real Dulus AutoAdapter 🦅\n"
        "── engine output ──\n"
    )
    is_error = rc != 0
    if not is_error:
        header += (
            "\nThe output above is a NATIVE DULUS plugin. To run its tools, use Dulus:\n"
            f"  dulus -c \"plugin list\"   and   dulus -c \"plugin reload\"\n"
            "Get Dulus: https://github.com/KevRojo/DulusUnchainned\n\n"
        )
    return (header + _truncate(out), is_error)


def tool_autoadapter_status(_args: dict) -> tuple[str, bool]:
    base = _dulus_base()
    if base is None:
        return (
            "Dulus: NOT installed.\n"
            "Install with `pip install dulus`. The adapter needs Dulus to run the\n"
            "real engine and a configured model provider (any of: Anthropic, Gemini,\n"
            "OpenAI, free NVIDIA, or local Ollama). Docs: "
            "https://github.com/KevRojo/DulusUnchainned",
            False,
        )
    rc, out = _run_dulus(base, "version", 120)
    model_hint = (
        "\nThe AutoAdapter uses the model in your Dulus config "
        "(`dulus -c \"config model <model>\"`). Free options: NVIDIA tier or local Ollama."
    )
    status = "installed and importable" if rc == 0 else f"installed but `version` exited {rc}"
    return (f"Dulus: {status}.\n{_truncate(out, 1500)}{model_hint}", False)


TOOLS = [
    {
        "name": "adapt_repo",
        "description": (
            "Adapt a Python repository, package, or MCP server into a native Dulus plugin "
            "using the REAL Dulus AutoAdapter engine (AI-driven generation + real-export "
            "verification, not a scaffold). Clones the source, generates plugin_tool.py + "
            "plugin.json under ~/.dulus/plugins/<name>/, and verifies it. Requires `dulus` "
            "installed and a model provider configured."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "source": {
                    "type": "string",
                    "description": "Git URL (https://github.com/user/repo), local path, or `name@gh` shorthand to adapt.",
                },
                "name": {
                    "type": "string",
                    "description": "Optional plugin name. Defaults to a safe name derived from the source.",
                },
            },
            "required": ["source"],
        },
    },
    {
        "name": "autoadapter_status",
        "description": (
            "Check whether Dulus is installed and ready to run adaptations, and how to "
            "configure a model provider. Use this first if adapt_repo fails."
        ),
        "inputSchema": {"type": "object", "properties": {}},
    },
]

_DISPATCH = {
    "adapt_repo": tool_adapt_repo,
    "autoadapter_status": tool_autoadapter_status,
}


# ── MCP request handling ─────────────────────────────────────────────────────

def _handle(msg: dict) -> None:
    method = msg.get("method")
    req_id = msg.get("id")
    is_request = req_id is not None

    if method == "initialize":
        params = msg.get("params") or {}
        proto = params.get("protocolVersion") or DEFAULT_PROTOCOL
        _result(req_id, {
            "protocolVersion": proto,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
        })
        return

    if method in ("notifications/initialized", "initialized"):
        return  # notification — no response

    if method == "ping":
        if is_request:
            _result(req_id, {})
        return

    if method == "tools/list":
        _result(req_id, {"tools": TOOLS})
        return

    if method == "tools/call":
        params = msg.get("params") or {}
        tool_name = params.get("name")
        args = params.get("arguments") or {}
        fn = _DISPATCH.get(tool_name)
        if fn is None:
            _error(req_id, -32602, f"Unknown tool: {tool_name}")
            return
        try:
            text, is_error = fn(args)
        except Exception as exc:  # never let a tool crash the server
            _text_result(req_id, f"AutoAdapter tool error: {exc}", is_error=True)
            return
        _text_result(req_id, text, is_error=is_error)
        return

    # Unknown method
    if is_request:
        _error(req_id, -32601, f"Method not found: {method}")


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except Exception:
            continue
        if isinstance(msg, dict):
            try:
                _handle(msg)
            except Exception as exc:
                rid = msg.get("id")
                if rid is not None:
                    _error(rid, -32603, f"Internal error: {exc}")


if __name__ == "__main__":
    main()
