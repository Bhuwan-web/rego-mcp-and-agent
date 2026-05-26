# OPA Policy MCP: Modular Control Protocol for Policy Generation & Testing

This project provides a generic, extensible MCP (Modular Control Protocol) for generating and testing OPA (Open Policy Agent) policies, with a focus on robust input schema validation and agent-driven automation. It is designed to be both a standalone policy generation/test harness and a backend for agent-based systems (e.g., dspy agents) that require strict input schemas for domain-specific use cases.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [MCP: Generic Policy Generation & Testing](#mcp-generic-policy-generation--testing)
	- [Features](#features)
	- [MCP API & Tools](#mcp-api--tools)
	- [Policy Authoring Guidelines](#policy-authoring-guidelines)
	- [Testing & Debugging](#testing--debugging)
3. [Agent Integration: dspy Agent with Constrained Input Schema](#agent-integration-dspy-agent-with-constrained-input-schema)
	- [Agent Input Schema](#agent-input-schema)
	- [How the Agent Uses MCP](#how-the-agent-uses-mcp)
	- [Example: HTTP Policy](#example-http-policy)
4. [Development & Usage](#development--usage)
5. [License](#license)

---

## Project Overview

OPA Policy MCP is a framework for:
- Authoring OPA (Rego) policies with best practices and robust testing.
- Enforcing user-specified input schemas for policy generation and validation.
- Supporting agent-driven workflows (e.g., LLM agents) that require strict schema adherence.

It is split into two main parts:
- **MCP Core**: Generic, schema-driven policy generation and test harness.
- **Agent Layer**: Example dspy agent that interacts with MCP using a specific, constrained input schema.

---

## MCP: Generic Policy Generation & Testing

### Features
- **Skill Context**: Reads authoring guidelines and requirements from `policy_skill.md`.
- **Strict Input Schema**: Requires user-specified input schema for all policy/test generation. No guessing or auto-generation.
- **Policy Testing**: Uses OPA CLI to test policies with user-provided mock inputs.
- **Policy Harnessing**: Saves final, validated policies with explanations for future reference.

### MCP API & Tools
- `get_skill_context()`: Returns authoring guidelines for policy generation.
- `verify_input_schema(input_schema: dict)`: Ensures input schema is user-specified, not auto-generated.
- `test_rego(policy: str, package_name: str, mock_input: list[dict], test_value: str, retry_count: int)`: Tests a policy using OPA CLI and user-provided mock inputs. Requires explicit input schema.
- `harness_skill`: Saves the final policy and documentation.

### Policy Authoring Guidelines
- See `policy_skill.md` for best practices (e.g., rule chaining, input validation, OPA syntax, debugging tips).
- Policies must declare a package, use explicit allow/deny logic, and handle all input cases.
- All test inputs must match the user-specified schema.

### Testing & Debugging
- Policies are tested with multiple user-provided mock inputs.
- Debugging is supported by customizing the `test_value` and retrying with different scenarios.
- Policies and test results are saved in `generated_policies/`.

---

## Agent Integration: dspy Agent with Constrained Input Schema

### Agent Input Schema
The dspy agent defines a strict input schema using Pydantic, e.g.:

```python
class PolicyInputSchema(pydantic.BaseModel):
	method: str
	url: str
	host: str
	user_agent: str
```

This schema is used for all policy generation and testing. The agent will not proceed without an explicit, user-specified schema.

### How the Agent Uses MCP
- The agent sends the user query and the input schema to MCP.
- MCP verifies the schema and generates a policy according to the guidelines.
- The agent uses MCP's test tools to validate the policy with mock inputs matching the schema.
- The agent does **not** generate schemas on the fly; it enforces user specification for correctness and reproducibility.

### Example: HTTP Policy
- See `generated_policies/httppolicy.rego` for an example policy.
- Example input (see `generated_policies/httppolicy_input_0.json`):
  ```json
  {"method": "POST", "url": "/api/data", "host": "example.com", "user_agent": "test-agent"}
  ```
- The policy will deny POST requests and allow others, as per the schema and user query.

---

## Development & Usage

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   # or use pyproject.toml with poetry/pdm
   ```
2. **Run the MCP server**:
   ```bash
   python server.py
   ```
3. **Agent usage**:
   - See `agent.py` for an example of agent integration.
   - The agent must provide a valid input schema and user query.

---

## License

MIT License. See LICENSE file.

---

## Using rego-mcp Docker Image in VS Code, Codex, and ClaudeCode


You can use the prebuilt Docker image for rego-mcp: `bhuwanpanta/rego-mcp:latest`.

**Note:** rego-mcp runs in stdio mode (not HTTP). It should be configured as an MCP that communicates over standard input/output, not via a network port.

### VS Code MCP Integration (mcp.json)


Add the following entry to your `mcp.json` to enable rego-mcp (using the recommended servers format):

```json
{
   "servers": {
      "rego-mcp": {
         "command": "docker",
         "args": [
            "run",
            "-i",
            "--rm",
            "bhuwanpanta/rego-mcp:latest"
         ]
      }
   }
}
```

### Run rego-mcp Manually with Docker

To run rego-mcp locally for testing or development (in stdio mode), use:

```bash
docker run -i --rm bhuwanpanta/rego-mcp:latest
```

This will start the MCP server in stdio mode and automatically clean up the container after it exits. You can connect to it using tools that support stdio MCPs.

### Enable rego-mcp in Codex

To enable rego-mcp in Codex, run:

```bash
codex mcp add rego-mcp -- docker run -i --rm bhuwanpanta/rego-mcp:latest
```

### Enable rego-mcp in ClaudeCode

To enable rego-mcp in ClaudeCode, run:

```bash
claudecode mcp add rego-mcp -- docker run -i --rm bhuwanpanta/rego-mcp:latest
```

This will make rego-mcp available as an MCP backend for policy generation and validation in your preferred environment.
