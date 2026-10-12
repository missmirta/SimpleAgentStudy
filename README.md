# Minimal agent

Python, about 80 lines. Tools: `read_file`, `search`, `run_command`. A 10-step limit, a log entry for every call, and a confirmation prompt before every command.

## Running

```bash
pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...
python agent.py "Find all TODOs in this directory and summarize them"
```

Check without a key (tools only, no API call): `python agent.py --dry-run`

The default model is `claude-sonnet-5-5`; set another one with `AGENT_MODEL`, for example `AGENT_MODEL=claude-opus-5-5`.

## How it works

1. Send the task and the tool descriptions to `messages.create`.
2. If `stop_reason == "tool_use"`, run each `tool_use` block and send back a `tool_result`.
3. Repeat until the model finishes its answer or `MAX_STEPS` is reached.
