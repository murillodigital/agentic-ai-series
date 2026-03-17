# Getting Started with the AI Agent Learning Series

This guide helps you get started with both Module 1 and Module 2 agents.

## Prerequisites

- Python 3.11 or later
- AWS account (for live mode) or use mock mode for demos
- Git installed

## Installation

```bash
# Clone the repository
cd /home/ubuntu/workspace/amazon/infra-agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Module 1: AWS Infrastructure Agent

### Quick Demo (Mock Mode)

```bash
# Run the complete demo
AGENT_MOCK_AWS=true python demos/module1_demo.py

# Run specific sections
AGENT_MOCK_AWS=true python demos/module1_demo.py --section 1  # Architecture
AGENT_MOCK_AWS=true python demos/module1_demo.py --section 2  # The loop
AGENT_MOCK_AWS=true python demos/module1_demo.py --section 4  # Human-in-the-loop
```

### Live AWS Mode

```bash
# Configure AWS credentials
aws configure

# Enable Bedrock model access in AWS Console:
# Amazon Bedrock → Model Access → Enable Anthropic models

# Run against real AWS
python demos/module1_demo.py --live
```

### Run Tests

```bash
AGENT_MOCK_AWS=true pytest tests/test_tools.py -v
```

## Module 2: Repository Analysis Agent

### Quick Demo (Mock Mode)

```bash
# Run the complete demo
AGENT_MOCK_REPO=true python demos/module2_demo.py

# Run specific sections
AGENT_MOCK_REPO=true python demos/module2_demo.py --section 1  # Framework comparison
AGENT_MOCK_REPO=true python demos/module2_demo.py --section 3  # App detection
AGENT_MOCK_REPO=true python demos/module2_demo.py --section 6  # Full workflow
```

### Analyze a Real Repository

```bash
# Analyze any git repository
python demos/module2_demo.py --repo /path/to/your/repo
```

### Run Tests

```bash
AGENT_MOCK_REPO=true pytest tests/test_repo_tools.py -v
```

### Start HTTP Server

```bash
# Start the server (port 8081)
python module2/app.py

# In another terminal, test it
curl -X POST http://localhost:8081/analyze \
  -H "Content-Type: application/json" \
  -d '{"repo_path": "/path/to/repo"}'
```

## Using Both Agents Together (Python API)

```python
# Module 1: Check AWS infrastructure
from module1.agent import create_agent as create_infra_agent

infra_agent = create_infra_agent(verbose=True)
aws_status = infra_agent("Give me a health summary of us-east-1")
print(aws_status)

# Module 2: Analyze repository
from module2.agent import analyze_repository

repo_analysis = analyze_repository("/path/to/repo", verbose=True)
print(repo_analysis["analysis"])

# Future: Orchestrator will coordinate both agents
```

## LangSmith Tracing (Module 2)

Enable detailed tracing for Module 2:

```bash
# Set environment variables
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=your-langsmith-api-key
export LANGCHAIN_PROJECT=repo-analysis-agent

# Run demo - traces appear in LangSmith dashboard
python demos/module2_demo.py
```

View traces at: https://smith.langchain.com/

## Common Issues

### Import Errors

If you see import errors, ensure you're in the virtual environment and have installed dependencies:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### AWS Credentials Not Found (Module 1)

Use mock mode for demos:
```bash
AGENT_MOCK_AWS=true python demos/module1_demo.py
```

Or configure AWS credentials:
```bash
aws configure
```

### Repository Not Found (Module 2)

Use mock mode for demos:
```bash
AGENT_MOCK_REPO=true python demos/module2_demo.py
```

Or provide a valid git repository path:
```bash
python demos/module2_demo.py --repo /path/to/valid/git/repo
```

## Next Steps

1. **Run both demos** to see the agents in action
2. **Read the module READMEs** for detailed documentation
3. **Explore the code** to understand the implementation
4. **Try with real data** (AWS account or git repositories)
5. **Wait for Module 3** for evaluation and routing patterns
6. **Wait for Module 4** for multi-agent orchestration

## Learning Path

1. **Module 1 Demo** → Understand agent fundamentals (Strands framework)
2. **Module 2 Demo** → Learn LangChain/LangGraph approach
3. **Compare frameworks** → See different ways to build the same patterns
4. **Run tests** → Understand tool implementation
5. **Modify agents** → Experiment with your own use cases

## Resources

- [Module 1 README](module1/README.md)
- [Module 2 README](module2/README.md)
- [AWS Strands Documentation](https://github.com/awslabs/strands)
- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Amazon Bedrock](https://aws.amazon.com/bedrock/)
