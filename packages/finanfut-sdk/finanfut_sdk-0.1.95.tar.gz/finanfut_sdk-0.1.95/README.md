# FinanFut Intelligence Python SDK

Official Python SDK for **FinanFut Intelligence**, a modular AI platform for agents, memory and orchestration.

This package provides a high-level client to interact with FinanFut Intelligence:
- Unified `interact` API for chat and actions
- Application and agent management
- Memory (settings + records)
- Contexts (documents & sessions)
- Billing & usage
- Async requests and developer analytics
- Optional CLI tool: `finanfut`

---

## Installation

```bash
pip install finanfut-sdk
```

Requires **Python >= 3.10**.

---

## Quickstart

```python
from finanfut_sdk import FinanFutClient

client = FinanFutClient(
    api_key="YOUR_API_KEY",
    application_id="YOUR_APPLICATION_ID",
)

response = client.interact.query("Hello! Schedule a meeting tomorrow at 10.")
print(response.answer)
```

---

## Configuration (optional)

### Local config file

```bash
mkdir -p ~/.finanfut
```

Create `~/.finanfut/config.json`:

```json
{
  "api_key": "YOUR_API_KEY",
  "application_id": "YOUR_APPLICATION_ID",
  "api_url": "https://api.finan.fut/intelligence"
}
```

Then:

```python
client = FinanFutClient()  # reads from config/env
```

### Environment variables supported

- `FINANFUT_API_KEY`
- `FINANFUT_APPLICATION_ID`
- `FINANFUT_API_URL`

---

## Using agents and intents

```python
# List agents
agents = client.agents.list()

for agent in agents:
    print(agent.name, agent.ai_model_id or "default model")

# Use a specific application agent and intent
response = client.interact.query(
    query="Add an event to my calendar.",
    application_agent_id="UUID_OF_APPLICATION_AGENT",
    intent_id="UUID_OF_INTENT",
)
print(response.answer)
```

`ai_model_id` reflects the catalog entry resolved by the backend and should be
used whenever you need to persist or audit the concrete model tied to an
agent.

---

## Memory API

```python
settings = client.memory.settings.get(application_id="APP_UUID")

records = client.memory.records.query(
    application_id="APP_UUID",
    application_agent_id="AGENT_UUID",
    query="What was the last scheduled event?"
)
```

---

## Billing & usage

```python
usage = client.billing.get_usage()
print("Total tokens used:", usage.tokens_used)
```

---

## CLI usage

```bash
finanfut init
finanfut interact "Hi!"
finanfut usage
```

---

## License

This project is licensed under the MIT License.
