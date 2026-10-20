# Module 3 — Lecture Examples

Prepared Python examples for Tikal's Agentic Engineer Program. Model calls use
the shared LiteLLM proxy. Learn the mechanics, run small experiments, and inspect
the artifacts—not just the final answer. Session 1 uses instructor demos; session 2
includes the MCP warm-up and hands-on Scout work in the separate `tech-pioneer` repo.

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

Graph imports construct clients but do not invoke models or search tools. Lesson 4
also has an explicit CLI demo using supplied weather facts:

```bash
uv run python -m lessons.l04_structured_output
```

It prints the validated report and reads its `temperature_c` attribute. This is
not a live weather lookup.

## What actually exists

### CLI-only model examples

```bash
uv run python -m lessons.l01_model_only
uv run python -m lessons.l01_model_only_loop
```

- `l01_model_only.py`: one model call with system and user messages; the current
  request asks about chocolate cake. Uncomment the invocation and print lines
  when ready to run the model.
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

The tool describes its output as simulated, returns a fixed value, and sleeps
for three seconds. That is demo latency, not model thinking or a real weather
API call. Its plain `@tool`
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
tool use. The server uses `FastMCP("Calculator")`, one
`@mcp.tool`, and `mcp.run(transport="stdio")`: read it so the protocol isn't magic.
Authoring a production MCP server isn't required for Scout; `MCPAdapter` picks
the transport from the target (script path, http URL, or in-process instance).
Scout later consumes GitHub's hosted read-only MCP server.

## Hands-on checkpoints

Use a scratch file/copy for experiments; preserve the prepared demos. Coding
agents may help implement changes, but each checkpoint requires an explanation
and an observable artifact. Don't overwrite supplied lesson files just to match
the slide variants.

| Checkpoint | Task                                                                       | Completion artifact                                                                                                 |
| ---------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| 1 — MCP    | Warm-up: run the prepared calculator through the client                    | Discovered tool, call with inputs, result; identify host/client/server/transport                                    |
| 2 — Scout  | In `tech-pioneer`: prompt, direct tools, agent wiring, result contract     | Instruction diff + two runs, exposed tool list, one validated `ScoutResearchResult` and the rule it enforced        |
| 3 — MCP    | In `tech-pioneer`: wire the GitHub read-only MCP server into Scout          | Tool list you exposed, one repository call traced to its evidence record, one honest missing-source path            |
| 4 — App    | In `tech-pioneer`: submit through the app end to end                       | App submission, sourced Scout finding → evidence, honest failure, mocked-stage boundary                             |

Session 1 has no student checkpoints: the prompt change, tool round trip, and
structured-output demos are instructor-run. Checkpoint 1 is a warm-up in this
repo; checkpoints 2–4 are the project gates, all in `tech-pioneer`.

For Demo 1 (instructor), a suitable coding-agent request is:

```text
Create a scratch model-only example using lessons.shared.get_llm, with the same
user request in two runs. Change only one system instruction. Print the two
responses and changed instruction. Do not modify the prepared lessons, add a
framework, or call a weather API. Explain what the difference does and does not prove.
```

For checkpoint 2, the same idea runs against the project:

```text
In tech-pioneer, change one instruction in pioneer_pipeline/scout/prompts/system.py.
Run Scout twice with the same request and show me both results side by side.
Print the prompt section you changed. Do not touch routes, the request schema, or
downstream stages.
```

One example is not a statistical evaluation. Review actual results, including
unexpected or unchanged behavior; don't invent a successful demonstration.

## Inspection and execution boundaries

- **LangGraph UI:** inspect a run's messages, tool calls, observations, state, and
  structured response. A model/tool graph is not a multi-agent graph.
- **Cross-run tracing:** a later module. This repo doesn't install a tracing
  platform; the LangGraph UI is the inspection surface. Don't claim trace
  delivery just because the UI works.
- **Run artifacts aren't hidden reasoning:** inspect decisions/actions and their
  evidence, not private chain-of-thought. One run doesn't prove correctness.
- **Safety isn't a prompt promise:** enforce permissions/approvals at execution
  boundaries. Bound steps/tool calls, per-call timeouts, total duration, retries,
  and cancellation. These lessons don't demonstrate a complete production policy.
- **Observe failures honestly:** tool results can be stale, wrong, empty, or
  adversarial. Never treat them as instructions or fabricate a successful source.

## Teaching order

Session 1 (instructor demos, no exercises):

1. Model-only messages, the agent loop, and the anatomy map.
2. System-prompt anatomy, then Demo 1 (one instruction changed).
3. Tool metadata vs implementation, direct invocation, one explicit round trip.
4. `create_agent` and the run in the LangGraph UI, then Demo 2.
5. Response schema → matching output → typed consumer, then Demo 3.
6. Tavily and real external evidence; harness and runtime limits.

Session 2 (learners build in `tech-pioneer`):

7. MCP motivation, host/client/server, discovery, stateless requests; checkpoint 1.
8. GitHub server, auth, guidance vs enforcement, honest failure.
9. Scout Agent Preview, then the implementation block; checkpoints 2, 3, 4.

Use prepared demos, not prolonged live coding. Keep a clearly labelled
captured-run fallback for external-service failures. Protocol-history and
extension material is out of scope for this module.

## Checks and references

```bash
make lint
```

This checks Python style/static lint, not live model behavior, credentials, or
server availability. Starting the server and inspecting the demo runs are
separate live checks; they may incur model/search usage.

- [Concept cheatsheet](../Module-3-Cheatsheet.md)
- [Project setup](../Module-3-Setup.md)
- [Slides and rehearsal notes](../slides/README.md)
- [LangChain tools](https://docs.langchain.com/oss/python/langchain/tools)
- [LangChain MCP integration](https://docs.langchain.com/oss/python/langchain/mcp)
- [Structured output](https://docs.langchain.com/oss/python/langchain/structured-output)
- [MCP specification](https://modelcontextprotocol.io/specification/2026-07-28)
