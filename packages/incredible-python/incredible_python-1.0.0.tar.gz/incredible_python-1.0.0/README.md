# Incredible Python SDK

Drop-in replacement for the [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python) that speaks to the [Incredible API](https://incredible.one). The goal is plug-and-play migration: swap `anthropic.Anthropic` for `incredible_python.Incredible` and keep the rest of your code unchanged—function calling, streaming, token counting, and multi-step workflows included.

---

## Table of Contents
1. [Features](#features)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Quick Start](#quick-start)
5. [Function Calling](#function-calling)
6. [Streaming Responses](#streaming-responses)
7. [Token Counting](#token-counting)
8. [Cookbook Compatibility](#cookbook-compatibility)
9. [Testing & Development](#testing--development)
10. [Contributing](#contributing)
11. [License](#license)

---

## Features
- **Anthropic-compatible client**: identical constructor and method signatures where possible.
- **Function/tool calling**: pass `functions` (and `tools`) to `messages.create` and receive structured tool-use events.
- **Streaming support**: iterate over server-sent events that follow Anthropic semantics (`data: ...`, `[DONE]`).
- **Utility helpers**: helper functions to create `function_call` / `function_call_result` messages when you run tools locally.
- **Token counting**: call `client.messages.count_tokens(...)` to estimate usage before executing a request.
- **Cookbook-ready**: all examples in `Incredible-API-Cookbook-main/` can now be executed with this SDK.

---

## Installation

### From source (recommended during development)
```bash
# create and activate a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# install in editable mode
pip install -e .
```

### (Future) From PyPI
When the package is published you will be able to run:
```bash
pip install incredible-python
```

---

## Configuration
The client reads configuration from keyword arguments or environment variables—mirroring the Anthropic SDK.

| Setting        | Env Var                | Default                         |
| -------------- | ---------------------- | ------------------------------- |
| API key        | `INCREDIBLE_API_KEY`   | *(required)*                    |
| Base URL       | `INCREDIBLE_BASE_URL`  | `https://api.incredible.one`    |
| Timeout        | —                      | 600 seconds                     |
| Max retries    | —                      | 2 (with backoff)                |

```bash
export INCREDIBLE_API_KEY="your-secret-key"
```

---

## Quick Start
```python
from incredible_python import Incredible

client = Incredible()
response = client.messages.create(
    model="small-1",
    max_tokens=256,
    messages=[
        {"role": "user", "content": "Give me three startup ideas."}
    ],
)
print(response.content[0]["text"])
```

`response` is a rich object that exposes Anthropic-style properties:
```python
print(response.tool_calls)     # list of ToolCall objects (if any)
print(response.usage)          # token usage metadata (if provided)
print(response.stop_reason)    # e.g. "end_turn", "stop_sequence"
```

---

## Function Calling

Provide tool schemas via `functions`
> **Important:** If you need to work with large context (e.g., multi-megabyte datasets or long documents), register a function/tool that returns that data instead of pasting it directly into a message. The Incredible API assumes heavy payloads are fetched on demand via tool calls; injecting them into the prompt will overflow the current context window.

 (or `tools`) when calling `messages.create`. If the Incredible model decides to call your function, you can execute it locally and send a follow-up message using the helper utilities.

### Manual control
```python
from incredible_python import Incredible, helpers

client = Incredible()

functions = [
    {
        "name": "calculate_operation",
        "description": "Perform basic math",
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {"type": "string", "enum": ["add", "subtract", "multiply", "divide"]},
                "a": {"type": "number"},
                "b": {"type": "number"},
            },
            "required": ["operation", "a", "b"],
        },
    }
]

initial = client.messages.create(
    model="small-1",
    max_tokens=64,
    messages=[{"role": "user", "content": "What is 24 multiplied by 7?"}],
    functions=functions,
)

for call in initial.tool_calls:
    result_value = call.arguments["a"] * call.arguments["b"]
    function_result = helpers.make_tool_result(call.id, result_value)

    follow_up_messages = [
        {"role": "user", "content": "What is 24 multiplied by 7?"},
        helpers.make_tool_call(call.name, call.arguments, call_id=call.id),
        function_result,
    ]

    final = client.messages.create(
        model="small-1",
        max_tokens=128,
        messages=follow_up_messages,
        functions=functions,
    )
    print(final.content)
```

### Automated helper flow
When the model returns a `function_call` block you can offload the parsing and follow-up message creation to the helper utilities:

```python
from incredible_python import Incredible, helpers

client = Incredible()
registry = {
    "calculate_operation": lambda operation, a, b: eval(f"{a}{ {'add':'+','subtract':'-','multiply':'*','divide':'/' }[operation] }{b}"),
}

messages = [{"role": "user", "content": "Calculate 42 / 7."}]
response = client.messages.create(
    model="small-1",
    max_tokens=64,
    messages=messages,
    functions=list_registry_as_json_schema(...),  # supply your schemas as before
)

plan = helpers.build_tool_execution_plan(response.raw)
if plan and not plan.is_empty():
    results = helpers.execute_plan(plan, registry=registry)
    follow_up = helpers.build_follow_up_messages(messages, plan, results)
    final = client.messages.create(
        model="small-1",
        max_tokens=64,
        messages=follow_up,
        functions=list_registry_as_json_schema(...),
    )
    print(final.content)
```

> **Tip:** `execute_plan` takes care of running multiple tool calls in the order the model requested. `build_follow_up_messages` packages the results back into the canonical `function_call_result` format required by the API.

---

## Streaming Responses
```python
client = Incredible()
stream = client.messages.stream(
    model="small-1",
    max_tokens=256,
    messages=[{"role": "user", "content": "Stream a short poem about the ocean."}],
)

for event in stream.iter_lines():
    if event.get("content", {}).get("type") == "content_chunk":
        chunk = event["content"]["content"]
        print(chunk, end="", flush=True)
```

`StreamBuilder.iter_lines()` yields parsed JSON events; when the server sends `data: [DONE]` the iterator stops. Call `stream.close()` to release the network connection early if needed.

---

## Token Counting
```python
usage_estimate = client.messages.count_tokens(
    model="small-1",
    messages=[{"role": "user", "content": "Summarise this 1,000 word article."}],
)
print(usage_estimate)
```

> **Note:** The live Incredible API has not yet exposed `/v1/messages/count_tokens`, so this method will raise a 404 until the endpoint ships. The SDK keeps the method for future compatibility and mirrors Anthropic’s signature.

---

## Cookbook Compatibility
This SDK was validated against every scenario in **Incredible-API-Cookbook-main**:

- ✅ `01-getting-started/` – basic chat, conversations, streaming, function calling
- ✅ `02-function-calling/` – multiple tools, advanced multi-step workflows, JSON extraction, and more

To migrate an example:
1. Replace raw `requests.post(...)` calls with `client.messages.create(...)` or `client.messages.stream(...)`.
2. Use the helper utilities to create intermediate `function_call` / `function_call_result` messages when you execute tools locally.
3. Profit! No other structural changes are required.

---

## Testing & Development
```bash
# install dev dependencies
pip install -r requirements.txt

# run unit tests (add more as the SDK grows)
pytest

# run lint/format tools if configured (e.g. ruff, black)
```

The repository ships with a `.venv/` suggestion for isolation; feel free to use your own environment manager.

---

## Contributing
Pull requests are welcome! Please:
1. Fork & clone the repository.
2. Create a topic branch (`git checkout -b feat/awesome-improvement`).
3. Add tests for new functionality when possible.
4. Open a PR describing the change and cookbook scenarios it improves.

For major changes, open an issue first to discuss what you’d like to see.

---

## License
MIT License. See [LICENSE](LICENSE).

---

## Integrations

The SDK wraps the `/v1/integrations` endpoints so you can enumerate, connect, and execute third-party apps with just a few lines of code.

```python
client = Incredible()

# List available integrations
for integration in client.integrations.list():
    print(integration["id"], integration["name"])

# Fetch details for a specific integration
perplexity = client.integrations.retrieve("perplexity")
print(perplexity["features"])

# Connect a user (API key example)
client.integrations.connect(
    "perplexity",
    user_id="user_123",
    api_key="perplexity-secret",
)

# Execute a feature from a connected integration
result = client.integrations.execute(
    "perplexity",
    user_id="user_123",
    feature_name="PERPLEXITY_SEARCH",
    inputs={"query": "Latest AI news"},
)
print(result)
```

Supports both API key and OAuth flows via the same `connect` call—pass `api_key` or `callback_url` depending on the integration’s `auth_method`.

---

## Reference & Helpers

The SDK ships with helper utilities so you can mirror the cookbook patterns without manual parsing. Key modules:

- `helpers.build_tool_execution_plan(response.raw)` → parses the model’s requested tool calls.
- `helpers.execute_plan(plan, registry)` → runs your Python callables in order, returns results.
- `helpers.build_follow_up_messages(messages, plan, results)` → generates the follow-up `function_call`
  and `function_call_result` messages you can feed back to the model.

Example:

```python
from incredible_python import Incredible, helpers

client = Incredible()
response = client.messages.create(
    model="small-1",
    max_tokens=256,
    messages=[{"role": "user", "content": "Add 7 and 35, then look up taylor@example.com"}],
    functions=get_tool_schemas(),
)

plan = helpers.build_tool_execution_plan(response.raw)
if plan and not plan.is_empty():
    results = helpers.execute_plan(plan, registry=get_tool_registry())
    follow_up = helpers.build_follow_up_messages(response.raw["result"]["messages"], plan, results)
    final = client.messages.create(
        model="small-1",
        max_tokens=256,
        messages=follow_up,
        functions=get_tool_schemas(),
    )
```

See [`docs/python_sdk_helpers.md`](docs/python_sdk_helpers.md) for full argument tables and advanced patterns such as
wrapping the entire flow inside a reusable `run_agent_query()` helper.
