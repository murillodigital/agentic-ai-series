#!/usr/bin/env python3
"""
demos/module2_demo.py
=====================
Live workshop demonstration for Module 2: Agent Frameworks and Building Blocks.

Demonstrates LangChain/LangGraph agent analyzing repositories to identify
applications, technology stacks, and AWS infrastructure requirements.

USAGE
-----
  # Recommended: mock mode (no real repository needed)
  AGENT_MOCK_REPO=true python demos/module2_demo.py

  # Analyze a real repository
  python demos/module2_demo.py --repo /path/to/repo

  # Run just one section
  AGENT_MOCK_REPO=true python demos/module2_demo.py --section 3

SECTIONS
--------
  1  Framework comparison   — LangChain vs Strands architecture
  2  Repository scan        — File structure analysis
  3  Application detection  — Multi-app/monorepo identification
  4  Dependency analysis    — Stack and AWS service mapping
  5  LangSmith tracing      — Observability and debugging
  6  Full workflow          — Complete analysis pipeline
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ---------------------------------------------------------------------------
# Rich output helpers
# ---------------------------------------------------------------------------

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax
    _c = Console()

    def header(text: str, color: str = "cyan") -> None:
        _c.rule(f"[bold {color}]{text}[/bold {color}]", style=color)

    def concept(text: str) -> None:
        _c.print(f"\n[bold yellow]💡 Module 2 Concept:[/bold yellow] [yellow]{text}[/yellow]")

    def user_says(text: str) -> None:
        _c.print(f"\n[bold green]USER ›[/bold green] [italic]{text}[/italic]")

    def box(title: str, body: str) -> None:
        _c.print(Panel(f"[dim]{body}[/dim]", title=f"[bold]{title}[/bold]", border_style="cyan"))

    def code_block(code: str, language: str = "python") -> None:
        syntax = Syntax(code, language, theme="monokai", line_numbers=False)
        _c.print(syntax)

except ImportError:
    def header(text: str, color: str = "cyan") -> None:  # type: ignore[misc]
        print(f"\n{'═' * 62}\n  {text}\n{'═' * 62}")

    def concept(text: str) -> None:  # type: ignore[misc]
        print(f"\n💡 Concept: {text}")

    def user_says(text: str) -> None:  # type: ignore[misc]
        print(f"\nUSER › {text}")

    def box(title: str, body: str) -> None:  # type: ignore[misc]
        print(f"\n[ {title} ]\n{body}")

    def code_block(code: str, language: str = "python") -> None:  # type: ignore[misc]
        print(f"\n{code}\n")


def pause(msg: str = "  ↵  Press Enter to continue...") -> None:
    try:
        input(msg)
    except KeyboardInterrupt:
        sys.exit(0)


# ---------------------------------------------------------------------------
# Section 1 — Framework Comparison
# ---------------------------------------------------------------------------

def section_1_framework_comparison() -> None:
    header("SECTION 1 — LangChain vs AWS Strands", "cyan")
    box(
        "Framework Architecture Comparison",
        "Module 1 uses AWS Strands. Module 2 uses LangChain + LangGraph.\n"
        "Both implement the same think-act-observe loop with different approaches.",
    )

    print("\n  MODULE 1 (AWS Strands) — Infrastructure Agent")
    code_block("""
from strands import Agent
from strands.models import BedrockModel

model = BedrockModel(model_id="claude-sonnet-4", region="us-east-1")
agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=ALL_TOOLS,
    conversation_manager=SlidingWindowConversationManager(),
)
response = agent("List ECS services in us-east-1")
    """)

    print("\n  MODULE 2 (LangChain) — Repository Analysis Agent")
    code_block("""
from langchain_aws import ChatBedrock
from langchain.agents import create_tool_calling_agent, AgentExecutor

model = ChatBedrock(model_id="claude-sonnet-4", region_name="us-east-1")
agent = create_tool_calling_agent(model, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)
response = executor.invoke({"input": "Analyze repository at /path"})
    """)

    concept(
        "Both frameworks use the same Amazon Bedrock model and implement the same "
        "think-act-observe loop. The difference is in the orchestration layer: "
        "Strands provides a simpler API, while LangChain offers more flexibility "
        "and integration with the broader LangChain ecosystem (LangGraph, LangSmith)."
    )
    pause()


# ---------------------------------------------------------------------------
# Section 2 — Repository Scan
# ---------------------------------------------------------------------------

def section_2_repository_scan(agent) -> None:
    header("SECTION 2 — Repository Structure Scan", "green")
    box(
        "First step: Understanding the repository layout",
        "The agent uses scan_repository_structure to get an overview of files, "
        "directories, dependency files, and configuration files.",
    )

    concept(
        "Unlike Module 1 which queries AWS APIs, Module 2 analyzes local git repositories. "
        "The scan tool identifies dependency files (package.json, requirements.txt) "
        "and config files (Dockerfile, terraform files) to understand the stack."
    )

    q = "Scan the repository structure and tell me what you find."
    user_says(q)
    print()
    response = agent.invoke({"input": q})
    print(f"\n  AGENT › {response['output']}\n")
    pause()


# ---------------------------------------------------------------------------
# Section 3 — Application Detection
# ---------------------------------------------------------------------------

def section_3_application_detection(agent) -> None:
    header("SECTION 3 — Multi-Application Detection", "blue")
    box(
        "Identifying distinct applications in a monorepo",
        "The agent detects separate applications by finding dependency files "
        "in different directories. This is crucial for monorepo analysis.",
    )

    concept(
        "Modern repositories often contain multiple services (microservices architecture). "
        "The agent identifies each service by its dependency file and Dockerfile, "
        "enabling separate stack analysis for each application."
    )

    q = "Detect all applications in this repository. How many are there?"
    user_says(q)
    print()
    response = agent.invoke({"input": q})
    print(f"\n  AGENT › {response['output']}\n")
    pause()


# ---------------------------------------------------------------------------
# Section 4 — Dependency Analysis and AWS Mapping
# ---------------------------------------------------------------------------

def section_4_dependency_analysis(agent) -> None:
    header("SECTION 4 — Stack Analysis & AWS Service Mapping", "yellow")
    box(
        "From dependencies to AWS infrastructure requirements",
        "The agent reads dependency files, identifies libraries, and maps them "
        "to required AWS services (RDS, ElastiCache, S3, etc.).",
    )

    concept(
        "This is where repository analysis becomes infrastructure planning. "
        "The agent knows that 'pg' → RDS PostgreSQL, 'redis' → ElastiCache, "
        "'boto3' → S3/AWS SDK. It builds a complete infrastructure requirements list."
    )

    q = """For each application you detected:
1. Analyze its dependencies
2. Identify the technology stack (language, framework)
3. Map dependencies to AWS infrastructure services
4. Tell me what AWS services each application needs"""

    user_says(q)
    print()
    response = agent.invoke({"input": q})
    print(f"\n  AGENT › {response['output']}\n")
    pause()


# ---------------------------------------------------------------------------
# Section 5 — LangSmith Tracing
# ---------------------------------------------------------------------------

def section_5_langsmith_tracing() -> None:
    header("SECTION 5 — LangSmith Tracing & Observability", "magenta")
    box(
        "Observability: Understanding agent behavior",
        "LangSmith provides detailed traces of every agent run, showing each "
        "think step, tool call, and model response with timing data.",
    )

    print("""
  LangSmith Integration (when configured):
  
  1. Set environment variables:
     export LANGCHAIN_TRACING_V2=true
     export LANGCHAIN_API_KEY=<your-key>
     export LANGCHAIN_PROJECT=repo-analysis-agent
  
  2. Run the agent — traces automatically appear in LangSmith
  
  3. View in LangSmith dashboard:
     - Every model call with input/output
     - Every tool call with parameters and results
     - Token counts and latency for each step
     - Full conversation history
  
  4. Debug failed runs:
     - See exactly where the agent went wrong
     - Inspect the context window at each step
     - Identify tool errors or model confusion
  
  LangSmith is the Module 2 equivalent of Module 1's LoopObserver callback,
  but with persistent storage, search, and comparison across runs.
""")

    concept(
        "Observability is critical for agent development. Module 1 uses callback handlers "
        "to print loop steps. Module 2 uses LangSmith for persistent tracing, evaluation, "
        "and debugging. Both serve the same purpose: making agent behavior transparent."
    )
    pause()


# ---------------------------------------------------------------------------
# Section 6 — Full Analysis Workflow
# ---------------------------------------------------------------------------

def section_6_full_workflow(agent) -> None:
    header("SECTION 6 — Complete Analysis Pipeline", "red")
    box(
        "End-to-end repository analysis",
        "The agent executes the full workflow: scan → detect → analyze → map → synthesize",
    )

    concept(
        "This demonstrates the complete Module 2 capability: analyzing a repository "
        "and producing a structured report with all applications, their stacks, and "
        "AWS infrastructure requirements. This output can be consumed by Module 1 "
        "(the AWS Infrastructure Agent) to check existing resources and identify gaps."
    )

    q = """Perform a complete analysis of this repository:

1. Scan the repository structure
2. Detect all applications/services
3. For each application:
   - Analyze its technology stack
   - Identify dependencies
   - Map to AWS infrastructure requirements
4. Produce a comprehensive report with:
   - Repository overview
   - Application details (stack, dependencies, AWS needs)
   - Infrastructure summary (all AWS services needed)
   - Deployment recommendations

Format the final report as structured JSON."""

    user_says(q)
    print()
    response = agent.invoke({"input": q})
    print(f"\n  AGENT › {response['output']}\n")
    
    concept(
        "The agent decomposed this complex request into multiple tool calls, "
        "analyzed the repository systematically, and synthesized findings into "
        "a comprehensive report. This is the multi-step reasoning capability "
        "that makes agents powerful for complex analysis tasks."
    )
    pause()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Module 2 Workshop Demo")
    parser.add_argument("--section", "-s", type=int, choices=range(1, 7), metavar="1-6")
    parser.add_argument("--repo", type=str, help="Path to real repository to analyze")
    args = parser.parse_args()

    # Set mock mode if no real repo provided
    if not args.repo:
        os.environ["AGENT_MOCK_REPO"] = "true"
        print("  Mock mode ON  (pass --repo /path to analyze a real repository)\n")

    from module2.agent import create_agent

    agent = create_agent(verbose=True, max_iterations=15)

    header("REPOSITORY ANALYSIS AGENT — MODULE 2 DEMO", "bold cyan")
    print("""
  Use case: DevOps Engineer analyzing a software repository to understand
  what applications exist, what technology stacks they use, and what AWS
  infrastructure services they require.

  Module 2 scope: REPOSITORY ANALYSIS
  - Scan git repository structure
  - Detect applications/services
  - Analyze technology stacks
  - Map dependencies to AWS services
  
  Framework: LangChain + LangGraph (vs Module 1's AWS Strands)
""")
    pause("  ↵  Press Enter to begin...")

    sections = {
        1: section_1_framework_comparison,
        2: lambda: section_2_repository_scan(agent),
        3: lambda: section_3_application_detection(agent),
        4: lambda: section_4_dependency_analysis(agent),
        5: section_5_langsmith_tracing,
        6: lambda: section_6_full_workflow(agent),
    }

    if args.section:
        sections[args.section]()
    else:
        for fn in sections.values():
            fn()

    header("DEMO COMPLETE", "bold green")
    print("""
  ✅ You've seen:
     • LangChain vs AWS Strands framework comparison
     • Repository structure scanning with git awareness
     • Multi-application detection in monorepos
     • Dependency analysis and AWS service mapping
     • LangSmith tracing for observability
     • Complete analysis workflow with structured output

  🔜 Next: Module 3 — Evaluation and Routing Patterns
  
  💡 Multi-Agent Future:
     Module 2 Agent (repo analysis) + Module 1 Agent (AWS infrastructure)
     = Complete DevOps automation pipeline
""")


if __name__ == "__main__":
    main()
