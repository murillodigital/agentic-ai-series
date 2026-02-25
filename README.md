# AWS Infrastructure Agent — Module 1: Introduction to AI Agents

Hands-on demonstration code for the *Module 1: Introduction to AI Agents* workshop session.

**Use case:** An AWS Infrastructure Engineer is building an agentic system that can provision infrastructure, deploy and build microservices, and observe those services running in AWS.

This module builds the **skeleton** — a working agent that observes and analyses. Later modules add provisioning, deployment, multi-agent patterns, long-term memory, and full autonomy.

---

## What This Demonstrates

Every concept from the Module 1 slides is visible in the running code:

| Slide Concept | Where It Lives |
|---|---|
| Three Layers (Reasoning / Orchestration / Tools) | `agent.py` → `create_agent()` |
| Think → Act → Observe loop | `LoopObserver` callback handler in `agent.py` |
| Context window / short-term memory | `SlidingWindowConversationManager(window_size=10)` |
| Tools as external system interfaces | `tools/aws_tools.py` — 5 `@tool` functions |
| Human-in-the-loop pattern | `request_human_review` tool |
| Model-agnostic architecture | `config/models.py` — one-line model swap |
| AgentCore deployment | `app.py` — `BedrockAgentCoreApp` wrapper |

---

## Project Structure

```
infra-agent/
├── agent.py              # Core agent: all three layers assembled
├── app.py                # AgentCore Runtime entrypoint (deploy here)
├── requirements.txt
│
├── config/
│   └── models.py         # Anthropic + Hugging Face model configs
│
├── tools/
│   └── aws_tools.py      # 5 read-only AWS tools (@tool decorated)
│
├── demos/
│   └── module1_demo.py   # Live workshop demo script (6 sections)
│
├── scripts/
│   └── invoke_agentcore.py  # Invoke deployed agent via boto3
│
└── tests/
    └── test_tools.py     # 27 unit tests (mock mode, no credentials)
```

---

## Quick Start (No AWS Account Needed)

```bash
# 1. Create virtual environment
python -m venv .venv && source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the full demo in mock mode
AGENT_MOCK_AWS=true python demos/module1_demo.py

# 4. Run just one section (1–6)
AGENT_MOCK_AWS=true python demos/module1_demo.py --section 4

# 5. Run tests
AGENT_MOCK_AWS=true pytest tests/ -v
```

---

## Live AWS Mode

### Prerequisites

**Anthropic (Claude Sonnet 4 via Amazon Bedrock)**

1. AWS account with credentials configured (`aws configure` or `AWS_*` env vars)
2. Enable model access: *AWS Console → Amazon Bedrock → Model Access → Enable Anthropic models*
3. No subscription needed — pay per token

```bash
# Run against real AWS
python demos/module1_demo.py --live
```

**Hugging Face (via Amazon Bedrock Marketplace)**

1. *AWS Console → Amazon Bedrock → Model Catalog → Filter by "Hugging Face"*
2. Select a model (e.g. **Mistral-7B-Instruct** — public model, no subscription fee)
3. Click **Deploy** → select instance → wait for *"In service"*
4. Copy the SageMaker endpoint ARN from the deployment details page
5. Set: `export HF_ENDPOINT_ARN="arn:aws:sagemaker:..."`

```bash
# Run with Hugging Face model (same agent, different reasoning engine)
python demos/module1_demo.py --live --hf
```

> Guide: https://huggingface.co/blog/bedrock-marketplace

---

## Deploying to AgentCore Runtime

```bash
# 1. Install the CLI
pip install bedrock-agentcore-starter-toolkit

# 2. Configure (run once — prompts for settings)
agentcore configure --entrypoint app.py --disable-memory

# 3. Test locally (no Docker needed)
AGENT_MOCK_AWS=true python app.py
# → Serves on http://localhost:8080/invocations

# 4. Test the local server
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Give me a health summary of us-east-1"}'

# 5. Deploy to AWS (CodeBuild, no Docker needed)
agentcore launch

# 6. Invoke the deployed agent
agentcore invoke '{"prompt": "List ECS services in us-east-1"}'

# 7. Invoke via boto3 (for automation / integration)
export AGENTCORE_ARN="arn:aws:bedrock-agentcore:..."
python scripts/invoke_agentcore.py --prompt "Health check us-east-1"
python scripts/invoke_agentcore.py --repl   # interactive mode
```

---

## Tools Reference

All Module 1 tools are **read-only**. The only action path is `request_human_review`.

| Tool | Purpose | Slide Concept |
|---|---|---|
| `list_aws_resources(service_type, region)` | ECS / EC2 / RDS / Lambda listings | Grounding: agent sees current state |
| `describe_resource(service_type, name, region)` | Detailed drill-down | Multi-step reasoning |
| `check_resource_health(service_type, name, region)` | Structured health verdict | Observation |
| `get_environment_summary(region)` | Cross-service overview | Data synthesis |
| `request_human_review(...)` | Escalation ticket | Human-in-the-loop |

### Mock data

With `AGENT_MOCK_AWS=true` the tools return realistic simulated data including:
- **`api-gateway-svc`** → healthy (3/3 tasks running)
- **`notification-svc`** → degraded (1/2 tasks, EssentialContainerExited event) ← triggers HITL
- **`reporting-mysql`** → degraded (Single-AZ RDS, no failover)
- **`prod-postgres-01`** → healthy (Multi-AZ, available)

---

## The Model-Agnostic Property

The most important architectural property to highlight in the workshop:

```python
# config/models.py

# Anthropic — Claude Sonnet 4 via Amazon Bedrock
model = get_bedrock_model()

# Hugging Face — open model via Bedrock Marketplace (ONE LINE change)
model = get_hf_bedrock_model(endpoint_arn="arn:aws:sagemaker:...")
```

The `create_agent()` factory in `agent.py` accepts `hf_endpoint_arn` and swaps the model. **Tools, system prompt, conversation manager, and AgentCore wrapper are completely unchanged.**

---

## What's Scoped Out (Future Modules)

| Capability | Module |
|---|---|
| Write operations (provision, deploy, scale) | Module 3 |
| Multi-agent supervisor pattern | Module 4 |
| Long-term memory (DynamoDB / vector store) | Module 7 |
| RAG / Knowledge Base | Module 10 |
| Production IAM hardening | Module 8 |
| CloudWatch / X-Ray tracing | Module 12 |

---

## Demo Sections

Run `AGENT_MOCK_AWS=true python demos/module1_demo.py --section N`:

| # | Title | Key Concept |
|---|---|---|
| 1 | Architecture anatomy | Three layers in code |
| 2 | The loop | Think → Act → Observe, live |
| 3 | Multi-step reasoning | Compound query, multiple tool calls |
| 4 | Human-in-the-loop | Agent escalates, doesn't act |
| 5 | Model swap | Anthropic ↔ Hugging Face |
| 6 | Context window | Multi-turn short-term memory |
