import asyncio
import json
import os
import sys
import uuid
from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional

try:
    from google.antigravity import Agent, LocalAgentConfig, CapabilitiesConfig
    AG_AVAILABLE = True
except ImportError:
    AG_AVAILABLE = False

app = FastAPI()

os.makedirs("static", exist_ok=True)
os.makedirs("temp", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

ag_agent = None
conversation_history = []
MAX_HISTORY = 100
oc_session_id = None
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


@app.on_event("startup")
async def startup():
    global ag_agent
    if AG_AVAILABLE:
        try:
            config = LocalAgentConfig(
                api_key=os.environ.get("ANTIGRAVITY_API_KEY", ""),
                capabilities=CapabilitiesConfig()
            )
            ag_agent = Agent(config)
            await ag_agent.__aenter__()
            print("[Nexus] Antigravity Agent initialized.", file=sys.stderr)
        except Exception as e:
            print(f"[Nexus] Antigravity init failed: {e}", file=sys.stderr)


@app.on_event("shutdown")
async def shutdown():
    global ag_agent
    if ag_agent:
        try:
            await ag_agent.__aexit__(None, None, None)
        except Exception:
            pass


@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/index.html", encoding="utf-8") as f:
        return f.read()


def build_context(new_message: str, agent_name: str) -> str:
    parts = [
        f"You are {agent_name} in a group chat with User and another AI agent ({'Antigravity' if agent_name == 'OpenCode' else 'OpenCode'}).",
        "Below is the full conversation history. Use it to understand context.",
        "---",
    ]
    for msg in conversation_history:
        parts.append(f"{msg['role']}: {msg['content']}")
    parts.append("---")
    parts.append(f"User: {new_message}")
    parts.append("")
    parts.append(f"Respond as {agent_name} based on the full context.")
    return "\n".join(parts)


@app.post("/api/message")
async def handle_message(
    message: str = Form(...),
    image: Optional[UploadFile] = File(None)
):
    global oc_session_id

    image_path = None
    if image and image.filename:
        ext = os.path.splitext(image.filename)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        image_path = os.path.join("temp", filename)
        with open(image_path, "wb") as f:
            f.write(await image.read())

    prompt = message
    if image_path:
        prompt += f"\n[Image: {os.path.abspath(image_path)}]"

    conversation_history.append({"role": "User", "content": prompt})
    if len(conversation_history) > MAX_HISTORY:
        conversation_history.pop(0)

    async def stream():
        queue = asyncio.Queue()
        active = 2

        async def run_oc(prompt_text):
            nonlocal active
            global oc_session_id
            try:
                ctx = build_context(prompt_text, "OpenCode")
                tempf = os.path.join("temp", f"oc_{uuid.uuid4().hex}.txt")
                with open(tempf, "w", encoding="utf-8") as f:
                    f.write(ctx)

                cmd = f'type "{tempf}" | opencode run --format json'
                if oc_session_id:
                    cmd = f'type "{tempf}" | opencode run --format json --session {oc_session_id}'

                proc = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=ROOT_DIR
                )

                buf = b""
                while True:
                    chunk = await proc.stdout.read(4096)
                    if not chunk:
                        break
                    buf += chunk
                    while b"\n" in buf:
                        line, buf = buf.split(b"\n", 1)
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            ev = json.loads(line.decode("utf-8"))
                            ev_type = ev.get("type")

                            if ev_type == "step_start":
                                sid = ev.get("sessionID") or ev.get("part", {}).get("sessionID")
                                if sid:
                                    oc_session_id = sid

                            if ev_type == "text":
                                t = ev.get("part", {}).get("text", "")
                                if t:
                                    await queue.put({"agent": "OpenCode", "text": t})
                        except json.JSONDecodeError:
                            pass

                stderr_data = await proc.stderr.read()
                if stderr_data:
                    print(f"[Nexus][OC stderr] {stderr_data.decode('utf-8', errors='replace')}", file=sys.stderr)

                await proc.wait()
            except Exception as e:
                print(f"[Nexus][OC error] {e}", file=sys.stderr)
                await queue.put({"agent": "OpenCode", "text": f"\n[OpenCode Error: {e}]"})
            finally:
                await queue.put({"agent": "OpenCode", "status": "complete"})
                await queue.put(None)
                active -= 1

        async def run_ag(prompt_text):
            nonlocal active
            if not ag_agent:
                await queue.put({"agent": "Antigravity", "text": "[Antigravity SDK unavailable]"})
                await queue.put({"agent": "Antigravity", "status": "complete"})
                await queue.put(None)
                active -= 1
                return
            try:
                ctx = build_context(prompt_text, "Antigravity")
                resp = await ag_agent.chat(ctx)
                async for token in resp:
                    if token:
                        await queue.put({"agent": "Antigravity", "text": token})
            except Exception as e:
                print(f"[Nexus][AG error] {e}", file=sys.stderr)
                await queue.put({"agent": "Antigravity", "text": f"\n[Antigravity Error: {e}]"})
            finally:
                await queue.put({"agent": "Antigravity", "status": "complete"})
                await queue.put(None)
                active -= 1

        asyncio.create_task(run_oc(prompt))
        asyncio.create_task(run_ag(prompt))

        oc_resp, ag_resp = "", ""
        while active > 0:
            item = await queue.get()
            if item is None:
                continue
            if item.get("status") == "complete":
                yield f"data: {json.dumps(item)}\n\n"
            else:
                t = item.get("text", "")
                if item["agent"] == "OpenCode":
                    oc_resp += t
                else:
                    ag_resp += t
                yield f"data: {json.dumps(item)}\n\n"

        if oc_resp.strip():
            conversation_history.append({"role": "OpenCode", "content": oc_resp.strip()})
        if ag_resp.strip():
            conversation_history.append({"role": "Antigravity", "content": ag_resp.strip()})
        if len(conversation_history) > MAX_HISTORY:
            conversation_history[:] = conversation_history[-MAX_HISTORY:]

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.post("/api/reset")
async def reset_conversation():
    global oc_session_id, conversation_history
    oc_session_id = None
    conversation_history.clear()
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
