# Module 3 — Lecture Examples

Prepared Python examples for Tikal's Agentic Engineer Program. Model calls use
the shared LiteLLM proxy. Learn the mechanics, run small experiments, and inspect
the artifacts—not just the final answer. Hands-on work is interleaved through
both sessions; Scout integration happens in the separate `tech-pioneer` repo.

## Setup and run

Requires Python 3.11+, [uv](https://docs.astral.sh/uv/), and `make`. Run these
commands **from `module-3-examples`**:

```bash
make setup
# Edit .env: LITELLM_API_KEY and TAVILY_API_KEY.
make dev
```

`make setup` installs dependencies and creates `.env` only if it doesn't exist.
Get the LiteLLM key from the course team and a Tavily key from
[Tavily](https://app.tavily.com). Add missing variables manually to an existing
`.env`. Never commit keys or show them in errors/screenshots.

Optional configuration:

- `BALANCED_MODEL`: a bare model name accepted by the course proxy. Tools require
  tool-calling support; lesson 4 also needs native structured-output support.
- `LITELLM_PROXY_URL`: override the proxy URL if instructed by the course team.

All registered graphs load together. The current modules construct model clients
at import time, and the Tavily lesson requires its key to load. Have both keys
configured even if you initially select only the weather graph. Tavily searches
use your account's quota.

**Current demo limitation:** `l04_structured_output.py` also invokes the model and
prints an invented-weather result while the module loads. Server startup can
therefore make a model request, incur usage, or fail before you invoke a graph.
That output isn't a live weather lookup or the result of a later Studio message.
Use supplied facts for the structured-output exercise below.

## What actually exists

### CLI-only model examples

```bash
uv run python -m lessons.l01_model_only
uv run python -m lessons.l01_model_only_loop
```

- `l01_model_only.py`: one model call with system and user messages; the current
  request asks about chocolate cake. It prints the assistant response.
- `l01_model_only_loop.py`: interactive chat history. Type `exit` to stop.
  A conversation loop is not a tool-use loop.

Neither script exports a registered Studio graph. For the lecture's common
weather narrative, use the supplied-weather request from the slides in a scratch
copy; don't mistake a teaching variant for the exact checked-in file.

### Studio graphs

Open the Studio URL printed by `make dev`. This table matches `langgraph.json`:

| Graph ID                | Source                             | Concept                                                   |
| ----------------------- | ---------------------------------- | --------------------------------------------------------- |
| `l02-react-loop`        | `lessons/l02_react_loop.py`        | `create_agent` with a simulated weather tool              |
| `l04-structured-output` | `lessons/l04_structured_output.py` | Pydantic response contract via `ProviderStrategy`         |
| `l05-mcp`               | `lessons/l05_mcp.py`               | Discover and call a tool from a prepared local MCP server |
| `l06-tavily`            | `lessons/l06_tavily.py`            | Direct remote search through a prebuilt Tavily tool       |

There is **no lesson 3** and no handwritten agent-loop implementation in the
current lesson set. Lesson 2 already uses `create_agent`. In the lecture, expose
one model → tool call → observation → next model call round trip before showing
the framework abstraction; don't write a second framework live.

## Demo inputs and what to inspect

In Chat mode send the text; in Graph mode use a `messages` object as below.
Exact tool-call sequences and wording may differ between runs.

### Weather tool — `l02-react-loop`

```json
{ "messages": [{ "role": "user", "content": "What's the weather in Lisbon?" }] }
```

Inspect the assistant's `get_weather` request, the `city` argument, the matching
tool result, and the subsequent assistant response. The application executes the
function; the model only requests it.

The tool returns a fixed simulated value and sleeps for three seconds. That is
demo latency, not model thinking or a real weather API call. Its plain `@tool`
doesn't parse `Args` text into per-field descriptions by default; the slides show
an improved teaching variant with `@tool(parse_docstring=True)` and no sleep.
The Python `-> str` annotation is not automatically a model-facing output schema.

Inspect the existing tool without a model invocation (requires the configured
LiteLLM key because importing the module constructs its agent):

```bash
uv run python -c 'from lessons.l02_react_loop import get_weather; print(get_weather.name); print(get_weather.description); print(get_weather.args_schema.model_json_schema()); print(get_weather.invoke({"city": "Lisbon"}))'
```

Try omitting the city in another request. It may ask for clarification, but the
current generic system prompt doesn't guarantee that behavior. To require it,
test an explicit instruction in a scratch variant. Clarification isn't an enforced
HITL approval gate.

### Structured result — `l04-structured-output`

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Lisbon is sunny and 22°C. Outdoor work is comfortable. Return a weather report."
    }
  ]
}
```

Inspect `structured_response`, not a prose paragraph:

```json
{ "city": "Lisbon", "temperature_c": 22, "is_workable_outdoors": true }
```

The schema uses required string/integer/boolean fields and descriptive guidance.
The parsed Python result is a `WeatherReport`; application code reads attributes
such as `report.temperature_c`. The schema doesn't establish that weather is
accurate or that outdoor work is safe. There is no weather lookup in this lesson.

`ProviderStrategy` requires a compatible provider/model/proxy route. A schema
passed directly lets LangChain choose a compatible strategy; `ToolStrategy` uses
tool calling to collect a structured result. JSON mode alone doesn't enforce the
schema. Surface compatibility/validation failures honestly instead of promising
that changing strategies always succeeds or always fails.

### Real search — `l06-tavily`

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Search for the latest LangGraph release. Summarize the changes and cite source URLs."
    }
  ]
}
```

`TavilySearch(max_results=3)` already supplies its tool description and schema;
no custom decorator or MCP server is needed. Inspect the returned sources and
check whether the answer follows from them. Direct/native integration still
depends on a network, credentials, and service availability.

### MCP — `l05-mcp`

```json
{
  "messages": [
    { "role": "user", "content": "Use the tool to add 123 and 456." }
  ]
}
```

`mcp_server.py` is a prepared calculator exposing `add(a, b)`. The async graph
factory uses `MCPAdapter` to start it as a local stdio subprocess, discover tools,
and keep the connection open while the agent runs. No separate server command,
port, or arithmetic API key is needed; the model still uses LiteLLM.

Identify the host, client, server, and transport. Follow discovery → selected
tool/arguments → observation → response. The answer `579` alone is not proof of
tool use. Students consume this server; authoring a production MCP server isn't
required for Scout. Scout later consumes GitHub's hosted read-only MCP server.

## Hands-on checkpoints

Use a scratch file/copy for experiments; preserve the prepared demos. Coding
agents may help implement changes, but each checkpoint requires an explanation
and an observable artifact. Don't overwrite supplied lesson files just to match
the slide variants.

| Checkpoint   | Task                                                                                 | Completion artifact                                                                                                 |
| ------------ | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------- |
| 1 — Prompt   | Keep one request fixed; change one role/purpose, rule/boundary, or style instruction | Before/after responses and the exact changed instruction                                                            |
| 2 — Tool     | Invoke weather directly, inspect its definition, then run the agent                  | Name + args, matched tool result, next response; identify who executed the code                                     |
| 3 — Contract | Supply weather facts and inspect the typed result                                    | Named fields/types and an explanation of what validation cannot prove                                               |
| 3b — Design  | Decide tool vs application code for one Scout capability; draft its contract         | Name, description, inputs, returned data, failure behavior, and boundary rationale; no code required                |
| 4a — MCP     | Run the prepared calculator through the client                                       | Discovered tool, call with inputs, result; identify host/client/server/transport                                    |
| 4b — Scout   | Complete the module in `tech-pioneer`                                                | App submission, sourced Scout finding, observable run, honest missing-source/failure example, mocked-stage boundary |

For checkpoint 1, a suitable coding-agent request is:

```text
Create a scratch model-only example using lessons.shared.get_llm, with the same
user request in two runs. Change only one system instruction. Print the two
responses and changed instruction. Do not modify the prepared lessons, add a
framework, or call a weather API. Explain what the difference does and does not prove.
```

One example is not a statistical evaluation. Review actual results, including
unexpected or unchanged behavior; don't invent a successful demonstration.

## Inspection and execution boundaries

- **Studio:** inspect a run's messages, tool calls, observations, state, and
  structured response. A model/tool graph is not a multi-agent graph.
- **LangFuse:** separate instrumentation for tracing/monitoring across runs.
  This repo currently neither installs nor wires LangFuse. Don't claim trace
  delivery just because Studio works. Baseline Scout tracing is a course goal,
  not a demonstrated feature of these lessons.
- **Traces aren't hidden reasoning:** inspect decisions/actions and their
  evidence, not private chain-of-thought. A trace alone doesn't prove correctness.
- **Safety isn't a prompt promise:** enforce permissions/approvals at execution
  boundaries. Bound steps/tool calls, per-call timeouts, total duration, retries,
  and cancellation. These lessons don't demonstrate a complete production policy.
- **Observe failures honestly:** tool results can be stale, wrong, empty, or
  adversarial. Never treat them as instructions or fabricate a successful source.

## Teaching order

1. Model-only messages, then system-prompt anatomy and checkpoint 1.
2. Tool metadata vs implementation; direct invocation; one explicit round trip.
3. `create_agent`, runtime/harness boundaries, limits; checkpoint 2.
4. Response schema → matching output → typed consumer; checkpoint 3.
5. Tavily and observable execution with real external evidence.
6. MCP motivation and the prepared calculator; checkpoint 4a.
7. GitHub, security/failure boundaries, and Scout app integration; checkpoint 4b.

Use prepared demos, not prolonged live coding. Pause for guided practice in both
sessions. Keep a clearly labelled captured-run fallback for external-service
failures. Protocol-history/extension material is optional, not a prerequisite.

## Checks and references

```bash
make lint
```

This checks Python style/static lint, not live model behavior, credentials, or
server availability. Starting the server and inspecting the checkpoint runs are
separate live checks; they may incur model/search usage.

- [Concept cheatsheet](../Module-3-Cheatsheet.md)
- [Project setup](../Module-3-Setup.md)
- [Slides and rehearsal notes](../slides/README.md)
- [LangChain tools](https://docs.langchain.com/oss/python/langchain/tools)
- [Structured output](https://docs.langchain.com/oss/python/langchain/structured-output)
- [MCP specification](https://modelcontextprotocol.io/specification/2026-07-28)
