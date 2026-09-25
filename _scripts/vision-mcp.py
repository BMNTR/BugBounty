#!/usr/bin/env python3
"""Vision MCP server for text-only models.

Runs a minimal MCP (JSON-RPC over stdio) server exposing image description
and OCR tools backed by an OpenAI-compatible vision endpoint.

Provider resolution (env vars, or C:\\BugBounty\\.env):
  VISION_API_KEY                  -> generic key (requires VISION_BASE_URL/VISION_MODEL)
  GEMINI_API_KEY                  -> Gemini OpenAI-compat endpoint (gemini-2.5-flash)
  OPENAI_API_KEY + OPENAI_BASE_URL + OPENAI_MODEL -> any OpenAI-compatible endpoint

Stdlib only - no pip installs needed.
"""

import base64
import io
import json
import os
import re
import sys
import urllib.request
import urllib.error

VISION_TOOL_NAME = "vision_describe"
OCR_TOOL_NAME = "vision_ocr"

ENV_FILE_CANDIDATES = [
    os.path.join(os.path.expanduser("~"), ".config", "opencode", ".env"),
    os.path.join(os.path.expanduser("~"), ".env"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"),
]


def load_dotenv(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
    except OSError:
        pass


def get_env(key, default=None):
    if key not in os.environ:
        for candidate in ENV_FILE_CANDIDATES:
            load_dotenv(candidate)
    return os.environ.get(key, default)


def resolve_endpoint():
    vision_key = get_env("VISION_API_KEY")
    gemini_key = get_env("GEMINI_API_KEY")
    openai_key = get_env("OPENAI_API_KEY")

    if vision_key:
        return {
            "key": vision_key,
            "base": get_env("VISION_BASE_URL", "").rstrip("/"),
            "model": get_env("VISION_MODEL", ""),
        }
    if gemini_key:
        return {
            "key": gemini_key,
            "base": "https://generativelanguage.googleapis.com/v1beta/openai",
            "model": get_env("VISION_MODEL", "gemini-2.5-flash"),
        }
    if openai_key:
        return {
            "key": openai_key,
            "base": get_env("OPENAI_BASE_URL", "https://api.groq.com/openai/v1").rstrip("/"),
            "model": get_env("OPENAI_MODEL", ""),
        }
    return None


def encode_image(path):
    if not os.path.isfile(path):
        raise ValueError("File not found: %s" % path)
    size = os.path.getsize(path)
    if size <= 0 or size > 20 * 1024 * 1024:
        raise ValueError("File is empty or larger than 20 MB: %s" % path)
    with open(path, "rb") as fh:
        data = fh.read()
    mime = "image/png"
    lower = path.lower()
    if lower.endswith(".jpg") or lower.endswith(".jpeg"):
        mime = "image/jpeg"
    elif lower.endswith(".gif"):
        mime = "image/gif"
    elif lower.endswith(".webp"):
        mime = "image/webp"
    return "data:%s;base64,%s" % (mime, base64.b64encode(data).decode("ascii"))


def call_vision(path, prompt):
    ep = resolve_endpoint()
    if ep is None or not ep["key"]:
        raise RuntimeError(
            "No vision API key found. Set VISION_API_KEY, GEMINI_API_KEY, "
            "or OPENAI_API_KEY in C:\\BugBounty\\.env"
        )
    base_url = ep["base"]
    model = ep["model"]
    if not base_url or not model:
        raise RuntimeError("VISION_BASE_URL/VISION_MODEL (or OPENAI_MODEL) are required")
    data_url = encode_image(path)
    payload = {
        "model": model,
        "temperature": 0.1,
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ],
    }
    req = urllib.request.Request(
        base_url + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer %s" % ep["key"],
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError("Vision API HTTP %s: %s" % (exc.code, detail))
    except urllib.error.URLError as exc:
        raise RuntimeError("Vision API unreachable: %s" % exc.reason)
    try:
        choices = body.get("choices") or []
        return choices[0]["message"]["content"].strip()
    except (IndexError, KeyError, TypeError, AttributeError):
        raise RuntimeError("Unexpected vision API response: %s" % json.dumps(body)[:500])


def _trace(kind, payload):
    trace_path = get_env("VISION_MCP_DEBUG")
    if trace_path:
        try:
            line = ("%s %s\n" % (kind, payload)).encode("utf-8")
            with open(trace_path, "ab") as fh:
                fh.write(line)
        except OSError:
            pass


TOOL_DEFS = [
    {
        "name": VISION_TOOL_NAME,
        "description": (
            "Analyze an image file at the given absolute path and return a detailed "
            "text description. Use this when the user pastes or references a "
            "screenshot/image and you cannot see it directly. Optional prompt "
            "parameter customizes what to focus on."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Absolute path to the image file"},
                "prompt": {"type": "string", "description": "Optional instruction for what to focus on"},
            },
            "required": ["path"],
        },
    },
    {
        "name": OCR_TOOL_NAME,
        "description": (
            "Extract all visible text from an image file at the given absolute path "
            "(OCR). Use when the user shares a screenshot and you need the exact text."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Absolute path to the image file"},
            },
            "required": ["path"],
        },
    },
]


def write_message(obj):
    ordered = {}
    if "result" in obj:
        ordered["result"] = obj["result"]
    if "error" in obj:
        ordered["error"] = obj["error"]
    ordered["jsonrpc"] = obj.get("jsonrpc", "2.0")
    if "id" in obj:
        ordered["id"] = obj["id"]
    data = json.dumps(ordered, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n"
    sys.stdout.buffer.write(data)
    sys.stdout.buffer.flush()
    _trace("OUT", json.dumps(obj)[:400])


def read_message():
    while True:
        line = sys.stdin.buffer.readline()
        if not line:
            return None
        stripped = line.strip()
        if not stripped:
            continue
        match = re.match(rb"content-length:\s*(\d+)", stripped, re.IGNORECASE)
        if match:
            content_length = int(match.group(1))
            while True:
                header_line = sys.stdin.buffer.readline()
                if header_line is None:
                    return None
                if not header_line.strip():
                    break
            raw = sys.stdin.buffer.read(content_length)
            break
        if stripped.startswith(b"{"):
            raw = stripped
            break
    _trace("IN", raw[:400] if isinstance(raw, bytes) else str(raw)[:400])
    try:
        return json.loads(raw.decode("utf-8"))
    except (ValueError, TypeError):
        return None


def handle_request(msg):
    msg_id = msg.get("id")
    method = msg.get("method", "")
    if method == "initialize":
        return {
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "vision-mcp", "version": "1.0.0"},
            },
        }
    if method == "notifications/initialized":
        return None
    if method == "tools/list":
        return {"id": msg_id, "result": {"tools": TOOL_DEFS}}
    if method == "tools/call":
        params = msg.get("params") or {}
        tool_name = params.get("name", "")
        args = params.get("arguments") or {}
        path = args.get("path", "")
        try:
            if tool_name == VISION_TOOL_NAME:
                prompt = args.get("prompt", "") or (
                    "Describe this image in detail: layout, visible text, "
                    "colors, and notable elements. Be precise and factual."
                )
                text = call_vision(path, prompt)
            elif tool_name == OCR_TOOL_NAME:
                text = call_vision(path, "Extract and return ALL visible text in this image verbatim.")
            else:
                raise ValueError("Unknown tool: %s" % tool_name)
            return {
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": text}],
                    "isError": False,
                },
            }
        except Exception as exc:  # noqa: BLE001 - surface every failure to the model
            return {
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": "ERROR: %s" % exc}],
                    "isError": True,
                },
            }
    return {"id": msg_id, "result": {}}


def main():
    _trace("BOOT", "vision-mcp started, python %s" % sys.version.split()[0])
    while True:
        msg = read_message()
        if msg is None:
            _trace("BOOT", "stdin EOF, exiting")
            break
        response = handle_request(msg)
        if response is not None:
            write_message(response)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as exc:  # noqa: BLE001
        try:
            write_message({"result": {"content": [{"type": "text", "text": "FATAL: %s" % exc}]}})
        except Exception:
            pass
