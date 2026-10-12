"""Minimal agent: Claude API + 3 tools + a tool_use loop."""
import json, logging, os, subprocess, sys
import anthropic

MODEL = os.environ.get("AGENT_MODEL", "claude-sonnet-5-5")
MAX_STEPS = 10
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("agent")

TOOLS = [
    {"name": "read_file", "description": "Read a text file.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    {"name": "search", "description": "Find lines containing the text in files under a directory (recursive).",
     "input_schema": {"type": "object", "properties": {"query": {"type": "string"},
                      "path": {"type": "string", "default": "."}}, "required": ["query"]}},
    {"name": "run_command", "description": "Run a shell command (requires user confirmation).",
     "input_schema": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}},
]


def read_file(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()[:20000]


def search(query, path="."):
    hits = []
    for root, _, files in os.walk(path):
        for name in files:
            p = os.path.join(root, name)
            try:
                for i, line in enumerate(open(p, encoding="utf-8", errors="ignore"), 1):
                    if query in line:
                        hits.append(f"{p}:{i}: {line.strip()}")
            except OSError:
                continue
            if len(hits) >= 50:
                return "\n".join(hits)
    return "\n".join(hits) or "no matches found"


def run_command(command):
    if input(f"\nRun `{command}`? [y/N] ").strip().lower() != "y":
        return "The user declined the command."
    r = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
    return f"exit={r.returncode}\n{r.stdout[-5000:]}{r.stderr[-2000:]}"


HANDLERS = {"read_file": read_file, "search": search, "run_command": run_command}


def run_tool(name, args):
    log.info("tool %s %s", name, json.dumps(args, ensure_ascii=False))
    try:
        return HANDLERS[name](**args), False
    except Exception as e:
        return f"Error: {e}", True


def agent(task):
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": task}]
    for step in range(1, MAX_STEPS + 1):
        resp = client.messages.create(model=MODEL, max_tokens=4096, tools=TOOLS, messages=messages)
        log.info("step %d stop_reason=%s", step, resp.stop_reason)
        messages.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason != "tool_use":
            return "".join(b.text for b in resp.content if b.type == "text")
        results = []
        for b in resp.content:
            if b.type == "tool_use":
                out, err = run_tool(b.name, b.input)
                results.append({"type": "tool_result", "tool_use_id": b.id, "content": out, "is_error": err})
        messages.append({"role": "user", "content": results})
    return f"Stopped: reached the limit of {MAX_STEPS} steps."


if __name__ == "__main__":
    if sys.argv[1:] == ["--dry-run"]:
        print(run_tool("search", {"query": "def agent", "path": os.path.dirname(__file__) or "."})[0])
    else:
        print(agent(" ".join(sys.argv[1:]) or input("Task: ")))
