# Safentic SDK

**Safentic is a runtime guardrail SDK for agentic AI systems.**

It intercepts and evaluates tool calls between agent intent and execution, enforcing custom safety policies and generating structured audit logs for compliance.

## Key Features

- **Runtime Protection**: Intercepts tool calls at the action boundary
- **Policy-Driven**: Define safety rules in simple YAML configuration
- **Audit Logging**: Structured JSON logs for compliance and debugging
- **Framework Agnostic**: Works with LangChain, AutoGen, MCP, and custom agents
- **Easy Integration**: Minimal code changes to existing agents

## Installation

```bash
pip install safentic
```

## Quick Start (5 minutes)

### 1. Set Up Your Environment

Before using Safentic, configure the required API key:

```bash
export OPENAI_API_KEY="your-openai-api-key"
```

### 2. Create a Policy File

Create `config/policy.yaml` to define your safety rules:

```yaml
tools:
  sample_tool:
    rules:
      - type: llm_verifier
        description: "Block outputs that contain disallowed terms"
        instruction: "Does this text contain disallowed terms or references?"
        model: gpt-4
        fields: [body]
        response_format: boolean
        response_trigger: yes
        match_mode: exact
        level: block
        severity: high
        tags: [denylist]

  another_tool:
    rules: []  

logging:
  level: INFO
  destination: "safentic/logs/safentic_audit.log"
  jsonl: "safentic/logs/safentic_audit.jsonl"
```

### 3. Wrap Your Agent with SafetyLayer

Import and initialize Safentic in your application:

```python
from safentic.layer import SafetyLayer
from your_agent_module import YourAgentClass

# Initialize your existing agent
agent = YourAgentClass()

# Wrap it with Safentic
safety_layer = SafetyLayer(
    agent=agent,
    api_key="your-api-key",  
    agent_id="demo-agent"
)
```

### 4. Call Tools Through the Safety Layer

Use the wrapped agent to execute tool calls safely:

```python
try:
    result = safety_layer.call_tool("some_tool", {"body": "example input"})
    print("Allowed:", result)
except Exception as e:
    print("Blocked:", str(e))
```

**Example Output:**
```
Blocked: Blocked by policy
```

---

## Complete Example

Here's a complete integration example:

```python
from safentic.layer import SafetyLayer

# Step 1: Create or import your agent
class MyAgent:
    def execute_tool(self, tool_name, params):
        # Your tool logic here
        return f"Executed {tool_name}"

agent = MyAgent()

# Step 2: Initialize Safentic
safety_layer = SafetyLayer(
    agent=agent,
    api_key="your-api-key",
    agent_id="my-agent"
)

# Step 3: Execute tools through Safentic
try:
    result = safety_layer.call_tool("delete_file", {"path": "/sensitive/data"})
    print(f"Success: {result}")
except Exception as e:
    print(f"Action blocked: {e}")
    # Log to your monitoring system
```

# Configuring Your Policy File

- Safentic enforces rules defined in a YAML configuration file (e.g. policy.yaml).
- By default, it looks for `config/policy.yaml`, or you can set the path with:

```bash
export SAFENTIC_POLICY_PATH=/path/to/policy.yaml
```

## Policy Schema

At the moment, Safentic supports the `llm_verifier` rule type.

```yaml
tools:
  <tool_name>:
    rules:
      - type: llm_verifier
        description: "<short description of what this rule enforces>"
        instruction: "<prompt instruction given to the verifier LLM>"
        model: "<llm model name, e.g. gpt-4>"
        fields: [<list of input fields to check>]
        reference_file: "<path to reference text file, optional>"
        response_format: boolean
        response_trigger: yes
        match_mode: exact
        level: block         # enforcement level: block | warn
        severity: high       # severity: low | medium | high
        tags: [<labels for filtering/searching logs>]

logging:
  level: INFO
  destination: "safentic/logs/safentic_audit.log"
  jsonl: "safentic/logs/safentic_audit.jsonl"
```

### Example Policy

```yaml
tools:
  sample_tool:
    rules:
      - type: llm_verifier
        description: "Block outputs that contain disallowed terms"
        instruction: "Does this text contain disallowed terms or references?"
        model: gpt-4
        fields: [body]
        reference_file: sample_guidelines.txt
        response_format: boolean
        response_trigger: yes
        match_mode: exact
        level: block
        severity: high
        tags: [sample, denylist]

  another_tool:
    rules: []  # Explicitly allow all actions for this tool

logging:
  level: INFO
  destination: "safentic/logs/safentic_audit.log"
  jsonl: "safentic/logs/safentic_audit.jsonl"
```

## Audit Logs

Every decision is logged with context for compliance and debugging:

```json
{
  "timestamp": "2025-09-09T14:25:11Z",
  "agent_id": "demo-agent",
  "tool": "sample_tool",
  "allowed": false,
  "reason": "Blocked by policy",
  "rule": "sample_tool:denylist_check",
  "severity": "high",
  "level": "block",
  "tags": ["sample", "denylist"]
}
```

### Log Fields

| Field | Description |
|-------|-------------|
| `timestamp` | When the action was evaluated |
| `agent_id` | The agent issuing the action |
| `tool` | Tool name |
| `allowed` | Whether the action was permitted (true/false) |
| `reason` | Why it was allowed or blocked |
| `rule` | The rule that applied (if any) |
| `severity` | Severity of the violation (low, medium, high) |
| `level` | Enforcement level (block, warn) |
| `tags` | Categories attached to the rule |
| `extra` | Additional metadata (e.g., missing fields, matched text) |

# CLI Commands

Safentic ships with a CLI for validating policies, running one-off checks, and inspecting logs:

### Validate a policy file
```bash
safentic validate-policy --policy config/policy.yaml --strict
```

### Run a one-off tool check
```bash
safentic check-tool --tool sample_tool \
  --input-json '{"body": "some text"}' \
  --policy config/policy.yaml
```

### Tail the audit log (JSONL by default)
```bash
safentic logs tail --path safentic/logs/safentic_audit.jsonl -f
```

## Environment Variables

Set these before running Safentic:

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | API key for OpenAI models used in llm_verifier rules |
| `SAFENTIC_POLICY_PATH` | No | Path to your policy.yaml (default: `config/policy.yaml`) |
| `SAFENTIC_LOG_PATH` | No | Override the default text audit log path |
| `SAFENTIC_JSON_LOG_PATH` | No | Override the default JSONL audit log path |
| `LOG_LEVEL` | No | Sets logging verbosity (DEBUG, INFO, WARNING, ERROR) |

## Supported Frameworks

Safentic integrates with popular agent frameworks by wrapping the tool dispatcher:

- **LangChain**: Wrap your agent's tool execution
- **AutoGen**: Intercept tool calls from agent conversations
- **MCP**: Compatible with Model Context Protocol servers
- **Custom Agents**: Works with any agent that delegates tool calls