# Minimal agent

Python, about 80 lines. Tools: `read_file`, `search`, `run_command`. A 10-step limit, a log entry for every call, and a confirmation prompt before every command.

SimpleAgentStudy is a minimal AI agent in Python, about 80 lines in a single file (agent.py). It uses the Anthropic API and gives the model three tools: read_file, search and run_command. It has a few safety guardrails: a 10-step limit, a log entry for every tool call, and a confirmation prompt before any shell command runs. You run it with a task like python agent.py "Find all TODOs in this directory and summarize them". There is also a --dry-run mode that checks the tools without an API key.

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
